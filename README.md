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
             {download,upload,list,user,infos,connect,disconnect} ...

Dropbox command line tool.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -r, --reset           reload cached token

commands:
  {download,upload,list,user,infos,connect,disconnect}
    download            Download a file from Dropbox
    upload              Upload a file on Dropbox
    list                list a remote folder content
    user                get user info
    infos               get info on Dropbox entry
    connect             connect to Dropbox
    disconnect          disconnect from Dropbox
```

### Download file

```
usage: dpbox download [-h] [-d DEST] file

positional arguments:
  file                  the file to download

optional arguments:
  -h, --help            show this help message and exit
  -d DEST, --dest DEST  the download destination (current directory is default
```

### Upload file

```
usage: dpbox upload [-h] file dest

positional arguments:
  file        the file to upload
  dest        the upload destination

optional arguments:
  -h, --help  show this help message and exit
```

### List folder content

```
usage: dpbox list [-h] dir

positional arguments:
  dir         the path to directory to list

optional arguments:
  -h, --help  show this help message and exit
```

License
-------

[GNU GPLv2]('LICENSE')

Change log
----------

### 1.0

Initial version

### 1.1

* Changed options with positional arguments
* Can now download folders
* Renamed `infos` command to `user`
* New `infos` command display raw given entry's metadata