import argparse
from PIL import Image, ImageDraw, ImageFont
from argos_hola import get_trans
from collections import defaultdict
import argostranslate.apis
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

lang_fudge =  {'ja': 4.2,'ko': 4}

def get_max_width(trans, languages, font_size) -> int:
    """
    estimates from language-specific fudge how big the strings will be in the GIF
    """
    mx = 0
    for t,l in zip(trans,languages):
        adj_len = len(t) * lang_fudge.get(l, 2.1) * font_size
        mx = (adj_len if mx<adj_len else mx)
    return int(mx)
    
def create_gif(params):
    # PARAMS INPUT
    text = params.text
    if params.text_array:
        text_array = params.text_array.split(',')
    if not text and not text_array:
        raise ValueError("need text or text array")
    
    delay = params.delay
    font_color = params.font_color
    font_path = params.font_path
    background_color = params.background_color
    font_size = params.font_size
    languages = params.languages
    all_langs = [x['code'] for x in argostranslate.apis.LibreTranslateAPI().languages()]
    if 'all' in languages:
        languages = all_langs
    if any(l not in all_langs for l in languages):
        raise ValueError(f"Invalid lang supplied in following list: {languages}")
    # Hard-coded width
    width, height = (int(x) for x in params.size.split(','))
    # Create GIF frames
    frames = []

    text_array = get_trans(text, languages=languages) if text else text_array

    max_width = get_max_width(text_array, languages, font_size) if text else width

    def create_image(text, font, font_color, background_color):
        image = Image.new("RGB", (max_width, height), color=background_color)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font, height/2)
        x = 0
        y = height//8
        draw.text((x, y), text, font=font, fill=font_color)
        return image
    
    for t in text_array:
        image = create_image(
            t, font_path, font_color, background_color,
        )
        # Overlay the background_image onto the image here
        frames.append(image)
    # Save the frames as a GIF
    frames[0].save(
        params.gif_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,  # 0 means infinite loop
        duration=delay,  # Time in milliseconds between frames
    )
    print(f"GIF created as {params.gif_path}!")


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
        "--font_size", type=int, default=32, help="Delay between frames in milliseconds"
    )
    parser.add_argument(
        "--font_color", type=str,required=True, help="Font color (R,G,B)"
    )
    parser.add_argument("--font_path", required=True, help="Path to the font file")
    parser.add_argument(
        "--background_color", type=str, default="0,0,0", help="Background color (R,G,B)"
    )
    parser.add_argument("--size", type=str, default="256,256", help="Image width")
    parser.add_argument("--gif_path", default=f"output.gif", help="Path to save the output GIF")
    parser.add_argument("--languages", nargs='+', default="all", help="two letter code listˀ")
    params = parser.parse_args()
    params.font_color = tuple(map(int, params.font_color.split(",")))
    params.background_color = tuple(map(int, params.background_color.split(",")))
    create_gif(params)

if __name__ == "__main__":
     main()
