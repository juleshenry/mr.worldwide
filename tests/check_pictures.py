import json
import os
import glob

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


def check_pictures():
    translations_file = "translations.json"

    if not os.path.exists(translations_file):
        print(f"Error: {translations_file} not found.")
        return

    with open(translations_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"{'WORD':<10} | {'TRANSLATION':<15} | {'STATUS'}")
    print("-" * 50)

    any_missing = False
    for word, translations in data.items():
        assets_dir = f"{word}_assets"
        # Pre-calculate image counts per country folder for this word
        country_counts = {}
        for country in set(LANG_TO_COUNTRY.values()):
            path = os.path.join(assets_dir, country)
            if os.path.exists(path):
                # Only count non-dummy files
                files = [f for f in os.listdir(path) if not f.startswith("dummy_")]
                country_counts[country] = len(files)
            else:
                country_counts[country] = 0

        # Group by unique translated string to handle duplicates requiring n-images
        string_groups = {}
        for lang, trans_text in translations.items():
            string_groups.setdefault(trans_text, []).append(lang)

        for trans_text, langs in string_groups.items():
            # Group languages by their mapped country
            needed_per_country = {}
            for l in langs:
                country = LANG_TO_COUNTRY.get(l, "global")
                needed_per_country[country] = needed_per_country.get(country, 0) + 1

            # Check each country's capacity
            missing_details = []
            for country, count_needed in needed_per_country.items():
                available = country_counts.get(country, 0)
                if available < count_needed:
                    missing_details.append(f"{country}:{count_needed - available}")

            if missing_details:
                any_missing = True
                lang_str = ",".join(langs)
                detail_str = ", ".join(missing_details)
                print(
                    f"{word:<10} | {trans_text:<15} | MISSING {detail_str} [{lang_str}]"
                )

    if not any_missing:
        print("All background images satisfied!")


if __name__ == "__main__":
    check_pictures()
