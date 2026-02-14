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

# Mapping from ISO 639-1 language codes to country folder names in icon_assets
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
    "ga": "republic_of_ireland",
    "cy": "united_kingdom",
    "gd": "united_kingdom",
    "lb": "luxembourg",
    "mt": "malta",
    "sq": "albania",
    "hy": "armenia",
    "az": "azerbaijan",
    "ka": "armenia",  # Fallback for Georgia which is missing
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
    "eo": "esperanto",
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

# Regional mapping for ordering
COUNTRY_TO_REGION = {
    "spain": "Europe",
    "france": "Europe",
    "germany": "Europe",
    "italy": "Europe",
    "poland": "Europe",
    "ukraine": "Europe",
    "netherlands": "Europe",
    "greece": "Europe",
    "sweden": "Europe",
    "denmark": "Europe",
    "finland": "Europe",
    "norway": "Europe",
    "hungary": "Europe",
    "czech_republic": "Europe",
    "romania": "Europe",
    "slovakia": "Europe",
    "bulgaria": "Europe",
    "croatia": "Europe",
    "serbia": "Europe",
    "slovenia": "Europe",
    "estonia": "Europe",
    "latvia": "Europe",
    "lithuania": "Europe",
    "iceland": "Europe",
    "republic_of_ireland": "Europe",
    "united_kingdom": "Europe",
    "luxembourg": "Europe",
    "malta": "Europe",
    "albania": "Europe",
    "armenia": "Europe",
    "azerbaijan": "Europe",
    "georgia": "Europe",
    "russia": "Europe",
    "japan": "Asia",
    "south_korea": "Asia",
    "china": "Asia",
    "india": "Asia",
    "saudi_arabia": "Asia",
    "bangladesh": "Asia",
    "indonesia": "Asia",
    "vietnam": "Asia",
    "turkey": "Asia",
    "pakistan": "Asia",
    "thailand": "Asia",
    "israel": "Asia",
    "malaysia": "Asia",
    "iran": "Asia",
    "philippines": "Asia",
    "kazakhstan": "Asia",
    "kyrgyzstan": "Asia",
    "tajikistan": "Asia",
    "turkmenistan": "Asia",
    "uzbekistan": "Asia",
    "mongolia": "Asia",
    "myanmar": "Asia",
    "cambodia": "Asia",
    "laos": "Asia",
    "sri_lanka": "Asia",
    "nepal": "Asia",
    "afghanistan": "Asia",
    "iraq": "Asia",
    "kenya": "Africa",
    "ethiopia": "Africa",
    "nigeria": "Africa",
    "south_africa": "Africa",
    "united_states": "North America",
    "mexico": "North America",
    "brazil": "South America",
    "paraguay": "South America",
    "peru": "South America",
    "bolivia": "South America",
    "new_zealand": "Oceania",
    "samoa": "Oceania",
    "tonga": "Oceania",
    "fiji": "Oceania",
    "esperanto": "Global",
    "global": "Global",
}

REGION_ORDER = [
    "Europe",
    "Asia",
    "Africa",
    "North America",
    "South America",
    "Oceania",
    "Global",
]


def get_lang_sort_key(lang_code):
    """Returns a sort key based on regional ordering."""
    country = LANG_TO_COUNTRY.get(lang_code, "global")
    region = COUNTRY_TO_REGION.get(country, "Global")
    try:
        region_idx = REGION_ORDER.index(region)
    except ValueError:
        region_idx = len(REGION_ORDER)
    return (region_idx, lang_code)


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


