dpbox
=====

Simple command line tool to interact Dropbox API.

Configuration file
------------------

You need to create a `config.py` file in the root directory of the script.
This file must look like the following example:

```python
dpbox = dict(
    version = '1.0',
    cachefile = '~/.dpbox',
    app = dict(
        key = 'your_api_key',
        secret = 'your_api_secret',
        access = 'dropbox',
        encoded = 'base64_encoded_key'
    ),
    logger = dict(
        name = 'bpbox',
        file = '-' # './dpbox.log'
    )
)
```

Get your encoded Dropbox app key at https://dl-web.dropbox.com/spa/pjlfdak1tmznswp/api_keys.js/public/index.html

Usage
-----

```
usage: dpbox [-h] [-v] [-r]
             {download,upload,list,infos,connect,disconnect} ...

Dropbox command line tool.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -r, --reset           reload cached token

commands:
  {download,upload,list,infos,connect,disconnect}
    download            Download a file from Dropbox
    upload              Upload a file on Dropbox
    list                list a remote folder content
    infos               get info on user
    connect             connect to Dropbox
    disconnect          disconnect from Dropbox
```

### Download file

```
usage: dpbox download [-h] -f FILE [-d DEST]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  the file to download
  -d DEST, --dest DEST  the download destination
```

### Upload file

```
usage: dpbox upload [-h] -f FILE [-d DEST]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  the file to upload
  -d DEST, --dest DEST  the upload destination
```

### List folder content

```
usage: dpbox list [-h] [-d DIR]

optional arguments:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  the path to directory to list
```

License
-------

[GNU GPLv2]('LICENSE')

Change log
----------

1.0 Initial version
