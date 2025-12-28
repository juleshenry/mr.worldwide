import argparse
from PIL import Image, ImageDraw, ImageFont
from argos_hola import get_trans
from collections import defaultdict
import argostranslate.apis
from typing import List, Tuple, Optional
import urllib
import math
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

# Color picker constants
CAMOUFLAGE_VARIATION = 25  # Pixel value variation for camouflage effect
LUMINANCE_THRESHOLD = 0.5  # Threshold for determining bright vs dark backgrounds


def get_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculate relative luminance of an RGB color.
    Uses the formula from WCAG 2.0 guidelines.
    """
    r, g, b = [x / 255.0 for x in rgb]
    
    # Apply gamma correction
    def adjust(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return math.pow((c + 0.055) / 1.055, 2.4)
    
    r, g, b = adjust(r), adjust(g), adjust(b)
    
    # Calculate luminance
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_contrast_ratio(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """
    Calculate the contrast ratio between two colors.
    Returns a value between 1 and 21, where higher means more contrast.
    """
    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)
    
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    return (lighter + 0.05) / (darker + 0.05)


def get_average_color(image: Image.Image) -> Tuple[int, int, int]:
    """
    Calculate the average color of an image.
    """
    # Resize to small size for faster computation
    img = image.resize((50, 50))
    pixels = list(img.getdata())
    
    if img.mode == 'RGBA':
        # Filter out fully transparent pixels
        pixels = [p[:3] for p in pixels if p[3] > 128]
    
    if not pixels:
        return (128, 128, 128)  # Default to gray if no pixels
    
    avg_r = sum(p[0] for p in pixels) // len(pixels)
    avg_g = sum(p[1] for p in pixels) // len(pixels)
    avg_b = sum(p[2] for p in pixels) // len(pixels)
    
    return (avg_r, avg_g, avg_b)


def get_contrasting_color(bg_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Determine the most contrasting color (black or white) for a given background.
    """
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    white_contrast = get_contrast_ratio(bg_color, white)
    black_contrast = get_contrast_ratio(bg_color, black)
    
    return white if white_contrast > black_contrast else black


def get_camouflaged_color(bg_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Determine a color similar to the background for camouflage effect.
    Slightly adjusts the background color to maintain some readability.
    """
    r, g, b = bg_color
    
    # Adjust based on luminance - darker backgrounds get lighter text, vice versa
    lum = get_luminance(bg_color)
    if lum > LUMINANCE_THRESHOLD:
        # Bright background - make text slightly darker
        r = max(0, r - CAMOUFLAGE_VARIATION)
        g = max(0, g - CAMOUFLAGE_VARIATION)
        b = max(0, b - CAMOUFLAGE_VARIATION)
    else:
        # Dark background - make text slightly lighter
        r = min(255, r + CAMOUFLAGE_VARIATION)
        g = min(255, g + CAMOUFLAGE_VARIATION)
        b = min(255, b + CAMOUFLAGE_VARIATION)
    
    return (r, g, b)


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
    background_images = params.background_images
    smart_color_picker = params.smart_color_picker
    font_size = params.font_size
    languages = params.languages
    try:
        all_langs = [x["code"] for x in argostranslate.apis.LibreTranslateAPI().languages()]
        if "all" in languages:
            languages = all_langs
        if any(l not in all_langs for l in languages):
            raise ValueError(f"Invalid lang supplied in following list: {languages}")
    except (urllib.error.HTTPError, urllib.error.URLError):
        print('Unable to reach argos server. Translating disabled.')

    

    # Hard-coded width
    width, height = (int(x) for x in params.size.split(","))
    # Create GIF frames
    frames = []

    text_array = get_trans(text, languages=languages) if text else text_array

    max_width = get_max_width(text_array, languages, font_size) if text else width

    # Load background images if provided
    bg_images = []
    if background_images:
        for img_path in background_images:
            try:
                bg_img = Image.open(img_path.strip())
                # Resize to match the target size
                bg_img = bg_img.resize((max_width, height))
                bg_images.append(bg_img)
            except Exception as e:
                print(f"Warning: Could not load background image {img_path}: {e}")
                bg_images.append(None)
        
        # Ensure we have enough background images (cycle if needed)
        if len(bg_images) < len(text_array):
            while len(bg_images) < len(text_array):
                bg_images.extend(bg_images[:len(text_array) - len(bg_images)])

    def create_image(text, font, font_color, background_color, bg_image=None):
        if bg_image:
            # Use background image
            image = bg_image.copy()
        else:
            # Use solid color background
            image = Image.new("RGB", (max_width, height), color=background_color)
        
        # Determine font color based on smart_color_picker
        actual_font_color = font_color
        if smart_color_picker:
            if bg_image:
                avg_color = get_average_color(bg_image)
            else:
                avg_color = background_color
            
            if smart_color_picker == "contrast":
                actual_font_color = get_contrasting_color(avg_color)
            elif smart_color_picker == "camouflage":
                actual_font_color = get_camouflaged_color(avg_color)
        
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font, height / 2)
        x = 0
        y = height // 8
        draw.text((x, y), text, font=font, fill=actual_font_color)
        return image

    # x= Image.new("RGB",(4,4,),color=(0,0,0,)).save()
    for idx, t in enumerate(text_array):
        bg_img = bg_images[idx] if bg_images and idx < len(bg_images) else None
        image = create_image(
            t,
            font_path,
            font_color,
            background_color,
            bg_img,
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
    parser.add_argument(
        "--background_images", nargs="+", default=None, 
        help="List of image paths to use as backgrounds, stretched to fit box size. Can cycle if fewer than languages."
    )
    parser.add_argument(
        "--smart_color_picker", choices=["contrast", "camouflage"], default=None,
        help="Automatically pick text color: 'contrast' for maximal contrast with background, 'camouflage' for minimal contrast"
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