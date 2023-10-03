import argparse
from PIL import Image, ImageDraw, ImageFont
from argos_hola import get_trans
from collections import defaultdict
import argostranslate.apis
from typing import List
import urllib
"""
############################################
############################################
############################################
############################################
###*****########***#########################
###*****########***#########****############
###*****#######******#######****############
###*****####***********#####****############
###*****###**************###****############
##########***************###****############
##########****************##****############
###****###*****#***#******##****#********###
###****###****##***##*****##**************##
###****###****##***#########***************#
###****###*****#***#########****************
###****###*********#########******####******
###****###***********#######*****######*****
###****####************#####****########****
###****######************###****########****
###****#########*********###****########****
###****#########**********##****########****
###****#########***##*****##****########****
###****#########***##*****##****########****
###****###*****#***##*****##****########****
###****###*****#***##*****##****########****
###****###*********#******##****########****
###****###***************###****########****
###****####**************###****########****
###****#####***********#####****########****
###****########******#######################
###****#########***#########################
###****#########***#########################
###****#####################################
*******#####################################
*******#####################################
*******#####################################
******######################################
############################################
############################################
Prompt: Given a phrase, create a gif that repeats the text in multiple languages on a delay.

Font is selectable. Color of text is selectable. Background color is selectable.

Background can be any image. 

Images can change per language.

Params:
Text, Delay, FontColor, Font, BackgroundColor, ImagesArray

"""

lang_fudge = {"ja": 4.2, "ko": 4}


def get_max_width(trans, languages, font_size) -> int:
    """
    estimates from language-specific fudge how big the strings will be in the GIF
    """
    mx = 0
    for t, l in zip(trans, languages):
        adj_len = len(t) * lang_fudge.get(l, 2.1) * font_size
        mx = adj_len if mx < adj_len else mx
    return int(mx)


def create_gif(params):
    # PARAMS INPUT
    text = params.text
    if params.text_array:
        text_array = params.text_array.split(",")
    if not text and not text_array:
        raise ValueError("need text or text array")

    delay = params.delay
    sine_delay = params.sine_delay
    font_color = params.font_color
    font_path = params.font_path
    background_color = params.background_color
    font_size = params.font_size
    languages = params.languages
    try:
        all_langs = [x["code"] for x in argostranslate.apis.LibreTranslateAPI().languages()]
        if "all" in languages:
            languages = all_langs
        if any(l not in all_langs for l in languages):
            raise ValueError(f"Invalid lang supplied in following list: {languages}")
    except urllib.error.HTTPError:
        print('Unable to reach argos server. Translating disabled.')

    

    # Hard-coded width
    width, height = (int(x) for x in params.size.split(","))
    # Create GIF frames
    frames = []

    text_array = get_trans(text, languages=languages) if text else text_array

    max_width = get_max_width(text_array, languages, font_size) if text else width

    def create_image(text, font, font_color, background_color):
        image = Image.new("RGB", (max_width, height), color=background_color)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font, height / 2)
        x = 0
        y = height // 8
        draw.text((x, y), text, font=font, fill=font_color)
        return image

    # x= Image.new("RGB",(4,4,),color=(0,0,0,)).save()
    for t in text_array:
        image = create_image(
            t,
            font_path,
            font_color,
            background_color,
        )
        # Overlay the background_image onto the image here
        frames.append(image)
    if not sine_delay:
        # Save the frames as a GIF
        frames[0].save(
            params.gif_path,
            save_all=True,
            append_images=frames[1:],
            loop=0,  # 0 means infinite loop
            duration=delay,  # Time in milliseconds between frames
        )
    else:
        print("SINE:" + str(sine_delay) + ", DELAY:" + str(delay))
        # Save the frames as a GIF
        new_frames = sine_adder(frames, sine_delay // delay)
        frames[0].save(
            params.gif_path,
            save_all=True,
            append_images=new_frames,
            loop=0,  # 0 means infinite loop
            duration=delay,  # Time in milliseconds between frames
        )
    print(f"GIF created as {params.gif_path}!")


def sine_adder(f: List, d: int):
    nf = []
    for robin in range(len(f)):
        # each iteration requires 0 -> i-1
        for pre in f[0:robin]:
            nf.append(pre)
        # stuff up
        for _ in range(d):
            nf.append(f[robin])
        # each iteration requires i+1 -> n
        for post in f[robin + 1 :]:
            nf.append(post)
    return nf


def main():
    parser = argparse.ArgumentParser(
        description="Create a GIF with customizable parameters"
    )
    parser.add_argument("--text", default=None, help="The text to display")
    parser.add_argument("--text_array", default=None, help="The text to display")
    parser.add_argument(
        "--delay", type=int, default=100, help="Delay between frames in milliseconds"
    )
    parser.add_argument(
        "--sine_delay",
        type=int,
        default=0,
        help="If zero, ignored. Else, focuses on each frame for sine_delay seconds, round-robin",
    )
    parser.add_argument(
        "--font_size", type=int, default=32, help="Delay between frames in milliseconds"
    )
    parser.add_argument(
        "--font_color", type=str, default="256,256,256", help="Font color (R,G,B)"
    )
    parser.add_argument(
        "--font_path", default="fonts/arial.ttf", help="Path to the font file"
    )
    parser.add_argument(
        "--background_color", type=str, default="0,0,0", help="Background color (R,G,B)"
    )
    parser.add_argument("--size", type=str, default="256,256", help="Image width")
    parser.add_argument(
        "--gif_path", default="output.gif", help="Path to save the output GIF"
    )
    parser.add_argument(
        "--languages", nargs="+", default="all", help="two letter code listˀ"
    )
    params = parser.parse_args()
    params.font_color = tuple(map(int, params.font_color.split(",")))
    params.background_color = tuple(map(int, params.background_color.split(",")))
    create_gif(params)


if __name__ == "__main__":
    main()