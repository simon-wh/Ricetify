import argparse
import configparser
import glob
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

SPOTIFY_APPS_PATH = "/usr/share/spotify/Apps"
BACKUP_DIR = str(Path.home())+"/.config/ricify/spotify_backup"

TEMP_DIR_OBJ = tempfile.TemporaryDirectory()
TEMP_DIR = TEMP_DIR_OBJ.name

GLOBAL_VERBOSITY = 0

CONFIG = configparser.ConfigParser()

default_colors = {
    "main_fg": "ffffff",
    "secondary_fg": "c0c0c0",
    "main_bg": "282828",
    "sidebar_and_player_bg": "000000",
    "cover_overlay_and_shadow": "000000",
    "indicator_fg_and_button_bg": "1db954",
    "pressing_fg": "cdcdcd",
    "slider_bg": "404040",
    "sidebar_indicator_and_hover_button_bg": "1ed660",
    "scrollbar_fg_and_selected_row_bg": "333333",
    "pressing_button_fg": "cccccc",
    "pressing_button_bg": "179443",
    "selected_button": "18ac4d",
    "miscellaneous_bg": "4687d6",
    "miscellaneous_hover_bg": "2e77d0",
    "preserve_1": "ffffff"
}


def debug_print(str, verbosity):
    if verbosity <= GLOBAL_VERBOSITY:
        print(str)


def hex_to_rgb(hex):
    r = int(hex[:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:], 16)
    return f"{r},{g},{b}"


