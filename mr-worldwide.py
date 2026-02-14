import argparse
import os
import random
import glob
import json
import time
import shutil
import numpy as np
import colorsys
from scipy.cluster.vq import kmeans, vq
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
    Calculate the best text color by inverting or complementing the dominant
    background color for maximum contrast.
    """
    if region[2] <= region[0] or region[3] <= region[1]:
        return (255, 255, 255), (0, 0, 0)

    crop = image.crop(region).convert("RGB")
    small_crop = crop.copy()
    small_crop.thumbnail((32, 32))
    ar = np.asarray(small_crop)
    pixels = ar.reshape(-1, 3).astype(float)

    # Strategy: Find a color that maximizes contrast against ALL major background colors
    try:
        codes, _ = kmeans(pixels, 3)
        vecs, _ = vq(pixels, codes)
        counts, _ = np.histogram(vecs, bins=range(len(codes) + 1))
        # Sort codes by frequency
        sorted_indices = np.argsort(counts)[::-1]
        bg_colors = [colorsys.rgb_to_hls(*(codes[i] / 255.0)) for i in sorted_indices]
        bg_weights = [counts[i] / len(pixels) for i in sorted_indices]
    except:
        stat = ImageStat.Stat(crop)
        bg_colors = [colorsys.rgb_to_hls(*(np.array(stat.mean[:3]) / 255.0))]
        bg_weights = [1.0]

    # Weighted mean lightness to decide if we want a light or dark text
    avg_l = sum(c[1] * w for c, w in zip(bg_colors, bg_weights))

    # Target lightness with a bit of variation but high contrast
    if avg_l > 0.5:
        target_l = 0.15  # Dark text for light background
    else:
        target_l = 0.85  # Light text for dark background

    best_h = 0
    max_score = -1

    # Test 36 different hues to find the one that stands out most
    for i in range(36):
        test_h = i / 36.0

        # We want to maximize the distance from all dominant background hues,
        # weighted by how saturated and how dominant those background colors are.
        score = 0
        for (bh, bl, bs), weight in zip(bg_colors, bg_weights):
            if bs > 0.1:
                # Circular hue distance (0 to 1)
                h_dist = min(abs(test_h - bh), 1.0 - abs(test_h - bh)) * 2.0
                # Square the distance to heavily penalize very close colors
                score += (h_dist**2) * weight * bs
            else:
                # For neutral backgrounds, any hue is fine, but we prefer "warm" or "cool"
                # over muddy colors. Let's just give it a neutral boost.
                score += weight * 0.5

        # Prefer "vibrant" colors (Yellow, Cyan, Magenta, Red) over others
        # Yellow is ~0.16, Cyan is ~0.5, Magenta is ~0.83, Red is 0.0
        # This helps pick "pleasing" colors when multiple hues are equally far.
        vibrancy_bonus = 0
        for v_h in [0.0, 0.16, 0.33, 0.5, 0.66, 0.83]:
            v_dist = min(abs(test_h - v_h), 1.0 - abs(test_h - v_h)) * 2.0
            if v_dist < 0.1:
                vibrancy_bonus = 0.1

        final_score = score + vibrancy_bonus

        if final_score > max_score:
            max_score = final_score
            best_h = test_h

    # Final color: Best hue found, consistently high saturation
    new_h = best_h
    new_s = 0.95
    new_l = target_l

    tr, tg, tb = colorsys.hls_to_rgb(new_h, new_l, new_s)
    text_rgb = (int(tr * 255), int(tg * 255), int(tb * 255))

    # Calculate final brightness for the stroke
    text_brightness = (text_rgb[0] * 299 + text_rgb[1] * 587 + text_rgb[2] * 114) / 1000
    outline_color = (0, 0, 0) if text_brightness > 127 else (255, 255, 255)

    return text_rgb, outline_color


def get_background_image(
    lang_code, size, used_images=None, assets_dir="picture_assets"
):
    """
    Find a random image for the language and resize/crop it to fill the size.
    Ensures that the same image is NEVER repeated by moving used images to a .used folder.
    """
    if used_images is None:
        used_images = set()

    country = LANG_TO_COUNTRY.get(lang_code)
    img_path = None

    if country:
        country_dir = os.path.join(assets_dir, country)
        if not os.path.exists(country_dir):
            os.makedirs(country_dir, exist_ok=True)

        # Only pick files that are not in the .used directory (which is handled by glob being in country_dir)
        images = glob.glob(os.path.join(country_dir, "*.*"))
        # Filter out directories just in case
        images = [f for f in images if os.path.isfile(f)]
        random.shuffle(images)

        # Try to find an image that is unused in this session
        for potential_path in images:
            if potential_path in used_images:
                continue
            try:
                if os.path.getsize(potential_path) < 500:
                    continue
                img_path = potential_path
                break
            except:
                continue

    if not img_path:
        # Check global directory for a fallback
        global_dir = os.path.join(assets_dir, "global")
        if os.path.exists(global_dir):
            images = glob.glob(os.path.join(global_dir, "*.*"))
            images = [f for f in images if os.path.isfile(f)]
            unused_global = [f for f in images if f not in used_images]
            if unused_global:
                img_path = random.choice(unused_global)
            elif images:
                img_path = random.choice(images)

    if not img_path:
        # Final fallback: unique solid color
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        return Image.new("RGB", size, color), f"solid_color_{color}"

    try:
        img = Image.open(img_path).convert("RGB")

        # Resize and center crop (Cover strategy)
        target_w, target_h = size
        img_w, img_h = img.size

        aspect_target = target_w / target_h
        aspect_img = img_w / img_h

        if aspect_img > aspect_target:
            new_h = target_h
            new_w = int(aspect_img * new_h)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            img = img.crop((left, 0, left + target_w, target_h))
        else:
            new_w = target_w
            new_h = int(new_w / aspect_img)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            top = (new_h - target_h) // 2
            img = img.crop((0, top, target_w, top + target_h))

        return img, img_path
    except Exception as e:
        print(f"Error loading image {img_path}: {e}")
        return Image.new("RGB", size, (128, 128, 128)), None


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


def get_font_for_lang(lang_code, text, preferred_path):
    """
    Select the best font for a given language code or text content.
    Returns the font path if a suitable one is found and exists, else None.
    """
    # Mapping of language codes to specific Noto fonts
    FONT_MAP = {
        "zh": "fonts/noto-sc.ttf",
        "ja": "fonts/noto-sc.ttf",
        "ko": "fonts/noto-sc.ttf",
        "my": "fonts/NotoSansMyanmar-Regular.ttf",
        "hi": "fonts/NotoSansDevanagari-Regular.ttf",
        "mr": "fonts/NotoSansDevanagari-Regular.ttf",
        "ne": "fonts/NotoSansDevanagari-Regular.ttf",
        "ar": "fonts/NotoSansArabic-Regular.ttf",
        "ur": "fonts/NotoSansArabic-Regular.ttf",
        "fa": "fonts/NotoSansArabic-Regular.ttf",
        "ps": "fonts/NotoSansArabic-Regular.ttf",
        "bn": "fonts/NotoSansBengali-Regular.ttf",
        "th": "fonts/NotoSansThai-Regular.ttf",
        "he": "fonts/NotoSansHebrew-Regular.ttf",
        "ta": "fonts/NotoSansTamil-Regular.ttf",
        "te": "fonts/NotoSansTelugu-Regular.ttf",
        "pa": "fonts/NotoSansGurmukhi-Regular.ttf",
        "kn": "fonts/NotoSansKannada-Regular.ttf",
        "ml": "fonts/NotoSansMalayalam-Regular.ttf",
        "si": "fonts/NotoSansSinhala-Regular.ttf",
        "km": "fonts/NotoSansKhmer-Regular.ttf",
        "lo": "fonts/NotoSansLao-Regular.ttf",
        "am": "fonts/NotoSansEthiopic-Regular.ttf",
        "hy": "fonts/NotoSansArmenian-Regular.ttf",
        "ka": "fonts/NotoSansGeorgian-Regular.ttf",
        "bo": "fonts/NotoSansTibetan-Regular.ttf",
    }

    # Helper to check if text contains characters that definitely won't work with NotoSans-Regular
    def needs_special_font(t):
        for char in t:
            code = ord(char)
            # Basic Latin, Cyrillic, Greek are usually okay in NotoSans-Regular
            if code > 0x052F:  # Past Cyrillic
                # Skip common punctuation/symbols
                if 0x2000 <= code <= 0x206F:
                    continue
                return True
        return False

    # 1. Try explicit mapping
    if lang_code in FONT_MAP:
        font_path = FONT_MAP[lang_code]
        if os.path.exists(font_path):
            return font_path

    # 2. Detection logic for characters if mapping failed or wasn't there
    script_ranges = [
        ("\u0600", "\u06ff", "fonts/NotoSansArabic-Regular.ttf"),
        ("\u0900", "\u097f", "fonts/NotoSansDevanagari-Regular.ttf"),
        ("\u0980", "\u09ff", "fonts/NotoSansBengali-Regular.ttf"),
        ("\u0a00", "\u0a7f", "fonts/NotoSansGurmukhi-Regular.ttf"),
        ("\u0b80", "\u0bff", "fonts/NotoSansTamil-Regular.ttf"),
        ("\u0c00", "\u0c7f", "fonts/NotoSansTelugu-Regular.ttf"),
        ("\u0c80", "\u0cff", "fonts/NotoSansKannada-Regular.ttf"),
        ("\u0d00", "\u0d7f", "fonts/NotoSansMalayalam-Regular.ttf"),
        ("\u0d80", "\u0dff", "fonts/NotoSansSinhala-Regular.ttf"),
        ("\u0e00", "\u0e7f", "fonts/NotoSansThai-Regular.ttf"),
        ("\u0e80", "\u0eff", "fonts/NotoSansLao-Regular.ttf"),
        ("\u0f00", "\u0fff", "fonts/NotoSansTibetan-Regular.ttf"),
        ("\u1000", "\u109f", "fonts/NotoSansMyanmar-Regular.ttf"),
        ("\u10a0", "\u10ff", "fonts/NotoSansGeorgian-Regular.ttf"),
        ("\u1200", "\u137f", "fonts/NotoSansEthiopic-Regular.ttf"),
        ("\u0590", "\u05ff", "fonts/NotoSansHebrew-Regular.ttf"),
        ("\u0530", "\u058f", "fonts/NotoSansArmenian-Regular.ttf"),
        ("\u1780", "\u17ff", "fonts/NotoSansKhmer-Regular.ttf"),
        ("\u4e00", "\u9fff", "fonts/noto-sc.ttf"),
        ("\u3040", "\u309f", "fonts/noto-sc.ttf"),
        ("\u30a0", "\u30ff", "fonts/noto-sc.ttf"),
        ("\uac00", "\ud7af", "fonts/noto-sc.ttf"),
    ]

    for char in text:
        for start, end, f_path in script_ranges:
            if start <= char <= end:
                if os.path.exists(f_path):
                    return f_path
                break  # Found the range but font is missing, keep looking at other chars or move to fallbacks

    # 3. Check preferred_path if it's NOT a default and exists
    if (
        preferred_path
        and preferred_path
        not in [
            "fonts/arial.ttf",
            "fonts/NotoSans-Regular.ttf",
        ]
        and os.path.exists(preferred_path)
    ):
        return preferred_path

    # 4. Fallbacks
    fallbacks = [
        "fonts/NotoSans-Regular.ttf",
        "fonts/arial.ttf",
        "fonts/Quivira-A8VL.ttf",
    ]
    for fallback in fallbacks:
        if os.path.exists(fallback):
            # If we're falling back to NotoSans-Regular, make sure it can actually handle the text
            if fallback == "fonts/NotoSans-Regular.ttf" and needs_special_font(text):
                continue
            return fallback

    return None


def get_actual_text_width(text, lang_code, preferred_font_path, font_size):
    """
    Calculate the actual rendered width of text using PIL's textbbox.
    Returns 0 if no font is found.
    """
    font_path = get_font_for_lang(lang_code, text, preferred_font_path)
    if not font_path:
        return 0
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

    # Deduplicate and handle "same text in a row"
    unique_text_array = []
    seen_texts = set()
    for t, l in text_array:
        clean_t = t.lower().strip()
        if clean_t not in seen_texts:
            unique_text_array.append((t, l))
            seen_texts.add(clean_t)
    text_array = unique_text_array

    # Calculate actual font size and width for each translation to ensure it fits
    base_font_size = font_size if font_size != 32 else height // 4
    text_configs = {}  # text -> (font_size, width)

    max_width = width

    for t, l in text_array:
        # Use a key that includes both text and language code for configurations
        config_key = (t, l)
        if config_key not in text_configs:
            f_size = base_font_size
            t_width = get_actual_text_width(t, l, font_path, f_size)

            # If text cannot be rendered at all, mark it to be skipped
            if t_width == 0 and t.strip():
                text_configs[config_key] = (0, 0)
                continue

            # Reduce font size until it fits (with 5% padding on each side)
            while t_width > max_width * 0.9 and f_size > 8:
                f_size -= 2
                t_width = get_actual_text_width(t, l, font_path, f_size)

            text_configs[config_key] = (f_size, t_width)

    frames = []
    used_images_paths = set()

    def create_frame(
        text, lang_code, preferred_font_path, default_font_color, bg_color
    ):
        # Use the pre-calculated font size and width for this specific text and language
        font_size, text_width = text_configs[(text, lang_code)]

        if use_images:
            image, img_path = get_background_image(
                lang_code, (max_width, height), used_images=used_images_paths
            )
            if img_path:
                used_images_paths.add(img_path)
        else:
            image = Image.new("RGB", (max_width, height), color=bg_color)

        draw = ImageDraw.Draw(image)
        actual_font_path = get_font_for_lang(lang_code, text, preferred_font_path)
        if not actual_font_path:
            # Fallback to a very basic render or skip (should have been skipped already)
            return image

        font = ImageFont.truetype(actual_font_path, font_size)

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
        if text_configs[(t, l)][1] == 0 and t.strip():
            print(f"Skipping frame for '{t}' ({l}): No suitable font found.")
            continue
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
        "--font_color", type=str, default="255,255,255", help="Font color (R,G,B)"
    )
    parser.add_argument(
        "--font_path",
        default="fonts/NotoSans-Regular.ttf",
        help="Path to the font file",
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
