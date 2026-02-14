import argparse
import os
import random
import glob
import json
from PIL import Image, ImageDraw, ImageFont, ImageStat
from collections import defaultdict
from typing import List

# Mapping from ISO 639-1 language codes to country folder names in picture_assets
LANG_TO_COUNTRY = {
    "en": "united_states",
    "es": "spain",
    "fr": "france",
    "de": "germany",
    "it": "italy",
    "pt": "brazil",
    "ru": "russia",
    "ja": "japan",
    "ko": "south_korea",
    "zh": "china",
    "hi": "india",
    "ar": "saudi_arabia",
    "bn": "bangladesh",
    "pa": "india",
    "jv": "indonesia",
    "te": "india",
    "vi": "vietnam",
    "mr": "india",
    "ta": "india",
    "tr": "turkey",
    "ur": "pakistan",
    "pl": "poland",
    "uk": "ukraine",
    "nl": "netherlands",
    "el": "greece",
    "th": "thailand",
    "sv": "sweden",
    "da": "denmark",
    "fi": "finland",
    "no": "norway",
    "he": "israel",
    "id": "indonesia",
    "ms": "malaysia",
    "hu": "hungary",
    "cs": "czech_republic",
    "ro": "romania",
    "sk": "slovakia",
    "bg": "bulgaria",
    "hr": "croatia",
    "sr": "serbia",
    "sl": "slovenia",
    "et": "estonia",
    "lv": "latvia",
    "lt": "lithuania",
    "fa": "iran",
    "sw": "kenya",
    "tl": "philippines",
    "is": "iceland",
    "ga": "ireland",
    "cy": "united_kingdom",
    "gd": "united_kingdom",
    "lb": "luxembourg",
    "mt": "malta",
    "sq": "albania",
    "hy": "armenia",
    "az": "azerbaijan",
    "ka": "georgia",
    "kk": "kazakhstan",
    "ky": "kyrgyzstan",
    "tg": "tajikistan",
    "tk": "turkmenistan",
    "uz": "uzbekistan",
    "mn": "mongolia",
    "bo": "china",
    "my": "myanmar",
    "km": "cambodia",
    "lo": "laos",
    "ml": "india",
    "kn": "india",
    "si": "sri_lanka",
    "ne": "nepal",
    "ps": "afghanistan",
    "ku": "iraq",
    "am": "ethiopia",
    "yo": "nigeria",
    "ig": "nigeria",
    "zu": "south_africa",
    "xh": "south_africa",
    "af": "south_africa",
    "mi": "new_zealand",
    "haw": "united_states",
    "sm": "samoa",
    "to": "tonga",
    "fj": "fiji",
    "eo": "global",
    "ca": "spain",
    "gl": "spain",
    "eu": "spain",
    "oc": "france",
    "br": "france",
    "co": "france",
    "fy": "netherlands",
    "hsb": "germany",
    "csb": "poland",
    "tt": "russia",
    "ba": "russia",
    "ce": "russia",
    "cv": "russia",
    "udm": "russia",
    "mhr": "russia",
    "sah": "russia",
    "gn": "paraguay",
    "qu": "peru",
    "ay": "bolivia",
    "nah": "mexico",
    "yua": "mexico",
}


def get_contrast_colors(image, region, default_color=None):
    """
    Calculate the best text color by inverting the average background color
    of the region for maximum difference.
    """
    if region[2] <= region[0] or region[3] <= region[1]:
        return (255, 255, 255), (0, 0, 0)

    crop = image.crop(region)
    stat = ImageStat.Stat(crop)
    avg_rgb = tuple(int(x) for x in stat.mean[:3])

    # Calculate the inverted color for maximum difference
    text_color = tuple(255 - c for c in avg_rgb)

    # For the outline/stroke, pick white or black based on text brightness
    # to ensure the text itself is readable against the inverted background.
    brightness = (
        text_color[0] * 299 + text_color[1] * 587 + text_color[2] * 114
    ) / 1000
    outline_color = (0, 0, 0) if brightness > 127 else (255, 255, 255)

    return text_color, outline_color


def get_background_image(lang_code, size, assets_dir="picture_assets"):
    """
    Find a random image for the language and resize/crop it to fill the size.
    """
    country = LANG_TO_COUNTRY.get(lang_code)
    img_path = None

    if country:
        country_dir = os.path.join(assets_dir, country)
        if os.path.exists(country_dir):
            images = glob.glob(os.path.join(country_dir, "*.*"))
            if images:
                img_path = random.choice(images)

    if not img_path:
        default_path = os.path.join(assets_dir, "global_default.jpg")
        if os.path.exists(default_path):
            img_path = default_path
        else:
            # Fallback to solid color if no image found
            return Image.new("RGB", size, (128, 128, 128))

    try:
        img = Image.open(img_path).convert("RGB")

        # Resize and center crop (Cover strategy)
        target_w, target_h = size
        img_w, img_h = img.size

        aspect_target = target_w / target_h
        aspect_img = img_w / img_h

        if aspect_img > aspect_target:
            # Image is wider than target
            new_h = target_h
            new_w = int(aspect_img * new_h)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            img = img.crop((left, 0, left + target_w, target_h))
        else:
            # Image is taller than target
            new_w = target_w
            new_h = int(new_w / aspect_img)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            top = (new_h - target_h) // 2
            img = img.crop((0, top, target_w, top + target_h))

        return img
    except Exception as e:
        print(f"Error loading image {img_path}: {e}")
        return Image.new("RGB", size, (128, 128, 128))


