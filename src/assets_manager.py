import os
import glob
import json
import random
import colorsys
from PIL import Image, ImageFont, ImageDraw
from src.utils import get_path, get_lang_sort_key, hex_to_rgb
from src.config import LANG_TO_COUNTRY, FONT_MAP

FLAG_COLORS = {}
try:
    with open(get_path("flag_colors.json"), "r") as f:
        FLAG_COLORS = json.load(f)
except:
    pass


def get_font_for_lang(lang_code, text, preferred_path):
    """Select the best font for a given language code or text content."""

    # Helper to check if text contains characters that definitely won't work with NotoSans-Regular
    def needs_special_font(t):
        for char in t:
            code = ord(char)
            if 0x0000 <= code <= 0x052F:
                continue
            if 0x1E00 <= code <= 0x1EFF:
                continue
            if 0x2000 <= code <= 0x2BFF:
                continue
            if 0x3000 <= code <= 0x303F:
                continue
            if 0xFF00 <= code <= 0xFFEF:
                continue
            return True
        return False

    if lang_code in FONT_MAP:
        font_path = get_path(FONT_MAP[lang_code])
        if os.path.exists(font_path):
            return font_path

    script_ranges = [
        ("\u0600", "\u06ff", get_path("fonts/NotoSansArabic-Regular.ttf")),
        ("\u0900", "\u097f", get_path("fonts/NotoSansDevanagari-Regular.ttf")),
        ("\u0a80", "\u0aff", get_path("fonts/NotoSansGujarati-Regular.ttf")),
        ("\u0980", "\u09ff", get_path("fonts/NotoSansBengali-Regular.ttf")),
        ("\u0a00", "\u0a7f", get_path("fonts/NotoSansGurmukhi-Regular.ttf")),
        ("\u0b80", "\u0bff", get_path("fonts/NotoSansTamil-Regular.ttf")),
        ("\u0c00", "\u0c7f", get_path("fonts/NotoSansTelugu-Regular.ttf")),
        ("\u0c80", "\u0cff", get_path("fonts/NotoSansKannada-Regular.ttf")),
        ("\u0d00", "\u0d7f", get_path("fonts/NotoSansMalayalam-Regular.ttf")),
        ("\u0d80", "\u0dff", get_path("fonts/NotoSansSinhala-Regular.ttf")),
        ("\u0e00", "\u0e7f", get_path("fonts/NotoSansThai-Regular.ttf")),
        ("\u0e80", "\u0eff", get_path("fonts/NotoSansLao-Regular.ttf")),
        ("\u0f00", "\u0fff", get_path("fonts/NotoSerifTibetan-Regular.ttf")),
        ("\u1000", "\u109f", get_path("fonts/NotoSansMyanmar-Regular.ttf")),
        ("\u10a0", "\u10ff", get_path("fonts/NotoSansGeorgian-Regular.ttf")),
        ("\u1200", "\u137f", get_path("fonts/NotoSansEthiopic-Regular.ttf")),
        ("\u0590", "\u05ff", get_path("fonts/NotoSansHebrew-Regular.ttf")),
        ("\u0530", "\u058f", get_path("fonts/NotoSansArmenian-Regular.ttf")),
        ("\u1780", "\u17ff", get_path("fonts/NotoSansKhmer-Regular.ttf")),
        ("\u4e00", "\u9fff", get_path("fonts/NotoSansSC-Regular.otf")),
        ("\u3040", "\u309f", get_path("fonts/NotoSansJP-Regular.otf")),
        ("\uac00", "\ud7af", get_path("fonts/NotoSansKR-Regular.otf")),
    ]

    for char in text:
        for start, end, f_path in script_ranges:
            if start <= char <= end:
                if os.path.exists(f_path):
                    return f_path
                break

    if (
        preferred_path
        and os.path.exists(preferred_path)
        and "NotoSans-Regular" not in preferred_path
    ):
        return preferred_path

    fallbacks = [
        get_path("fonts/NotoSans-Regular.ttf"),
        get_path("fonts/arial.ttf"),
    ]
    for fallback in fallbacks:
        if os.path.exists(fallback):
            if fallback == get_path(
                "fonts/NotoSans-Regular.ttf"
            ) and needs_special_font(text):
                continue
            return fallback

    return None


def get_background_image(lang_code, size, word="hello", used_images=None):
    """Find a random image for the language and resize/crop it to fill the size."""
    if used_images is None:
        used_images = set()

    word_clean = word.lower().strip().strip("!").strip(".")
    assets_dir = (
        get_path("hello_assets") if word_clean == "hello" else get_path("love_assets")
    )

    country = LANG_TO_COUNTRY.get(lang_code)
    img_path = None

    if country:
        country_dir = os.path.join(assets_dir, country)
        if os.path.exists(country_dir):
            images = [
                f
                for f in glob.glob(os.path.join(country_dir, "*.*"))
                if os.path.isfile(f)
            ]
            random.shuffle(images)
            for potential_path in images:
                if potential_path not in used_images:
                    try:
                        if os.path.getsize(potential_path) > 500:
                            img_path = potential_path
                            break
                    except:
                        continue

    if not img_path:
        global_dir = os.path.join(assets_dir, "global")
        if os.path.exists(global_dir):
            images = [
                f
                for f in glob.glob(os.path.join(global_dir, "*.*"))
                if os.path.isfile(f)
            ]
            unused_global = [f for f in images if f not in used_images]
            img_path = (
                random.choice(unused_global)
                if unused_global
                else (random.choice(images) if images else None)
            )

    if not img_path:
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return Image.new("RGB", size, color), f"solid_color_{color}"

    try:
        img = Image.open(img_path).convert("RGB")
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
        return Image.new("RGB", size, (128, 128, 128)), None


def get_trans(text, languages=None):
    """Get hardcoded translations for 'hello' and 'love' from translations.json."""
    try:
        with open(get_path("translations.json"), "r", encoding="utf-8") as f:
            static_translations = json.load(f)
    except:
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
            for lang, trans_text in translations.items():
                res.append((trans_text, lang))
        else:
            if isinstance(languages, str):
                languages = [languages]
            res.append((translations.get("en", text), "en"))
            for lang in languages:
                if lang in translations and lang != "en":
                    res.append((translations[lang], lang))
        res.sort(key=lambda x: get_lang_sort_key(x[1]))
        return res
    return [(text, "en")]


def get_flag_colors_for_text(text, lang_code):
    country_key = LANG_TO_COUNTRY.get(lang_code, "global")
    formatted_country = "_".join([w.capitalize() for w in country_key.split("_")])
    colors_hex = FLAG_COLORS.get(formatted_country, ["#FFFFFF"])

    n_chars = len(text)
    n_colors = len(colors_hex)
    if n_chars == 0:
        return []

    char_colors = []
    for i in range(n_chars):
        color_idx = min(int((i / n_chars) * n_colors), n_colors - 1)
        char_colors.append(hex_to_rgb(colors_hex[color_idx]))
    return char_colors


def get_rainbow_colors_for_text(text, frame_idx, total_frames):
    n_chars = len(text)
    if n_chars == 0:
        return []
    base_hue = frame_idx / total_frames
    r, g, b = colorsys.hls_to_rgb(base_hue, 0.8, 0.5)
    color = (int(r * 255), int(g * 255), int(b * 255))
    return [color] * n_chars
