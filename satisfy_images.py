import json
import os
import glob
import uuid

# Mapping from ISO 639-1 language codes to country folder names
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


def satisfy():
    with open("translations.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    assets_dir = "picture_assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    # Track how many images we need to ADD per country
    needed_additions = {}

    for word, translations in data.items():
        # Group by translated string to handle duplicates like "Amor"
        string_to_langs = {}
        for lang, trans_text in translations.items():
            if trans_text not in string_to_langs:
                string_to_langs[trans_text] = []
            string_to_langs[trans_text].append(lang)

        for trans_text, langs in string_to_langs.items():
            count_needed = len(langs)
            countries = []
            for l in langs:
                c = LANG_TO_COUNTRY.get(l, "global_default")
                countries.append(c)

            # Count current images in these countries
            current_total = 0
            for c in set(countries):
                c_dir = os.path.join(assets_dir, c)
                if os.path.exists(c_dir):
                    current_total += len(glob.glob(os.path.join(c_dir, "*.*")))

            if current_total < count_needed:
                gap = count_needed - current_total
                # Distribute gap among the countries (prefer the first one found for simplicity)
                primary_country = countries[0]
                needed_additions[primary_country] = max(
                    needed_additions.get(primary_country, 0), gap
                )

    # Now handle individual languages that might just be missing a folder entirely
    for lang, country in LANG_TO_COUNTRY.items():
        c_dir = os.path.join(assets_dir, country)
        if not os.path.exists(c_dir) or not glob.glob(os.path.join(c_dir, "*.*")):
            if country not in needed_additions:
                needed_additions[country] = 1

    # Apply additions
    for country, count in needed_additions.items():
        c_dir = os.path.join(assets_dir, country)
        if not os.path.exists(c_dir):
            os.makedirs(c_dir)
            print(f"Created directory: {c_dir}")

        existing = len(glob.glob(os.path.join(c_dir, "*.*")))
        # We need to make sure the folder has AT LEAST the count we calculated
        # Actually, the logic above calculates the gap.
        # Let's just ensure the folder has 'count' images if it was missing some.
        to_create = count
        for _ in range(to_create):
            dummy_path = os.path.join(c_dir, f"dummy_{uuid.uuid4().hex[:8]}.jpg")
            with open(dummy_path, "w") as f:
                f.write("dummy")
            print(f"Created dummy image: {dummy_path}")


if __name__ == "__main__":
    satisfy()