def country_to_eponym(country):
    eponyms = {
        "united_states": "american",
        "spain": "spanish",
        "france": "french",
        "germany": "german",
        "italy": "italian",
        "brazil": "brazilian",
        "russia": "russian",
        "japan": "japanese",
        "south_korea": "korean",
        "china": "chinese",
        "india": "indian",
        "saudi_arabia": "saudi",
        "bangladesh": "bangladeshi",
        "indonesia": "indonesian",
        "vietnam": "vietnamese",
        "turkey": "turkish",
        "pakistan": "pakistani",
        "poland": "polish",
        "ukraine": "ukrainian",
        "netherlands": "dutch",
        "greece": "greek",
        "thailand": "thai",
        "sweden": "swedish",
        "denmark": "danish",
        "finland": "finnish",
        "norway": "norwegian",
        "israel": "israeli",
        "malaysia": "malaysian",
        "hungary": "hungarian",
        "czech_republic": "czech",
        "romania": "romanian",
        "slovakia": "slovak",
        "bulgaria": "bulgarian",
        "croatia": "croatian",
        "serbia": "serbian",
        "slovenia": "slovenian",
        "estonia": "estonian",
        "latvia": "latvian",
        "lithuania": "lithuanian",
        "iran": "iranian",
        "kenya": "kenyan",
        "philippines": "filipino",
        "iceland": "icelandic",
        "ireland": "irish",
        "republic_of_ireland": "irish",
        "united_kingdom": "british",
        "luxembourg": "luxembourgish",
        "malta": "maltese",
        "albania": "albanian",
        "armenia": "armenian",
        "azerbaijan": "azerbaijani",
        "georgia": "georgian",
        "kazakhstan": "kazakh",
        "kyrgyzstan": "kyrgyz",
        "tajikistan": "tajik",
        "turkmenistan": "turkmen",
        "uzbekistan": "uzbek",
        "mongolia": "mongolian",
        "myanmar": "burmese",
        "cambodia": "cambodian",
        "laos": "laotian",
        "sri_lanka": "sri lankan",
        "nepal": "nepalese",
        "afghanistan": "afghan",
        "iraq": "iraqi",
        "ethiopia": "ethiopian",
        "nigeria": "nigerian",
        "south_africa": "south african",
        "new_zealand": "new zealander",
        "samoa": "samoan",
        "tonga": "tongan",
        "fiji": "fijian",
        "paraguay": "paraguayan",
        "peru": "peruvian",
        "bolivia": "bolivian",
        "mexico": "mexican",
    }
    return eponyms.get(country, country)


def get_background_image(lang_code, size, word="hello", used_images=None):
    """
    Find a random image for the language and resize/crop it to fill the size.
    Ensures that the same image is NEVER repeated by moving used images to a .used folder.
    """
    if used_images is None:
        used_images = set()

    # Use hello_assets for 'hello', love_assets for 'love'
    word_clean = word.lower().strip().strip("!").strip(".")
    if word_clean == "hello":
        assets_dir = "hello_assets"
    elif word_clean == "love":
        assets_dir = "love_assets"
    else:
        # Fallback to icon_assets or one of the new ones
        assets_dir = "love_assets"

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
FLAG_COLORS = {}
try:
    with open("flag_colors.json", "r") as f:
        FLAG_COLORS = json.load(f)
except:
    pass


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c * 2 for c in hex_str])
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def get_flag_colors_for_text(text, lang_code):
    country_key = LANG_TO_COUNTRY.get(lang_code, "global")
    # Normalize country_key to match flag_colors.json (e.g. "united_states" -> "United_States")
    formatted_country = "_".join([w.capitalize() for w in country_key.split("_")])

    colors_hex = FLAG_COLORS.get(formatted_country)
    if not colors_hex:
        # Fallback to some defaults if country not found
        colors_hex = ["#FFFFFF"]

    # Map colors to characters
    n_chars = len(text)
    n_colors = len(colors_hex)
    char_colors = []
    if n_chars == 0:
        return []

    for i in range(n_chars):
        color_idx = min(int((i / n_chars) * n_colors), n_colors - 1)
        char_colors.append(hex_to_rgb(colors_hex[color_idx]))
    return char_colors


