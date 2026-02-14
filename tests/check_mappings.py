import json
import os

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

with open("flag_colors.json", "r") as f:
    flag_colors = json.load(f)

with open("translations.json", "r") as f:
    translations = json.load(f)

all_langs = set(translations["hello"].keys()) | set(translations["love"].keys())

missing_countries = []
missing_flags = []

for lang in all_langs:
    country = LANG_TO_COUNTRY.get(lang)
    if not country:
        missing_countries.append(lang)
        continue

    formatted_country = "_".join([w.capitalize() for w in country.split("_")])
    if formatted_country not in flag_colors:
        missing_flags.append((lang, formatted_country))

print(f"Total languages: {len(all_langs)}")
print(f"Missing country mapping for: {missing_countries}")
print(f"Missing flag data for: {missing_flags}")

# Check if any country is over-represented
from collections import Counter

counts = Counter(LANG_TO_COUNTRY.values())
print(f"Most common countries: {counts.most_common(5)}")
