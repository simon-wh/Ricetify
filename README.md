# Ricetify

A CLI and x-plat (kinda) interface for modifying spotify. Compatible with [spicetify](https://github.com/khanhas/Spicetify).

## Usage

```bash
$ python ricetify.py -h
usage: ricetify.py [-h] [-u USER_CSS] [-o OUTPUT] [-v {0,1,2,3}] [-c CONFIG]
                   [-e EXTENSIONS [EXTENSIONS ...]] [-a APPS [APPS ...]] [-r]

Rice spotify

optional arguments:
  -h, --help            show this help message and exit
  -u USER_CSS, --user-css USER_CSS
                        Apply custom CSS
  -o OUTPUT, --output OUTPUT
                        Output folder
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Increase output verbosity
  -c CONFIG, --config CONFIG
                        Load a config file
  -e EXTENSIONS [EXTENSIONS ...], --extensions EXTENSIONS [EXTENSIONS ...]
                        A list of extensions to inject
  -a APPS [APPS ...], --apps APPS [APPS ...]
                        A list of apps to inject
  -r, --restore         Restore spotify to default

```

## Examples

Update spotify to use custom CSS:

```bash
$ sudo python ricetify.py -u user.css -o /usr/share/spotify/Apps
```

Update spotify with custom CSS, extensions and a config file

```bash
$ sudo python ricetify.py -u user.css -c ricetify.conf -e autoSkipExplicit.js -o /usr/share/spotify/Apps
```

## Credit

Based on [**khanhas**](https://github.com/khanhas)' rainmeter skin [**Spicetify**](https://github.com/khanhas/Spicetify).