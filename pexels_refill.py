import os
import json
import requests
import random
import time
from PIL import Image


import argparse


# Load API key from .1nv
def get_api_key():
    if not os.path.exists(".1nv"):
        print("Error: .1nv file not found.")
        return None
    with open(".1nv", "r") as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                key = line.split("=", 1)[1].strip()
                # Remove quotes if present
                if (key.startswith('"') and key.endswith('"')) or (
                    key.startswith("'") and key.endswith("'")
                ):
                    key = key[1:-1]
                return key
    return None


# Mapping from ISO 639-1 language codes to country folder names
# Taken from check_pictures.py
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


def get_needed_counts():
    assets_dir = "picture_assets"
    translations_file = "translations.json"

    total_needed = {}
    # Initialize with 1 for every country to ensure we have at least one fallback
    for country in set(LANG_TO_COUNTRY.values()):
        total_needed[country] = 1

    if not os.path.exists(translations_file):
        return total_needed

    with open(translations_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for word, translations in data.items():
        # Mirror the deduplication logic in mr-worldwide.py
        seen_texts = set()
        for lang, trans_text in translations.items():
            clean_t = trans_text.lower().strip()
            if clean_t not in seen_texts:
                country = LANG_TO_COUNTRY.get(lang, "global")
                total_needed[country] = total_needed.get(country, 0) + 1
                seen_texts.add(clean_t)

    return total_needed


def is_valid_image(path):
    """Check if the file is a valid image and large enough."""
    if not os.path.exists(path):
        return False
    # Increased minimum size to 10KB to avoid thumbnails/placeholders
    if os.path.getsize(path) < 10000:
        return False
    try:
        with Image.open(path) as img:
            img.load()
        return True
    except:
        return False


def get_missing_counts():
    assets_dir = "picture_assets"
    needed = get_needed_counts()

    # Clean up invalid images
    if os.path.exists(assets_dir):
        for country in os.listdir(assets_dir):
            path = os.path.join(assets_dir, country)
            if not os.path.isdir(path) or country.startswith("."):
                continue

            for f in os.listdir(path):
                if f.startswith("."):
                    continue
                full_path = os.path.join(path, f)
                if not is_valid_image(full_path):
                    print(f"Removing invalid image: {full_path}")
                    os.remove(full_path)

    missing = {}
    for country, count_needed in needed.items():
        path = os.path.join(assets_dir, country)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            missing[country] = count_needed
            continue

        valid_files = [f for f in os.listdir(path) if not f.startswith(".")]

        if len(valid_files) < count_needed:
            missing[country] = count_needed - len(valid_files)

    return missing


def download_from_pexels(country, api_key, count=1):
    print(f"Searching Pexels for {country} ({count} images needed)...")
    headers = {"Authorization": api_key}
    # Using a more restrictive query to avoid mixed-up results
    # landmark in {country} is a safe bet
    query = f"landmark in {country.replace('_', ' ')}"
    url = f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page={count}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get("photos"):
            print(f"No photos found for {country}")
            return 0

        downloaded = 0
        for photo in data["photos"]:
            img_url = photo["src"]["large2x"]

            # Determine filename
            ext = img_url.split(".")[-1].split("?")[0]
            if ext not in ["jpg", "jpeg", "png", "webp"]:
                ext = "jpg"

            filename = f"{photo['id']}.{ext}"
            print(f"ID: {photo['id']} for {country}")
            target_path = os.path.join("picture_assets", country, filename)

            if os.path.exists(target_path):
                continue

            print(f"Downloading {img_url} to {target_path}...")
            img_response = requests.get(img_url)
            img_response.raise_for_status()

            with open(target_path, "wb") as f:
                f.write(img_response.content)

            if is_valid_image(target_path):
                downloaded += 1
            else:
                print(f"Downloaded image is invalid, removing: {target_path}")
                os.remove(target_path)

        if downloaded > 0:
            # Optional: Remove dummy files if they exist
            path = os.path.join("picture_assets", country)
            for f in os.listdir(path):
                if f.startswith("dummy_"):
                    os.remove(os.path.join(path, f))
                    print(f"Removed dummy file: {f}")

        return downloaded

    except Exception as e:
        print(f"Error processing {country}: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Refill Pexels images")
    parser.add_argument(
        "--clear", action="store_true", help="Clear all existing images before refill"
    )
    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        print("Please set PEXELS_API_KEY in .1nv")
        return

    assets_dir = "picture_assets"
    if args.clear and os.path.exists(assets_dir):
        print("Clearing all existing images...")
        for country in os.listdir(assets_dir):
            country_path = os.path.join(assets_dir, country)
            if os.path.isdir(country_path):
                for f in os.listdir(country_path):
                    if not f.startswith("."):
                        os.remove(os.path.join(country_path, f))

    missing = get_missing_counts()
    print(f"Needed counts: {get_needed_counts()}")
    if not missing:
        print("No missing backgrounds found.")
        return

    print(
        f"Found {len(missing)} countries needing refills: {', '.join(f'{k}:{v}' for k, v in missing.items())}"
    )

    for country, count in missing.items():
        downloaded = download_from_pexels(country, api_key, count)
        if downloaded > 0:
            print(f"Successfully refilled {downloaded} images for {country}")
            time.sleep(1)  # Be respectful to the API
        else:
            print(f"Failed to refill {country}")


if __name__ == "__main__":
    main()
