import os
from src.config import PRIORITY_LANGS, LANG_TO_COUNTRY, COUNTRY_TO_REGION, REGION_ORDER

# Get the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_path(path):
    """Returns the absolute path to a file or directory relative to the project root."""
    return os.path.join(ROOT_DIR, path)


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c * 2 for c in hex_str])
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def get_lang_sort_key(lang_code):
    """Returns a sort key based on regional ordering and priority languages."""
    try:
        priority_idx = PRIORITY_LANGS.index(lang_code)
    except ValueError:
        priority_idx = len(PRIORITY_LANGS)

    country = LANG_TO_COUNTRY.get(lang_code, "global")
    region = COUNTRY_TO_REGION.get(country, "Global")
    try:
        region_idx = REGION_ORDER.index(region)
    except ValueError:
        region_idx = len(REGION_ORDER)

    return (priority_idx, region_idx, lang_code)


def sine_adder(f, d):
    """Adds 'stay' frames to each index in a loop to create a sine-like focus effect."""
    nf = []
    for robin in range(len(f)):
        for pre in f[0:robin]:
            nf.append(pre)
        for _ in range(d):
            nf.append(f[robin])
        for post in f[robin + 1 :]:
            nf.append(post)
    return nf