# Static translations for Hello and Love
def get_trans(text, languages=None):
    """
    Get hardcoded translations for "hello" and "love" from translations.json.
    If text is not recognized, return just the original text.
    """
    try:
        with open("translations.json", "r", encoding="utf-8") as f:
            static_translations = json.load(f)
    except Exception as e:
        print(f"Error loading translations: {e}")
        return [(text, "en")]

    key = text.lower().strip().strip("!").strip(".")
    if key in static_translations:
        translations = static_translations[key]
        res = []
        if (
            languages == "all"
            or languages is None
            or (isinstance(languages, list) and "all" in languages)
        ):
            # Return all available translations for this word
            for lang, trans_text in translations.items():
                res.append((trans_text, lang))
        else:
            # Return only requested languages
            if isinstance(languages, str):
                languages = [languages]

            res.append((translations.get("en", text), "en"))
            for lang in languages:
                if lang in translations and lang != "en":
                    res.append((translations[lang], lang))
        return res
    else:
        return [(text, "en")]


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


def get_actual_text_width(text, font_path, font_size):
    """
    Calculate the actual rendered width of text using PIL's textbbox
    """
    font = ImageFont.truetype(font_path, font_size)
    # Create a temporary draw object to measure text
    temp_image = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(temp_image)
    bbox = draw.textbbox((0, 0), text, font=font)
    # bbox returns (left, top, right, bottom)
    text_width = bbox[2] - bbox[0]
    return text_width


def create_gif(params):
    # PARAMS INPUT
    text = params.text
    text_array = []
    if params.text_array:
        text_array = [(t.strip(), "und") for t in params.text_array.split(",")]

    if not text and not text_array:
        raise ValueError("need text or text array")

    delay = params.delay
    sine_delay = params.sine_delay
    font_color_pref = params.font_color
    font_path = params.font_path
    background_color = params.background_color
    font_size = params.font_size
    languages = params.languages
    use_images = params.use_images

    # Hard-coded width
    width, height = (int(x) for x in params.size.split(","))

    # Get translations if text is provided
    if text:
        text_array = get_trans(text, languages=languages)

    # Calculate actual font size and width for each translation to ensure it fits
    base_font_size = font_size if font_size != 32 else height // 4
    text_configs = {}  # text -> (font_size, width)

    max_width = width

    for t, l in text_array:
        if t not in text_configs:
            f_size = base_font_size
            t_width = get_actual_text_width(t, font_path, f_size)

            # Reduce font size until it fits (with 5% padding on each side)
            while t_width > max_width * 0.9 and f_size > 8:
                f_size -= 2
                t_width = get_actual_text_width(t, font_path, f_size)

            text_configs[t] = (f_size, t_width)

    frames = []

    def create_frame(text, lang_code, font_path, default_font_color, bg_color):
        # Use the pre-calculated font size and width for this specific text
        font_size, text_width = text_configs[text]

        if use_images:
            image = get_background_image(lang_code, (max_width, height))
        else:
            image = Image.new("RGB", (max_width, height), color=bg_color)

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, font_size)

        x = max_width / 2 - text_width / 2
        y = (height - font_size) / 2  # Center vertically

        # Get actual bounding box for contrast calculation
        bbox = draw.textbbox((x, y), text, font=font)

        if use_images or params.smart_color:
            color, outline_color = get_contrast_colors(
                image, bbox, default_color=default_font_color
            )
            # Add a stroke for maximum contrast
            stroke_width = max(2, font_size // 15)
        else:
            color = default_font_color
            outline_color = None
            stroke_width = 0

        draw.text(
            (x, y),
            text,
            font=font,
            fill=color,
            stroke_width=stroke_width,
            stroke_fill=outline_color,
        )
        return image

    for t, l in text_array:
        image = create_frame(
            t,
            l,
            font_path,
            font_color_pref,
            background_color,
        )
        frames.append(image)

    if not frames:
        print("No frames created.")
        return

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
        new_frames[0].save(
            params.gif_path,
            save_all=True,
            append_images=new_frames[1:],
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
        "--use_images",
        action="store_true",
        help="Use country-specific background images",
    )
    parser.add_argument(
        "--smart_color",
        action="store_true",
        help="Automatically pick best text color based on background",
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
