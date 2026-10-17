import json
import sys
import unicodedata

# Every translation should be written in a single script. A stray character
# from a neighbouring block (e.g. Sinhala inside Kannada, Thai inside Bengali)
# has no glyph in the language's font and renders as a tofu box.


def script_of(char):
    """Rough script name from the Unicode character name; None for shared characters."""
    category = unicodedata.category(char)
    if category[0] in "PZNS" or category == "Cf":
        return None
    name = unicodedata.name(char, "")
    if name.startswith(("COMBINING", "MODIFIER LETTER")):
        return None
    script = name.split(" ")[0]
    if script in ("CJK", "HIRAGANA", "KATAKANA"):
        return "CJK"
    return script


def check_scripts(path="translations.json"):
    with open(path, "r", encoding="utf-8") as f:
        translations = json.load(f)

    errors = []
    for word, by_lang in translations.items():
        for lang, text in by_lang.items():
            scripts = {}
            for char in text:
                script = script_of(char)
                if script:
                    scripts.setdefault(script, []).append(f"U+{ord(char):04X}")
            if len(scripts) > 1:
                errors.append(f"{word}/{lang} {text!r} mixes scripts: {scripts}")
            if unicodedata.normalize("NFC", text) != text:
                errors.append(f"{word}/{lang} {text!r} is not NFC-normalised")
    return errors


if __name__ == "__main__":
    errors = check_scripts()
    for error in errors:
        print(error)
    if errors:
        sys.exit(1)
    print("All translations use a single script.")