def get_rainbow_colors_for_text(text, frame_idx, total_frames):
    n_chars = len(text)
    char_colors = []
    if n_chars == 0:
        return []

    # Use frame_idx to shift the hue for each page/translation
    base_hue = frame_idx / total_frames

    # Generate pastel color: high lightness (0.7-0.8) and moderate saturation (0.4-0.6)
    r, g, b = colorsys.hls_to_rgb(base_hue, 0.8, 0.5)
    color = (int(r * 255), int(g * 255), int(b * 255))

    return [color] * n_chars


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

        # Sort results based on regional ordering
        res.sort(key=lambda x: get_lang_sort_key(x[1]))
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
        "zh": "fonts/NotoSansSC-Regular.otf",
        "ja": "fonts/NotoSansJP-Regular.otf",
        "ko": "fonts/NotoSansKR-Regular.otf",
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
        "bo": "fonts/NotoSerifTibetan-Regular.ttf",
        "gu": "fonts/NotoSansGujarati-Regular.ttf",
    }

    # Helper to check if text contains characters that definitely won't work with NotoSans-Regular
    def needs_special_font(t):
        for char in t:
            code = ord(char)
            # Standard Latin, Greek, Cyrillic
            if 0x0000 <= code <= 0x052F:
                continue
            # Vietnamese / Latin Extended Additional
            if 0x1E00 <= code <= 0x1EFF:
                continue
            # General Punctuation, Currency, Symbols
            if 0x2000 <= code <= 0x2BFF:
                continue
            # CJK Symbols and Punctuation
            if 0x3000 <= code <= 0x303F:
                continue
            # Fullwidth Forms
            if 0xFF00 <= code <= 0xFFEF:
                continue

            # If it's outside these, it might need a specific Noto font
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
        ("\u0a80", "\u0aff", "fonts/NotoSansGujarati-Regular.ttf"),
        ("\u0980", "\u09ff", "fonts/NotoSansBengali-Regular.ttf"),
        ("\u0a00", "\u0a7f", "fonts/NotoSansGurmukhi-Regular.ttf"),
        ("\u0b80", "\u0bff", "fonts/NotoSansTamil-Regular.ttf"),
        ("\u0c00", "\u0c7f", "fonts/NotoSansTelugu-Regular.ttf"),
        ("\u0c80", "\u0cff", "fonts/NotoSansKannada-Regular.ttf"),
        ("\u0d00", "\u0d7f", "fonts/NotoSansMalayalam-Regular.ttf"),
        ("\u0d80", "\u0dff", "fonts/NotoSansSinhala-Regular.ttf"),
        ("\u0e00", "\u0e7f", "fonts/NotoSansThai-Regular.ttf"),
        ("\u0e80", "\u0eff", "fonts/NotoSansLao-Regular.ttf"),
        ("\u0f00", "\u0fff", "fonts/NotoSerifTibetan-Regular.ttf"),
        ("\u1000", "\u109f", "fonts/NotoSansMyanmar-Regular.ttf"),
        ("\u10a0", "\u10ff", "fonts/NotoSansGeorgian-Regular.ttf"),
        ("\u1200", "\u137f", "fonts/NotoSansEthiopic-Regular.ttf"),
        ("\u0590", "\u05ff", "fonts/NotoSansHebrew-Regular.ttf"),
        ("\u0530", "\u058f", "fonts/NotoSansArmenian-Regular.ttf"),
        ("\u1780", "\u17ff", "fonts/NotoSansKhmer-Regular.ttf"),
        # CJK
        ("\u4e00", "\u9fff", "fonts/NotoSansSC-Regular.otf"),
        ("\u3400", "\u4dbf", "fonts/NotoSansSC-Regular.otf"),
        ("\u3040", "\u309f", "fonts/NotoSansJP-Regular.otf"),
        ("\u30a0", "\u30ff", "fonts/NotoSansJP-Regular.otf"),
        ("\uac00", "\ud7af", "fonts/NotoSansKR-Regular.otf"),
        ("\u3000", "\u303f", "fonts/NotoSansSC-Regular.otf"),
        ("\uff00", "\uffef", "fonts/NotoSansSC-Regular.otf"),
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


