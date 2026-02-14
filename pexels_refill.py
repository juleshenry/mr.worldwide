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


def get_needed_counts(word):
    translations_file = "translations.json"

    total_needed = {}
    # Initialize with 1 for every country to ensure we have at least one fallback
    for country in set(LANG_TO_COUNTRY.values()):
        total_needed[country] = 1

    if not os.path.exists(translations_file):
        return total_needed

    with open(translations_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if word in data:
        translations = data[word]
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


def get_missing_counts(word):
    assets_dir = f"{word}_assets"
    needed = get_needed_counts(word)

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


def is_duplicate_globally(assets_dir, filename):
    """Check if the filename exists anywhere in the assets_dir."""
    for root, dirs, files in os.walk(assets_dir):
        if filename in files:
            return True
    return False


def download_from_pexels(country, api_key, word="hello", count=1):
    print(f"Searching Pexels for {word} in {country} ({count} images needed)...")
    headers = {"Authorization": api_key}

    country_name = country.replace("_", " ")
    eponym = country_to_eponym(country)

    if word.lower() == "hello":
        # More specific queries to avoid generic cultural heritage results
        queries = [
            f"{country_name} landmarks",
            f"{country_name} culture",
            f"{country_name} scenery",
            f"{country_name} travel",
            f"beautiful {country_name}",
            f"{country_name} architecture",
            f"{country_name} tourism",
        ]
        assets_dir = "hello_assets"
    elif word.lower() == "love":
        queries = [
            f"{eponym} couple",
            f"romance {country_name}",
            f"love {country_name}",
            f"{eponym} romance",
            f"romantic {country_name}",
        ]
        assets_dir = "love_assets"
    else:
        queries = [
            country_name,
            f"{country_name} landscape",
            f"{country_name} city",
            f"{country_name} nature",
            f"{country_name} travel",
        ]
        assets_dir = "icon_assets"

    # Randomize query order to avoid same first results
    random.shuffle(queries)

    # Request max images per page to maximize variety
    search_count = 80

    downloaded = 0
    for query in queries:
        if downloaded >= count:
            break

        # Try a random page to avoid getting the same "bad" images
        page = random.randint(1, 5)
        url = f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page={search_count}&page={page}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # If the random page is empty, try page 1
            if not data.get("photos") and page > 1:
                print(f"Page {page} empty for '{query}', trying page 1...")
                url = f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page={search_count}&page=1"
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

            if not data.get("photos"):
                continue

            # Shuffle photos to avoid always picking the first one
            photos = data["photos"]
            random.shuffle(photos)

            for photo in photos:
                if downloaded >= count:
                    break

                img_url = photo["src"]["large2x"]

                # Determine filename
                ext = img_url.split(".")[-1].split("?")[0]
                if ext not in ["jpg", "jpeg", "png", "webp"]:
                    ext = "jpg"

                filename = f"{photo['id']}.{ext}"

                # Check for duplicates locally and globally
                if is_duplicate_globally(assets_dir, filename):
                    continue

                target_path = os.path.join(assets_dir, country, filename)
                current_page = 1 if "page=1" in url else page
                print(
                    f"Downloading {img_url} to {target_path} (Query: {query}, Page: {current_page})..."
                )
                img_response = requests.get(img_url)
                img_response.raise_for_status()

                with open(target_path, "wb") as f:
                    f.write(img_response.content)

                if is_valid_image(target_path):
                    downloaded += 1
                else:
                    print(f"Downloaded image is invalid, removing: {target_path}")
                    os.remove(target_path)

        except Exception as e:
            print(f"Error processing {country} with query {query}: {e}")

    if downloaded > 0:
        # Optional: Remove dummy files if they exist
        path = os.path.join(assets_dir, country)
        for f in os.listdir(path):
            if f.startswith("dummy_"):
                os.remove(os.path.join(path, f))
                print(f"Removed dummy file: {f}")

    return downloaded


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

    words = ["hello", "love"]

    for word in words:
        assets_dir = f"{word}_assets"
        if args.clear and os.path.exists(assets_dir):
            print(f"Clearing all existing images in {assets_dir}...")
            for country in os.listdir(assets_dir):
                country_path = os.path.join(assets_dir, country)
                if os.path.isdir(country_path):
                    for f in os.listdir(country_path):
                        if not f.startswith("."):
                            os.remove(os.path.join(country_path, f))

        missing = get_missing_counts(word)
        if not missing:
            print(f"No missing backgrounds found for {word}.")
            continue

        print(
            f"Found {len(missing)} countries needing refills for {word}: {', '.join(f'{k}:{v}' for k, v in missing.items())}"
        )

        for country, count in missing.items():
            downloaded = download_from_pexels(country, api_key, word, count)
            if downloaded > 0:
                print(
                    f"Successfully refilled {downloaded} images for {country} ({word})"
                )
                time.sleep(1)  # Be respectful to the API
            else:
                print(f"Failed to refill {country} ({word})")


if __name__ == "__main__":
    main()