def convert_css(css_data):
    css_data = css_data.replace("#1ed660",
                                "var(--modspotify_sidebar_indicator_and_hover"
                                "_button_bg)")
    css_data = css_data.replace("#1ed760",
                                "var(--modspotify_sidebar_indicator_and_hover_"
                                "button_bg)")

    css_data = css_data.replace("#1db954",
                                "var(--modspotify_indicator_fg_and_button_bg)")
    css_data = css_data.replace("#1df369",
                                "var(--modspotify_indicator_fg_and_button_bg)")
    css_data = css_data.replace("#1df269",
                                "var(--modspotify_indicator_fg_and_button_bg)")
    css_data = css_data.replace("#1cd85e",
                                "var(--modspotify_indicator_fg_and_button_bg)")
    css_data = css_data.replace("#1bd85e",
                                "var(--modspotify_indicator_fg_and_button_bg)")

    css_data = css_data.replace("#18ac4d",
                                "var(--modspotify_selected_button)")
    css_data = css_data.replace("#18ab4d",
                                "var(--modspotify_selected_button)")

    css_data = css_data.replace("#179443",
                                "var(--modspotify_pressing_button_bg)")
    css_data = css_data.replace("#14833b",
                                "var(--modspotify_pressing_button_bg)")

    css_data = css_data.replace("#282828",
                                "var(--modspotify_main_bg)")
    css_data = css_data.replace("#121212",
                                "var(--modspotify_main_bg)")
    css_data = css_data.replace("#999999",
                                "var(--modspotify_main_bg)")
    css_data = css_data.replace("#606060",
                                "var(--modspotify_main_bg)")

    css_data = re.sub(r'rgba\(18, 18, 18, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(18, 19, 20, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(80, 55, 80, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(40, 40, 40, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(40,40,40,([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(24, 24, 24, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(18, 19, 20, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)
    css_data = css_data = css_data.replace("#181818",
                                           "var(--modspotify_sidebar_and_"
                                           "player_bg)")
    css_data = css_data = css_data.replace("#000000",
                                           "var(--modspotify_sidebar_and_"
                                           "player_bg)")

    css_data = css_data.replace("#333333",
                                "var(--modspotify_scrollbar_fg_and_selected_"
                                "row_bg)")
    css_data = css_data.replace("#3f3f3f",
                                "var(--modspotify_scrollbar_fg_and_selected_"
                                "row_bg)")
    css_data = css_data.replace("#535353",
                                "var(--modspotify_scrollbar_fg_and_selected_"
                                "row_bg)")

    css_data = css_data.replace("#404040", "var(--modspotify_slider_bg)")

    css_data = css_data.replace("#000011",
                                "var(--modspotify_sidebar_and_player_bg)")
    css_data = css_data.replace("#0a1a2d",
                                "var(--modspotify_sidebar_and_player_bg)")

    css_data = css_data.replace("#ffffff", "var(--modspotify_main_fg)")

    css_data.replace("#f8f8f7", "var(--modspotify_pressing_fg)")
    css_data = css_data.replace("#fcfcfc", "var(--modspotify_pressing_fg)")
    css_data = css_data.replace("#d9d9d9", "var(--modspotify_pressing_fg)")
    css_data = css_data.replace("#cdcdcd", "var(--modspotify_pressing_fg)")
    css_data = css_data.replace("#e6e6e6", "var(--modspotify_pressing_fg)")
    css_data = css_data.replace("#e5e5e5", "var(--modspotify_pressing_fg)")

    css_data = css_data.replace("#adafb2", "var(--modspotify_secondary_fg)")
    css_data = css_data.replace("#c8c8c8", "var(--modspotify_secondary_fg)")
    css_data = css_data.replace("#a0a0a0", "var(--modspotify_secondary_fg)")
    css_data = css_data.replace("#bec0bb", "var(--modspotify_secondary_fg)")
    css_data = css_data.replace("#bababa", "var(--modspotify_secondary_fg)")
    css_data = css_data.replace("#b3b3b3", "var(--modspotify_secondary_fg)")
    css_data = css_data.replace("#c0c0c0", "var(--modspotify_secondary_fg)")

    css_data = re.sub(r'rgba\(179, 179, 179, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_secondary_fg),\1)",
                      css_data)

    css_data = css_data.replace("#cccccc",
                                "var(--modspotify_pressing_button_fg)")
    css_data = css_data.replace("#ededed",
                                "var(--modspotify_pressing_button_fg)")

    css_data = css_data.replace("#4687d6",
                                "var(--modspotify_miscellaneous_bg)")
    css_data = re.sub(r'rgba\(70, 135, 214, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_miscellaneous_bg),\1)",
                      css_data)

    css_data = css_data.replace("#2e77d0",
                                "var(--modspotify_miscellaneous_hover_bg)")
    css_data = re.sub(r'rgba\(51,153,255,([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_miscellaneous_hover_bg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(30,50,100,([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_miscellaneous_hover_bg),\1)",
                      css_data)

    css_data = re.sub(r'rgba\(24, 24, 24, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(25,20,20,([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_sidebar_and_player_bg),\1)",
                      css_data)

    css_data = re.sub(r'rgba\(160, 160, 160, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_pressing_button_fg),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(255, 255, 255, ([\d.]+)\)',
                      r"rgba(var(--modspotify_rgb_pressing_button_fg),\1)",
                      css_data)

    css_data = css_data.replace("#ddd;",
                                "var(--modspotify_pressing_button_fg);")

    css_data = css_data.replace("#000;",
                                "var(--modspotify_sidebar_and_player_bg);")
    css_data = css_data.replace("#000 ",
                                "var(--modspotify_sidebar_and_player_bg) ")

    css_data = css_data.replace("#333;",
                                "var(--modspotify_scrollbar_fg_and_selected_"
                                "row_bg);")
    css_data = css_data.replace("#333 ",
                                "var(--modspotify_scrollbar_fg_and_selected_"
                                "row_bg) ")

    css_data = css_data.replace("#444;", "var(--modspotify_slider_bg);")
    css_data = css_data.replace("#444 ", "var(--modspotify_slider_bg) ")

    css_data = css_data.replace("#fff;", "var(--modspotify_main_fg);")
    css_data = css_data.replace("#fff ", "var(--modspotify_main_fg) ")

    css_data = css_data.replace(" black;",
                                " var(--modspotify_sidebar_and_player_bg);")
    css_data = css_data.replace(" black ",
                                " var(--modspotify_sidebar_and_player_bg) ")

    css_data = css_data.replace(" gray ", " var(--modspotify_main_bg) ")
    css_data = css_data.replace(" gray;", " var(--modspotify_main_bg);")

    css_data = css_data.replace(" lightgray ",
                                " var(--modspotify_pressing_button_fg) ")
    css_data = css_data.replace(" lightgray;",
                                " var(--modspotify_pressing_button_fg);")

    css_data = css_data.replace(" white;", " var(--modspotify_main_fg);")
    css_data = css_data.replace(" white ", " var(--modspotify_main_fg) ")

    css_data = re.sub(r'rgba\(0, 0, 0, ([\d.]+)\)',
                      r"rgba(var(--"
                      r"modspotify_rgb_cover_overlay_and_shadow),\1)",
                      css_data)
    css_data = re.sub(r'rgba\(0,0,0,([\d.]+)\)',
                      r"rgba(var(--"
                      r"modspotify_rgb_cover_overlay_and_shadow),\1)",
                      css_data)

    css_data = css_data.replace("#fff", "var(--modspotify_main_fg)")

    css_data = css_data.replace("#000",
                                "var(--modspotify_sidebar_and_player_bg)")

    return css_data


def generate_color_vars(colours):
    vars = ":root {"
    for key, value in colours.items():
        vars += f"--modspotify_{key}:#{value};\n"
        vars += f"--modspotify_rgb_{key}:{hex_to_rgb(value)};"
    vars += "}\n"
    return vars


def inject_css(user_css):
    if 'Colours' in CONFIG:
        colours = CONFIG['Colours']
    else:
        colours = default_colors

    css_data = generate_color_vars(colours)

    if user_css:
        with open(user_css) as user_css:
            css_data += user_css.read()

    with open(os.path.join(TEMP_DIR, "css/user.css"), "w") as css_file:
        css_file.write(css_data)


def process_css():
    css_dir = os.path.join(TEMP_DIR, "css")
    processed_glue = None
    if os.path.isdir(css_dir):
        for css in glob.glob(os.path.join(css_dir, "*.css")):
            css_filename = os.path.basename(css)
            debug_print(f"\t{css_filename}", 2)
            if css_filename == "glue.css" and processed_glue is not None:
                css_data = processed_glue
            else:
                with open(css) as css_file:
                    css_data = convert_css(css_file.read())
                if css_filename == "glue.css":
                    processed_glue = css_data
            with open(css, "w") as css_file:
                css_file.write(css_data)


def process_html():
    for html in glob.glob(os.path.join(TEMP_DIR, "*.html")):
        html_filename = os.path.basename(html)
        debug_print(f"\t{html_filename}", 2)
        with open(html) as html_file:
            html_data = html_file.read()
        html_data = html_data.replace('</head>',
                                      '<link rel="stylesheet" class="userCSS"'
                                      ' href="css/user.css"></head>')
        with open(html, "w") as html_file:
            html_file.write(html_data)


def cleanup(dir):
    for root, dirs, files in os.walk(dir):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


class FullPaths(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest,
                os.path.abspath(os.path.expanduser(values)))


def is_file(filename):
    if not os.path.isfile(filename):
        raise argparse.ArgumentTypeError(f"{filename} is not a file")
    else:
        return filename


def is_folder(dirname):
    if not os.path.isdir(dirname):
        raise argparse.ArgumentTypeError(f"{dirname} is not a directory")
    else:
        return dirname


def main():
    global GLOBAL_VERBOSITY
    parser = argparse.ArgumentParser(description="Rice spotify")
    parser.add_argument('-u', '--user-css', help="Apply custom CSS",
                        action=FullPaths, type=is_file)
    parser.add_argument('-o', '--output', help='Output folder',
                        action=FullPaths, type=is_folder)
    parser.add_argument('-v', '--verbosity', help='Increase output verbosity',
                        type=int, choices=[0, 1, 2], default=0)
    parser.add_argument('-c', '--config', help="Load a config file",
                        action=FullPaths, type=is_file)
    args = parser.parse_args()

    GLOBAL_VERBOSITY = args.verbosity

    if args.config:
        CONFIG.read(args.config)

    for file in glob.glob(os.path.join(SPOTIFY_APPS_PATH, '*.spa')):
        filename = os.path.basename(file)
        debug_print(f"Processing: {filename}", 1)

        # Extract file
        with zipfile.ZipFile(file, "r") as zip:
            zip.extractall(path=TEMP_DIR)

        process_css()

        process_html()

        inject_css(user_css=args.user_css)

        if args.output:
            output_file = os.path.join(args.output, filename)
        else:
            output_file = os.path.join(os.curdir, filename)

        shutil.make_archive(output_file,
                            "zip", TEMP_DIR)
        shutil.move(output_file+".zip", output_file)

        # Empty directory for next loop
        cleanup(TEMP_DIR)


if __name__ == "__main__":
    main()