def get_actual_text_width(
    text, lang_code, preferred_font_path, font_size, char_by_char=False
):
    """
    Calculate the actual rendered width of text using PIL's textbbox or textlength.
    Returns (width, bbox_left, bbox_right).
    Returns (0, 0, 0) if no font is found.
    """
    font_path = get_font_for_lang(lang_code, text, preferred_font_path)
    if not font_path:
        return 0, 0, 0
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError as e:
        print(f"Error loading font: {font_path} for text '{text}' ({lang_code})")
        raise e

    # Create a temporary draw object to measure text
    temp_image = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(temp_image)

    if char_by_char:
        if not text:
            return 0, 0, 0
        # Sum of individual character lengths (as used in character-by-character rendering)
        # We need to calculate the actual ink bounds
        w_advance = 0
        b_left = 0
        b_right = 0
        for i, char in enumerate(text):
            char_bbox = draw.textbbox((w_advance, 0), char, font=font)
            if i == 0:
                b_left = char_bbox[0]
            if i == len(text) - 1:
                b_right = char_bbox[2]
            w_advance += draw.textlength(char, font=font)

        return b_right - b_left, b_left, b_right
    else:
        bbox = draw.textbbox((0, 0), text, font=font)
        # bbox returns (left, top, right, bottom)
        text_width = bbox[2] - bbox[0]
        return text_width, bbox[0], bbox[2]


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
    use_icons = params.use_icons

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
            t_width, b_left, b_right = get_actual_text_width(
                t,
                l,
                font_path,
                f_size,
                char_by_char=params.use_flag_colors or params.rainbow,
            )

            # If text cannot be rendered at all, mark it to be skipped
            if t_width == 0 and t.strip():
                text_configs[config_key] = (0, 0, 0, 0)
                continue

            # Reduce font size until it fits (with 5% padding on each side)
            while t_width > max_width * 0.9 and f_size > 8:
                f_size -= 2
                t_width, b_left, b_right = get_actual_text_width(
                    t,
                    l,
                    font_path,
                    f_size,
                    char_by_char=params.use_flag_colors or params.rainbow,
                )

            text_configs[config_key] = (f_size, t_width, b_left, b_right)

    frames = []
    used_images_paths = set()

    def create_frame(
        text,
        lang_code,
        preferred_font_path,
        default_font_color,
        bg_color,
        frame_idx,
        total_frames,
    ):
        # Use the pre-calculated font size and width for this specific text and language
        font_size, text_width, b_left, b_right = text_configs[(text, lang_code)]

        if use_icons:
            image, img_path = get_background_image(
                lang_code,
                (max_width, height),
                word=params.text or "hello",
                used_images=used_images_paths,
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

        # Center both the origin and the ink
        x = (max_width - (b_left + b_right)) / 2
        y = (height - font_size) / 2  # Center vertically

        # Get actual bounding box for contrast calculation
        bbox = draw.textbbox((x, y), text, font=font)

        if params.use_flag_colors or params.rainbow:
            if params.rainbow:
                char_colors = get_rainbow_colors_for_text(text, frame_idx, total_frames)
            else:
                char_colors = get_flag_colors_for_text(text, lang_code)

            # For multi-color text, we still want a stroke for contrast if background is complex
            if use_icons or params.smart_color:
                _, outline_color = get_contrast_colors(
                    image, bbox, default_color=default_font_color
                )
                stroke_width = max(2, font_size // 15)
            else:
                outline_color = None
                stroke_width = 0

            # Draw character by character for simplicity in splitting colors
            current_x = x
            for i, char in enumerate(text):
                char_color = char_colors[i % len(char_colors)]
                draw.text(
                    (current_x, y),
                    char,
                    font=font,
                    fill=char_color,
                    stroke_width=stroke_width,
                    stroke_fill=outline_color,
                )
                # Advance x
                char_w = draw.textlength(char, font=font)
                current_x += char_w
        else:
            if use_icons or params.smart_color:
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

    for i, (t, l) in enumerate(text_array):
        if text_configs[(t, l)][1] == 0 and t.strip():
            print(f"Skipping frame for '{t}' ({l}): No suitable font found.")
            continue
        image = create_frame(
            t,
            l,
            font_path,
            font_color_pref,
            background_color,
            i,
            len(text_array),
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
        "--use_icons",
        "--use_icons",
        action="store_true",
        help="Use country-specific icon background images",
    )
    parser.add_argument(
        "--smart_color",
        action="store_true",
        help="Automatically pick best text color based on background",
    )
    parser.add_argument(
        "--use_flag_colors",
        action="store_true",
        help="Use colors from the country flag for the text",
    )
    parser.add_argument(
        "--rainbow",
        action="store_true",
        help="Use rainbow colors for the text",
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
