#!/usr/bin/env python

##
## https://www.dropbox.com/developers/core/start/python
##

import os, sys, argparse
import locale, logging, json, types
import config
from base64 import b64decode
# Include the Dropbox SDK
from dropbox.session import DropboxSession
from dropbox.client import DropboxClient

# Initialize version from a number given in setup.py.
try:
    import pkg_resources  # Part of setuptools.
except ImportError:  # Standalone script?
    pass
else:
    try:
        VERSION = pkg_resources.require('dpbox')[0].version
    except pkg_resources.DistributionNotFound:  # standalone script?
        VERSION = config.dpbox['version']
        pass
    
def decode_dropbox_key(key):
    key, secret = key.split('|')
    key = b64decode(key)
    key = [ord(x) for x in key]
    secret = b64decode(secret)

    s = range(256)
    y = 0
    for x in xrange(256):
        y = (y + s[len(key)] + key[x % len(key)]) % 256
        s[x], s[y] = s[y], s[x]

    x = y = 0
    result = []
    for z in range(len(secret)):
        x = (x + 1) % 256
        y = (y + s[x]) % 256
        s[x], s[y] = s[y], s[x]
        k = s[(s[x] + s[y]) % 256]
        result.append(chr((k ^ ord(secret[z])) % 256))

    # key = ''.join([chr(a) for a in key])
    # return '|'.join([b64encode(key), b64encode(''.join(result))])
    return ''.join(result).split('?', 2)
    
class DBoxClient(object):
    def __init__(self):
        self._logger = logging.getLogger(config.dpbox['logger']['name'])
        self.cache_file = config.dpbox['cachefile']
        self._token = None

        self._load()
        
        key, secret = decode_dropbox_key(config.dpbox['app']['encoded'])
        
        self.session = DBoxSession(config.dpbox['app']['key'], config.dpbox['app']['secret'], access_type=config.dpbox['app']['access'])
        
        if(self._token):
            self.session.set_token(self._token[0], self._token[1])
        else:
            self._token = self.session.link()
            self._save()
            
        self.client = DropboxClient(self.session)
        
    def reset(self):
        self._logger.debug('[dpbox v%s] resetting local state' % (VERSION))
        self._save()
        
    def download(self, source, directory=''):
        
        if len(directory) > 0 and directory[len(directory)-1] != '/':
            directory += '/'
           
        self._logger.info(u'[dpbox v%s] FETCH %s -> %s' % (VERSION, unicode(source), unicode(directory)))
        self._download(source, directory)

        
    def _download(self, source, directory):
        try:
            metadata = self.client.metadata(source)
            self._logger.debug(u'metadata for %s' % source)
            self._logger.debug(metadata)
        except Exception as e:
            self._logger.error('[dpbox v%s] error fetching file' % (VERSION))
            self._logger.exception(e)
            return # Will check later if we've got everything.
            
        segs = metadata['path'].split('/')
        directory += segs[len(segs)-1]

        if metadata['is_dir']:
            try:
                os.stat(directory)
            except:
                os.mkdir(directory)

            for item in metadata['contents']:
                self._download(item['path'], directory + '/')
        else:
            f = self.client.get_file(source)
            print 'writing file to disc...'
            destination = open(os.path.expanduser(directory.encode('utf-8')), 'wb')
            destination.write(f.read())
            destination.close()
            print u"[rev %s] %s - '%s' downloaded" % (metadata['revision'], metadata['size'], directory)

    def upload(self, source, directory):
        
        if len(directory) > 0 and directory[len(directory)-1] != '/':
            directory += '/'
            
        segs = source.split('/')
        directory += segs[len(segs)-1]
        
        f = open(source, 'rb')
        print u'uploading file %s -> %s' % (source, directory)
        response = self.client.put_file(directory.encode('utf-8'), f)
        print "[rev %s] %s - '%s' uploaded" % (response['revision'], response['size'], response['path'])
        
        self._logger.debug('[dpbox v%s] upload response: %s' % (VERSION, response))
        
    def list(self, directory):
        path = unicode(directory).encode('utf-8')
        metadata = self.client.metadata(path)
        self._logger.debug('[dpbox v%s] metadata: %s' % (VERSION, metadata))
        
        print 'display content of ', metadata['path'],  ', ', metadata['size']
        
        for item in metadata['contents']:
            if item['is_dir']:
                print 'd ', item['path']
            else:
                print 'f ', item['path']
        
    def infos(self, item):
        path = unicode(item).encode('utf-8')
        metadata = self.client.metadata(path)
        print metadata

    def user(self, item=''):
        infos = self.client.account_info()
        
        self._logger.debug(u'[dpbox v%s] %s' % (VERSION, infos))
        if len(item) > 0:
            print item, ' = ', infos[item]
            return
            
        for name in infos:
            space = ' '*(20-len(name))
            if isinstance(infos[name], types.DictType):
                print name, ':'
                for key in infos[name]:
                    print '  -> ', key, ': ', infos[name][key]
            else:
                print name, space, infos[name]

    def disconnect(self):
        cachefile = os.path.expanduser(self.cache_file)
        if os.path.exists(cachefile):
            os.unlink(cachefile)
        self.session.unlink()
        print 'disconnected from service'

    def _save(self):
        with open(os.path.expanduser(self.cache_file), 'w') as f:
            f.write(''.join([json.dumps(self._token), '\n']))
            # f.write(''.join([json.dumps(self.remote_dir), '\n']))
            
    def _load(self):
        cachefile = os.path.expanduser(self.cache_file)

        if not os.path.exists(cachefile):
            self._logger.warn('[dpbox v%s] Cache file not found: %s' % (VERSION, cachefile))
            self.reset()
            return

        try:
            with open(cachefile, 'r') as f:
                dir_changed = False
                try:
                    line = f.readline()  # Token.
                    self._token = json.loads(line)
                    self._logger.debug('[dpbox v%s] loaded token' % (VERSION))
                except Exception as e:
                    self._logger.warn('[dpbox v%s] can\'t load cache state' % (VERSION))
                    self._logger.exception(e)

                # try:
                #     line = f.readline()  # Dropbox directory.
                #     directory = json.loads(line)
                #     if directory != self.remote_dir:  # Don't use state.
                #         self._logger.info(u'remote dir changed "%s" -> "%s"' %
                #                           (directory, self.remote_dir))
                #         dir_changed = True
                # except Exception as e:
                #     self._logger.warn('can\'t load cache state')
                #     self._logger.exception(e)
                    
                if dir_changed:
                    return

        except Exception as e:
            self._logger.error('[dpbox v%s] error opening cache file' % (VERSION))
            self._logger.exception(e)

