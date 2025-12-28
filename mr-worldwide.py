import sys
import os

# Ensure src is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mr_worldwide import Config, Translator, GifGenerator
from mr_worldwide.logger import setup_logging, get_logger

def main():
    # 1. Parse Configuration
    config = Config.from_args()
    
    # Setup logging
    setup_logging(config.log_level)
    logger = get_logger(__name__)

    try:
        # 2. Get Translations or Text Array
        if config.text:
            translator = Translator(provider=config.provider)
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
