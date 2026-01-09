import sys
import os

# Ensure src is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.mr_worldwide import Config, Translator, GifGenerator
from src.mr_worldwide.logger import setup_logging, get_logger
import sys

def interactive_config(config):
    """Interactive mode to prompt for configuration"""
    print("=== Mister Worldwide Interactive Mode ===")

    # Text input
    if not config.text and not config.text_array:
        text_choice = input("Enter text or text array? (1=text, 2=array): ").strip()
        if text_choice == "1":
            config.text = input("Enter text to translate: ").strip()
        elif text_choice == "2":
            text_array = input("Enter comma-separated texts: ").strip()
            config.text_array = text_array.split(",") if text_array else None
        else:
            print("Invalid choice, exiting.")
            sys.exit(1)

    # Languages
    if not config.languages or config.languages == ["all"]:
        langs = input("Enter language codes (comma-separated, or 'all'): ").strip()
        config.languages = langs.split(",") if langs != "all" else ["all"]

    # Size
    size_input = input(f"Image size (default {config.size}): ").strip()
    if size_input:
        config.size = tuple(map(int, size_input.split(",")))

    # Colors
    font_color = input(f"Font color RGB (default {config.font_color}): ").strip()
    if font_color:
        config.font_color = tuple(map(int, font_color.split(",")))

    bg_color = input(f"Background color RGB (default {config.background_color}): ").strip()
    if bg_color:
        config.background_color = tuple(map(int, bg_color.split(",")))

    # Other options
    delay = input(f"Frame delay in ms (default {config.delay}): ").strip()
    if delay:
        config.delay = int(delay)

    animation = input(f"Animation type (default {config.animation}): ").strip()
    if animation:
        config.animation = animation

    smart_color = input("Use smart color contrast? (y/N): ").strip().lower()
    config.smart_color = smart_color == "y"

    tts = input("Generate TTS audio? (y/N): ").strip().lower()
    config.tts = tts == "y"

    return config

def main():
    # 1. Parse Configuration
    config = Config.from_args()

    # 2. Interactive mode
    if config.interactive:
        config = interactive_config(config)
    
    # Setup logging
    setup_logging(config.log_level)
    logger = get_logger(__name__)

    try:
        # 2. Get Translations or Text Array
        if config.text:
            translator = Translator(provider=config.provider, offline=config.offline)
            # Note: The original code passed 'languages' to get_trans.
            # If languages is 'all', the translator handles it.
            text_list = translator.get_translations(config.text, config.languages)
        elif config.text_array:
            text_list = config.text_array
        else:
            raise ValueError("need text or text array")

        # 3. Generate GIF
        generator = GifGenerator(config)
        generator.generate(text_list)
        
    except Exception as e:
        logger.critical(f"An unhandled error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
