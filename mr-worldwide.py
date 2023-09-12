import os, sys
import argparse
from PIL import Image, ImageDraw, ImageFont
import imageio
from argos_hola import get_trans

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
FONT_SIZE = 16

def create_image(text, font, font_color, background_color, width, height):
    image = Image.new("RGB", (width, height))# background_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font, FONT_SIZE)
    x = (width - width) // 2
    y = (height - height) // 2
    draw.text((x, y), text, font=font, fill=font_color)
    return image

def create_gif(params):
    text = params.text
    delay = params.delay
    font_color = params.font_color
    font_path = params.font_path
    background_color = params.background_color
    width, height = (int(x) for x in params.size.split(','))

    if params.languages == ['all']:
        params.languages = None
    # Create GIF frames
    frames = []
    trans = get_trans(text, languages=params.languages)
    for t in trans:
        print('saving',t)
        image = create_image(
            t, font_path, font_color, background_color, width, height
        )
        # Overlay the background_image onto the image here
        frames.append(image)
    # Save the frames as a GIF
    frames[0].save(
        params.gif_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,  # 0 means infinite loop
        duration=100,  # Time in milliseconds between frames
    )

    # # Save GIF
    # imageio.mimsave(
    #     params.gif_path, frames, duration=delay / 1000
    # )  # Duration in seconds
    print("GIF created!")


def main():
    parser = argparse.ArgumentParser(
        description="Create a GIF with customizable parameters"
    )
    parser.add_argument("--text", required=True, help="The text to display")
    parser.add_argument(
        "--delay", type=int, default=100, help="Delay between frames in milliseconds"
    )
    parser.add_argument(
        "--font_color", type=str,required=True, help="Font color (R,G,B)"
    )
    parser.add_argument("--font_path", required=True, help="Path to the font file")
    parser.add_argument(
        "--background_color", type=str, default="0,0,0", help="Background color (R,G,B)"
    )
    parser.add_argument("--size", type=str, default="256,256", help="Image width")
    parser.add_argument("--gif_path", default=".", help="Path to save the output GIF")
    parser.add_argument("--languages", nargs='+', default="all", help="two letter code listˀ")
    params = parser.parse_args()
    params.font_color = tuple(map(int, params.font_color.split(",")))
    # print(params.background_color.split(','))
    params.background_color = tuple(map(int, params.background_color.split(",")))
    # params.images = [params.images[i : i + 2] for i in range(0, len(params.images), 2)]
    create_gif(params)

if __name__ == "__main__":
     main()
