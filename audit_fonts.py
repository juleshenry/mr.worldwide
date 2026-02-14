import json
import os


def check_fonts_for_translations():
    with open("translations.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    all_langs = set()
    for word in data:
        for lang in data[word]:
            all_langs.add(lang)

    print(f"Total languages in translations.json: {len(all_langs)}")
    print(f"Languages: {sorted(list(all_langs))}")

    # Mapping from mr-worldwide.py (current state)
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

    missing_map = []
    missing_file = []

    # Common Latin/Cyrillic/Greek usually handled by NotoSans-Regular
    latin_greek_cyrillic = {
        "en",
        "es",
        "fr",
        "de",
        "it",
        "pt",
        "ru",
        "pl",
        "uk",
        "nl",
        "el",
        "sv",
        "da",
        "fi",
        "no",
        "id",
        "ms",
        "hu",
        "cs",
        "ro",
        "sk",
        "bg",
        "hr",
        "sr",
        "sl",
        "et",
        "lv",
        "lt",
        "sw",
        "tl",
        "is",
        "ga",
        "cy",
        "gd",
        "lb",
        "mt",
        "sq",
        "az",
        "kk",
        "ky",
        "tg",
        "tk",
        "uz",
        "mn",
        "yo",
        "ig",
        "zu",
        "xh",
        "af",
        "mi",
        "haw",
        "sm",
        "to",
        "fj",
        "eo",
        "ca",
        "gl",
        "eu",
        "oc",
        "br",
        "co",
        "fy",
        "hsb",
        "csb",
        "tt",
        "ba",
        "ce",
        "cv",
        "udm",
        "mhr",
        "sah",
        "gn",
        "qu",
        "ay",
        "nah",
        "yua",
        "jv",
    }

    for lang in all_langs:
        if lang in latin_greek_cyrillic:
            continue
        if lang not in FONT_MAP:
            missing_map.append(lang)
        elif not os.path.exists(FONT_MAP[lang]):
            missing_file.append((lang, FONT_MAP[lang]))

    print(
        f"\nLanguages not in FONT_MAP and not in Latin/Cyrillic/Greek list: {missing_map}"
    )
    print(f"\nLanguages in FONT_MAP but file is missing: {missing_file}")


if __name__ == "__main__":
    check_fonts_for_translations()
