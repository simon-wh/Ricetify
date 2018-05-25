import argparse
import configparser
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

OS = sys.platform
if OS == "linux":
    SPOTIFY_PATH = "/usr/share/spotify"
elif OS == "darwin":
    # TODO find where the folder is
    SPOTIFY_PATH = ""
elif OS == "win32":
    SPOTIFY_PATH = os.path.join(os.getenv('APPDATA'), "Spotify")

RICETIFY_FOLDER = os.path.dirname(sys.argv[0])

GLOBAL_VERBOSITY = 0

CONFIG = configparser.ConfigParser()

TEMP_DIR = tempfile.TemporaryDirectory()
TEMP_DIR_PATH = TEMP_DIR.name

default_colors = {
    "main_fg": "#ffffff",
    "secondary_fg": "#c0c0c0",
    "main_bg": "#282828",
    "sidebar_and_player_bg": "#000000",
    "cover_overlay_and_shadow": "#000000",
    "indicator_fg_and_button_bg": "#1db954",
    "pressing_fg": "#cdcdcd",
    "slider_bg": "#404040",
    "sidebar_indicator_and_hover_button_bg": "#1ed660",
    "scrollbar_fg_and_selected_row_bg": "#333333",
    "pressing_button_fg": "#cccccc",
    "pressing_button_bg": "#179443",
    "selected_button": "#18ac4d",
    "miscellaneous_bg": "#4687d6",
    "miscellaneous_hover_bg": "#2e77d0",
    "preserve_1": "#ffffff"
}


def debug_print(string, verbosity):
    if verbosity <= GLOBAL_VERBOSITY:
        print(string)


def hex_to_rgb(hex_code):
    r = int(hex_code[1:3], 16)
    g = int(hex_code[3:5], 16)
    b = int(hex_code[5:], 16)
    return f"{r},{g},{b}"


def get_spotify_version():
    if OS == 'linux':
        ver = subprocess.run(["spotify", "--version"], stdout=subprocess.PIPE)
        return str(ver.stdout.split()[2][:-1])
    elif OS == 'darwin':
        # TODO find out how to do this
        pass
    elif OS == 'win32':
        with open(os.path.join(SPOTIFY_PATH, "prefs")) as prefs:
            return re.match(r"app\.last-launched-version=\"(.*)\"", prefs.read()).group(0)


