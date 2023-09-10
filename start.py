import os,sys
from PIL import Image

'''
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

'''
import argparse
from PIL import Image, ImageDraw, ImageFont
import imageio

def create_image(text, font, font_color, background_color, width, height):
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font, font_size)
    text_width, text_height = draw.textsize(text, font=font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, font=font, fill=font_color)
    return image

def create_gif(params):
    text = params.text
    delay = params.delay
    font_color = params.font_color
    font_path = params.font_path
    background_color = params.background_color
    width, height = params.width, params.height

    # Create GIF frames
    frames = []
    for language, background_image in params.images:
        image = create_image(text, font_path, font_color, background_color, width, height)
        # Overlay the background_image onto the image here
        frames.append(image)

    # Save GIF
    imageio.mimsave(params.gif_path, frames, duration=delay / 1000)  # Duration in seconds
    print("GIF created!")

def main():
    parser = argparse.ArgumentParser(description="Create a GIF with customizable parameters")
    parser.add_argument("--text", required=True, help="The text to display")
    parser.add_argument("--delay", type=int, default=100, help="Delay between frames in milliseconds")
    parser.add_argument("--font_color", type=str, default="255,255,255", help="Font color (R,G,B)")
    parser.add_argument("--font_path", required=True, help="Path to the font file")
    parser.add_argument("--background_color", type=str, default="0,0,0", help="Background color (R,G,B)")
    parser.add_argument("--width", type=int, default=500, help="Image width")
    parser.add_argument("--height", type=int, default=500, help="Image height")
    parser.add_argument("--images", nargs="+", required=True, help="List of language and background image pairs")
    parser.add_argument("--gif_path", required=True, help="Path to save the output GIF")

    params = parser.parse_args()
    params.font_color = tuple(map(int, params.font_color.split(",")))
    params.background_color = tuple(map(int, params.background_color.split(",")))
    params.images = [params.images[i:i+2] for i in range(0, len(params.images), 2)]

    create_gif(params)

if __name__ == "__main__":
	print('Give desired text')
    main()