class DBoxSession(DropboxSession):
    def link(self):
        request_token = self.obtain_request_token()
        
        url = self.build_authorize_url(request_token)
        print 'URL: ', url
        print 'Please authorize this URL in the browser and then press enter'
        raw_input()
        
        self.obtain_access_token(request_token)
        self.set_token(self.token.key, self.token.secret)
        return [self.token.key, self.token.secret]

    def unlink(self):
        DropboxSession.unlink(self)

def create_logger(log, verbose):
    FORMAT = '%(asctime)-15s %(message)s'.format(VERSION)
    console = log.strip() == '-'
    
    if console:
        logging.basicConfig(format=FORMAT)
        
    logger = logging.getLogger(config.dpbox['logger']['name'])
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        
    if not console:
        fh = logging.FileHandler(log)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FORMAT)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger
    
def main(argv):

    parser = argparse.ArgumentParser(description='Dropbox command line tool.')
    subparsers = parser.add_subparsers(title="commands", dest="subparser_name")
    
    parser_dl = subparsers.add_parser('download', help='Download a file from Dropbox')
    parser_dl.add_argument("file", help="the file to download")
    parser_dl.add_argument("-d", "--dest", default='',
                            help="the download destination (current directory is default")
    
    parser_ul = subparsers.add_parser('upload', help='Upload a file on Dropbox')
    parser_ul.add_argument("file", help="the file to upload")
    parser_ul.add_argument("dest", help="the upload destination")
    

    parser_li = subparsers.add_parser("list", help="list a remote folder content")
    parser_li.add_argument("dir", help="the path to directory to list")
    
    parser_u = subparsers.add_parser("user", help="get user info")
    parser_u.add_argument('-n', "--name", default='',
                         help="get a specific info")
    
    parser_i = subparsers.add_parser("infos", help="get info on Dropbox entry")
    parser_i.add_argument('-n', "--name", default='',
                         help="get a specific info")
    
    subparsers.add_parser("connect", help="connect to Dropbox")
    subparsers.add_parser("disconnect", help="disconnect from Dropbox")
                        
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
                        
    parser.add_argument("-r", "--reset", action="store_true",
                        help="reload cached token")
    
    args = parser.parse_args()
    
    locale.setlocale(locale.LC_ALL, 'C')  # To parse time correctly.
    
    logger = create_logger(config.dpbox['logger']['file'], args.verbose)
    logger.debug(u'[dpbox v%s] %s %s' % (VERSION, args.subparser_name, args))
        
    client = DBoxClient()
    
    if(args.reset):
        client.reset()
    
    if args.subparser_name == "connect":
        client.infos()
    if args.subparser_name == "user":
        client.user(args.name)
    if args.subparser_name == "infos":
        client.infos(args.name)
    elif args.subparser_name == "disconnect":
        client.disconnect()
    elif args.subparser_name == "download":
        client.download(args.file, args.dest)
    elif args.subparser_name == "upload":
        client.upload(args.file, args.dest)
    elif args.subparser_name == "list":
        client.list(args.dir)

    sys.exit()
    
if __name__ == "__main__":
    main(sys.argv[1:])