def convert_css(css_data):
    replacements = [
        ("#1ed660", "var(--modspotify_sidebar_indicator_and_hover_button_bg)"),
        ("#1ed760", "var(--modspotify_sidebar_indicator_and_hover_button_bg)"),
        ("#1db954", "var(--modspotify_indicator_fg_and_button_bg)"),
        ("#1df369", "var(--modspotify_indicator_fg_and_button_bg)"),
        ("#1df269", "var(--modspotify_indicator_fg_and_button_bg)"),
        ("#1cd85e", "var(--modspotify_indicator_fg_and_button_bg)"),
        ("#1bd85e", "var(--modspotify_indicator_fg_and_button_bg)"),
        ("#18ac4d", "var(--modspotify_selected_button)"),
        ("#18ab4d", "var(--modspotify_selected_button)"),
        ("#179443", "var(--modspotify_pressing_button_bg)"),
        ("#14833b", "var(--modspotify_pressing_button_bg)"),
        ("#282828", "var(--modspotify_main_bg)"),
        ("#121212", "var(--modspotify_main_bg)"),
        ("#999999", "var(--modspotify_main_bg)"),
        ("#606060", "var(--modspotify_main_bg)"),
        ("#181818", "var(--modspotify_sidebar_and_player_bg)"),
        ("#000000", "var(--modspotify_sidebar_and_player_bg)"),
        ("#3f3f3f", "var(--modspotify_scrollbar_fg_and_selected_row_bg)"),
        ("#535353", "var(--modspotify_scrollbar_fg_and_selected_row_bg)"),
        ("#333333", "var(--modspotify_scrollbar_fg_and_selected_row_bg)"),
        ("#404040", "var(--modspotify_slider_bg)"),
        ("#000011", "var(--modspotify_sidebar_and_player_bg)"),
        ("#0a1a2d", "var(--modspotify_sidebar_and_player_bg)"),
        ("#ffffff", "var(--modspotify_main_fg)"),
        ("#f8f8f7", "var(--modspotify_pressing_fg)"),
        ("#fcfcfc", "var(--modspotify_pressing_fg)"),
        ("#d9d9d9", "var(--modspotify_pressing_fg)"),
        ("#cdcdcd", "var(--modspotify_pressing_fg)"),
        ("#e6e6e6", "var(--modspotify_pressing_fg)"),
        ("#e5e5e5", "var(--modspotify_pressing_fg)"),
        ("#adafb2", "var(--modspotify_secondary_fg)"),
        ("#c8c8c8", "var(--modspotify_secondary_fg)"),
        ("#a0a0a0", "var(--modspotify_secondary_fg)"),
        ("#bec0bb", "var(--modspotify_secondary_fg)"),
        ("#bababa", "var(--modspotify_secondary_fg)"),
        ("#b3b3b3", "var(--modspotify_secondary_fg)"),
        ("#c0c0c0", "var(--modspotify_secondary_fg)"),
        ("#cccccc", "var(--modspotify_pressing_button_fg)"),
        ("#ededed", "var(--modspotify_pressing_button_fg)"),
        ("#4687d6", "var(--modspotify_miscellaneous_bg)"),
        ("#2e77d0", "var(--modspotify_miscellaneous_hover_bg)"),
        ("#ddd;", "var(--modspotify_pressing_button_fg);"),
        ("#000;", "var(--modspotify_sidebar_and_player_bg);"),
        ("#000 ", "var(--modspotify_sidebar_and_player_bg)"),
        ("#333;", "var(--modspotify_scrollbar_fg_and_selected_row_bg);"),
        ("#333 ", "var(--modspotify_scrollbar_fg_and_selected_row_bg)"),
        ("#444;", "var(--modspotify_slider_bg);"),
        ("#444 ", "var(--modspotify_slider_bg)"),
        ("#fff;", "var(--modspotify_main_fg);"),
        ("#fff ", "var(--modspotify_main_fg)"),
        (" black;", " var(--modspotify_sidebar_and_player_bg);"),
        (" black ", " var(--modspotify_sidebar_and_player_bg)"),
        (" gray ", " var(--modspotify_main_bg)"),
        (" gray;", " var(--modspotify_main_bg);"),
        (" lightgray ", " var(--modspotify_pressing_button_fg)"),
        (" lightgray;", " var(--modspotify_pressing_button_fg);"),
        (" white;", " var(--modspotify_main_fg);"),
        (" white ", " var(--modspotify_main_fg)"),
        ("#fff", "var(--modspotify_main_fg)"),
        ("#000", "var(--modspotify_sidebar_and_player_bg)"),
        (r'rgba\(18, 18, 18, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(18, 19, 20, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(80, 55, 80, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(40, 40, 40, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(40,40,40,([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(24, 24, 24, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(18, 19, 20, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(179, 179, 179, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_secondary_fg),\1)"),
        (r'rgba\(70, 135, 214, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_miscellaneous_bg),\1)"),
        (r'rgba\(51,153,255,([\d.]+)\)', r"rgba(var(--modspotify_rgb_miscellaneous_hover_bg),\1)"),
        (r'rgba\(30,50,100,([\d.]+)\)', r"rgba(var(--modspotify_rgb_miscellaneous_hover_bg),\1)"),
        (r'rgba\(24, 24, 24, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(25,20,20,([\d.]+)\)', r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)"),
        (r'rgba\(160, 160, 160, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_pressing_button_fg),\1)"),
        (r'rgba\(255, 255, 255, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_pressing_button_fg),\1)"),
        (r'rgba\(0, 0, 0, ([\d.]+)\)', r"rgba(var(--modspotify_rgb_cover_overlay_and_shadow),\1)"),
        (r'rgba\(0,0,0,([\d.]+)\)', r"rgba(var(--modspotify_rgb_cover_overlay_and_shadow),\1)")
    ]
    for old, new in replacements:
        css_data = re.sub(old, new, css_data)

    return css_data


def generate_color_vars(colours):
    css_vars = ":root {"
    for key, value in colours.items():
        css_vars += f"--modspotify_{key}:{value};\n"
        css_vars += f"--modspotify_rgb_{key}:{hex_to_rgb(value)};"
    css_vars += "}\n"
    return css_vars


def inject_css(folder_path, user_css):
    if 'Colours' in CONFIG:
        colours = CONFIG['Colours']
    else:
        colours = default_colors

    css_data = generate_color_vars(colours)

    if user_css:
        with open(user_css) as user_css:
            css_data += user_css.read()

    with open(os.path.join(folder_path, "css/user.css"), "w") as css_file:
        css_file.write(css_data)


def process_css(folder_path):
    css_dir = os.path.join(folder_path, "css")
    processed_glue = None
    if os.path.isdir(css_dir):
        for css in glob.glob(os.path.join(css_dir, "*.css")):
            css_filename = os.path.basename(css)
            debug_print(f"\t\t{css_filename}", 3)
            if css_filename == "glue.css" and processed_glue is not None:
                css_data = processed_glue
            else:
                with open(css) as css_file:
                    css_data = convert_css(css_file.read())
                if css_filename == "glue.css":
                    processed_glue = css_data
            with open(css, "w") as css_file:
                css_file.write(css_data)


def process_html(folder_path, extensions):
    for html in glob.glob(os.path.join(folder_path, "*.html")):
        html_filename = os.path.basename(html)
        debug_print(f"\t\t{html_filename}", 3)
        with open(html) as html_file:
            html_data = html_file.read()
        html_data = html_data.replace('</head>', '<link rel="stylesheet" class="userCSS" href="css/user.css"></head>')
        if 'zlink' in folder_path:
            html_data = html_data.replace('</body>', '<script src="/jquery-3.3.1.min.js"></script></body>')
            for ext in (extensions if not None else []):
                html_data = html_data.replace('</body>', f'<script src="/{os.path.basename(ext)}"></script></body>')
        with open(html, "w") as html_file:
            html_file.write(html_data)


def replace_in_file(filename, js_filename, pattern, repl):
    file_path = os.path.join(TEMP_DIR_PATH, filename, js_filename)
    with open(file_path) as file:
        file_data = file.read()
    with open(file_path, "w") as file:
        file.write(re.sub(pattern, repl, file_data))


def inject_js(filename, js_filename):
    shutil.copy2(os.path.join(RICETIFY_FOLDER, js_filename), os.path.join(TEMP_DIR_PATH, filename))


def mod_js(extensions):
    js_options = CONFIG['Javascript']
    if js_options.getboolean('enabled_dev_tools'):
        debug_print("\tEnabled dev tools", 1)
        replace_in_file("settings.spa", "bundle.js", r"(const isEmployee = ).*;", r"\1true;")
    if js_options.getboolean('enabled_home'):
        debug_print("\tEnabled home", 1)
        replace_in_file('zlink.spa', 'main.bundle.js', r"this\._initialState\.isHomeEnabled", r"true")
        replace_in_file('zlink.spa', 'main.bundle.js', r"isHomeEnabled(\?void 0:_flowControl)", r"true\1")
    if js_options.getboolean('enabled_radio'):
        debug_print("\tEnabled radio", 1)
        replace_in_file('zlink.spa', 'main.bundle.js', r'\(0,_productState\.hasValue\)\("radio","1"\)', r"true")
    mod_options = r''
    if js_options.getboolean('enabled_lyrics') and js_options.getboolean('lyrics_always_show'):
        debug_print("\tEnabled lyrics and always show button", 1)
        replace_in_file('lyrics.spa', 'bundle.js', r'(const anyAbLyricsEnabled = )', r'\1true || ')
        replace_in_file('zlink.spa', 'main.bundle.js', r'(lyricsEnabled\()trackHasLyrics&&\(.*?\)', r'\1true')
        mod_options = r'trackControllerOpts.noService = false;\n'
    elif js_options.getboolean('enabled_lyrics'):
        debug_print("\tEnabled lyrics", 1)
        replace_in_file('lyrics.spa', 'bundle.js', r'(const anyAbLyricsEnabled = )', r'\1true || ')
        replace_in_file('zlink.spa', 'main.bundle.js', r'(lyricsEnabled\(trackHasLyrics)&&\(.*?\)', r'\1')
        mod_options = r'trackControllerOpts.noService = false;\n'
    elif js_options.getboolean('lyrics_always_show'):
        debug_print("\tEnabled always show lyrics button", 1)
        replace_in_file('zlink.spa', 'main.bundle.js', r'(lyricsEnabled\()trackHasLyrics&&\(.*\)', r'\1true')
    if mod_options != "":
        replace_in_file('lyrics.spa', 'bundle.js', r'(trackController\.init\(trackControllerOpts\))',
                        mod_options + r"\1")

    inject_js("zlink.spa", "jquery-3.3.1.min.js")
    replace_in_file('zlink.spa', 'main.bundle.js', r'PlayerUI\.prototype\.setup=function\(\){',
                    'PlayerUI.prototype.setup=function(){chrome.player={};chrome.player.seek=(p)=>{if('
                    'p<=1)p=Math.round(p*(chrome.playerData?chrome.playerData.track.metadata.duration:0));this.seek('
                    'p)};chrome.player.getProgressMs=()=>this.progressbar.getRealValue('
                    ');chrome.player.getProgressPercent=()=>this.progressbar.getPercentage('
                    ');chrome.player.getDuration=()=>this.progressbar.getMaxValue();chrome.player.skipForward=('
                    'a=15e3)=>chrome.player.seek(chrome.player.getProgressMs()+a);chrome.player.skipBack=('
                    'a=15e3)=>chrome.player.seek(chrome.player.getProgressMs()-a);chrome.player.setVolume=('
                    'v)=>this.changeVolume(v, false);chrome.player.increaseVolume=()=>this.increaseVolume('
                    ');chrome.player.decreaseVolume=()=>this.decreaseVolume();chrome.player.getVolume=('
                    ')=>this.volumebar.getValue();chrome.player.next=()=>this._doSkipToNext();chrome.player.back=('
                    ')=>this._doSkipToPrevious();chrome.player.togglePlay=()=>this._doTogglePlay('
                    ');chrome.player.play=()=>{eventDispatcher.dispatchEvent(new Event('
                    'Event.TYPES.PLAYER_RESUME))};chrome.player.pause=()=>{eventDispatcher.dispatchEvent(new Event('
                    'Event.TYPES.PLAYER_PAUSE))};chrome.player.isPlaying=()=>this.progressbar.isPlaying('
                    ');chrome.player.toggleShuffle=()=>this.toggleShuffle();chrome.player.getShuffle=('
                    ')=>this.shuffle();chrome.player.setShuffle=(b)=>{this.shuffle(b)};chrome.player.toggleRepeat=('
                    ')=>this.toggleRepeat();chrome.player.getRepeat=()=>this.repeat();chrome.player.setRepeat=(r)=>{'
                    'this.repeat(r)};chrome.player.getMute=()=>this.mute();chrome.player.toggleMute=('
                    ')=>this._doToggleMute();chrome.player.setMute=(b)=>{this.volumeEnabled()&&this.changeVolume('
                    'this._unmutedVolume,b)};chrome.player.thumbUp=()=>this.thumbUp();chrome.player.getThumbUp=('
                    ')=>this.trackThumbedUp();chrome.player.thumbDown=()=>this.thumbDown('
                    ');chrome.player.getThumbDown=()=>this.trackThumbedDown();chrome.player.formatTime=('
                    'ms)=>this._formatTime(ms);chrome.player.eventListeners={};chrome.player.addEventListener=(type,'
                    'callback)=>{if(!(type in chrome.player.eventListeners)){chrome.player.eventListeners[type]=['
                    ']}chrome.player.eventListeners[type].push(callback)};chrome.player.removeEventListener=(type,'
                    'callback)=>{if(!(type in chrome.player.eventListeners)){return}var '
                    'stack=chrome.player.eventListeners[type];for(var i=0,l=stack.length;i<l;i+=1){if(stack['
                    'i]===callback){stack.splice(i,1);return}}};chrome.player.dispatchEvent=(event)=>{if(!(event.type '
                    'in chrome.player.eventListeners)){return true}var stack=chrome.player.eventListeners['
                    'event.type];for(var i=0,l=stack.length;i<l;i+=1){stack[i](event)}return!event.defaultPrevented};')
    # Leak track meta data, player state, current playlist to chrome.playerData
    replace_in_file('zlink.spa', 'main.bundle.js', r'const metadata=data\.track\.metadata;',
                    'const metadata=data.track.metadata;chrome.playerData=data;')
    # Leak localStorage and showNotification
    replace_in_file('zlink.spa', 'main.bundle.js', r'_localStorage2\.default\.get\(SETTINGS_KEY_AD\);',
                    '_localStorage2.default.get(SETTINGS_KEY_AD);chrome.localStorage=_localStorage2.default;'
                    'chrome.showNotification = text => {_eventDispatcher2.default.dispatchEvent(new _event2.default('
                    '_event2.default.TYPES.SHOW_NOTIFICATION_BUBBLE, {i18n: text}))};')
    # Leak bridgeAPI
    replace_in_file('zlink.spa', 'main.bundle.js', r'BuddyList\.prototype\.setup=function\(\){',
                    'BuddyList.prototype.setup=function(){chrome.bridgeAPI = _bridge;')
    # Leak audio data fetcher to chrome.getAudioData
    replace_in_file('zlink.spa', 'main.bundle.js', r'PlayerHelper\.prototype\._player=null',
                    'var uriToId=u=>{var t=u.match(/^spotify:track:(.*)/);if(!t||t.length<2)return false;'
                    'else return t[1]};chrome.getAudioData=(callback, uri)=>{uri=uri||chrome.playerData.track.uri;if('
                    'typeof(callback)!=="function"){console.log("chrome.getAudioData: callback has to be a function");'
                    'return;};var id=uriToId(uri);if(id)cosmos.resolver.get(`hm://audio-attributes/v1/audio-analysis/'
                    '${id}`, (e,p)=>{if(e){console.log(e);callback(null);return;}if('
                    'p._status===200&&p._body&&p._body!==""){var data=JSON.parse(p._body);data.uri=uri;callback(data);'
                    '}else callback(null)})};new Player(cosmos.resolver,"spotify:internal:queue","queue","1.0.0")'
                    '.subscribeToQueue((e,r)=>{if(e){console.log(e);return;}chrome.queue=r.getJSONBody();});'
                    'PlayerHelper.prototype._player=null')
    replace_in_file('zlink.spa', 'main.bundle.js', r'const Adaptor=function\(bridge,cosmos\)\{',
                    'const Adaptor=function(bridge,cosmos){chrome.libURI = liburi;chrome.addToQueue=(uri,callback)=>'
                    '{uri=liburi.from(uri);if(uri.type===liburi.Type.ALBUM){this.getAlbumTracks(uri,(err,tracks)=>'
                    '{if(err){console.log("chrome.addToQueue",err);return};this.queueTracks(tracks,callback)})}else '
                    'if(uri.type===liburi.Type.TRACK||uri.type===liburi.Type.EPISODE){this.queueTracks([uri],callback)}'
                    'else{console.log("chrome.addToQueue: Only Track and Album URIs are accepted")}};'
                    'chrome.removeFromQueue=(uri,callback)=>{if(chrome.queue){var indices=[],uriObj=liburi.from(uri);'
                    'if(uriObj.type===liburi.Type.ALBUM){this.getAlbumTracks(uriObj,(err,tracks)=>{if(err){'
                    'console.log(err);return}tracks.forEach(t=>chrome.queue.next_tracks.forEach((nt,index)=>'
                    't==nt.uri&&indices.push(index)))})}else if(uriObj.type===liburi.Type.TRACK||'
                    'uriObj.type===liburi.Type.EPISODE){chrome.queue.next_tracks.forEach((track,index)=>'
                    'track.uri==uri&&indices.push(index))}else{console.log("chrome.removeFromQueue: Only Album, '
                    'Track and Episode URIs are accepted")}indices=indices.reduce((a,b)=>{if(a.indexOf(b)<0){a.push('
                    'b)}return a},[]);this.removeTracksFromQueue(indices,callback)}}; ')
    # Register song change event
    replace_in_file('zlink.spa', 'main.bundle.js', r'this\._uri=track\.uri,this\._trackMetadata=track\.metadata',
                    'this._uri=track.uri,this._trackMetadata=track.metadata,'
                    'chrome.player&&chrome.player.dispatchEvent(new Event("songchange"))')
    # Register play/pause state change event
    replace_in_file('zlink.spa', 'main.bundle.js', r'(this\.playing\(data\.is_playing&&!data\.is_paused\).*?;)',
                    r'\1(this.playing()!==this._isPlaying)&&(this._isPlaying=this.playing(),'
                    r'chrome.player&&chrome.player.dispatchEvent(new Event("onplaypause")));')
    # Register progress change event
    replace_in_file('zlink.spa', 'main.bundle.js', r'(PlayerUI\.prototype\._onProgressBarProgress=function.*?{)',
                    r'\1chrome.player&&chrome.player.dispatchEvent(new Event("onprogress"));')
    # Leak Cosmos API to chrome.cosmosAPI
    replace_in_file('zlink.spa', 'main.bundle.js', r'(var _spotifyCosmosApi2=_interop.*?;)',
                    r'\1chrome.cosmosAPI=_spotifyCosmosApi2.default;')

    for ext in (extensions if not None else []):
        inject_js('zlink.spa', ext)


def make_backup(backup_dir):
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)
    version = get_spotify_version()
    backup_version_path = os.path.join(backup_dir, "version.txt")
    if os.path.exists(backup_version_path):
        with open(backup_version_path) as version_file:
            version_in_backup = version_file.read()
    else:
        version_in_backup = ""
    if version != version_in_backup:
        for file in glob.glob(os.path.join(SPOTIFY_PATH, 'Apps', '*.spa')):
            shutil.copy2(file, backup_dir)
        with open(backup_version_path, "w") as version_file:
            version_file.write(version)


class FullPaths(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def is_file(filename):
    if not os.path.isfile(filename):
        raise argparse.ArgumentTypeError(f"{filename} is not a file")
    else:
        return filename


def is_folder(dir_name):
    if not os.path.isdir(dir_name):
        raise argparse.ArgumentTypeError(f"{dir_name} is not a directory")
    else:
        return dir_name


def main():
    global GLOBAL_VERBOSITY

    parser = argparse.ArgumentParser(description="Rice spotify")
    parser.add_argument('-u', '--user-css', help="Apply custom CSS", action=FullPaths, type=is_file)
    parser.add_argument('-o', '--output', help='Output folder', action=FullPaths, type=is_folder)
    parser.add_argument('-v', '--verbosity', help='Increase output verbosity', type=int, choices=[0, 1, 2, 3],
                        default=0)
    parser.add_argument('-c', '--config', help="Load a config file", action=FullPaths, type=is_file)
    parser.add_argument('-e', '--extensions', help="A list of extensions to inject", nargs='+', type=is_file)
    args = parser.parse_args()

    GLOBAL_VERBOSITY = args.verbosity

    if args.config:
        CONFIG.read(args.config)

    if 'SUDO_USER' in os.environ:
        home_dir = os.path.expanduser(f"~{os.getenv('SUDO_USER')}")
    else:
        home_dir = str(Path.home())
    backup_dir = os.path.join(home_dir, ".spotify_backup")

    make_backup(backup_dir)

    # Extract all files and process css and html (javascript involved modifying many files)
    debug_print("Extracting files", 0)
    for file in glob.glob(os.path.join(backup_dir, '*.spa')):
        filename = os.path.basename(file)
        debug_print(f"\tExtracting: {filename}", 2)

        sub_dir_path = os.path.join(TEMP_DIR_PATH, filename)

        with zipfile.ZipFile(file, "r") as spa:
            spa.extractall(path=sub_dir_path)

        process_css(sub_dir_path)

        process_html(sub_dir_path, args.extensions)

        inject_css(sub_dir_path, user_css=args.user_css)

    debug_print('Modifying JS', 0)
    if 'Javascript' in CONFIG:
        mod_js(args.extensions)

    # Recompile and move to output
    debug_print("Compiling files", 0)
    for folder in glob.glob(os.path.join(TEMP_DIR_PATH, '*.spa')):
        folder_name = os.path.basename(folder)
        debug_print(f"\tCompiling {os.path.basename(folder_name)}", 2)
        if args.output:
            output_file = os.path.join(args.output, folder_name)
        else:
            output_file = os.path.join(os.curdir, folder_name)
        shutil.make_archive(output_file, "zip", folder)
        shutil.move(output_file + ".zip", output_file)


if __name__ == "__main__":
    main()
