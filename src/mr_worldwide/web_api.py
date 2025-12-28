from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
from typing import Optional, List
from .config import Config
from .translator import Translator
from .gif_generator import GifGenerator
from .logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Mister Worldwide GIF Generator", description="Generate animated GIFs with translated text")

@app.post("/generate-gif")
async def generate_gif(
    text: Optional[str] = None,
    text_array: Optional[str] = None,
    languages: str = "all",
    provider: str = "argos",
    size: str = "256,256",
    font_color: str = "255,255,255",
    background_color: str = "0,0,0",
    delay: int = 100,
    font_path: str = "fonts/arial.ttf",
    animation: str = "linear",
    smart_color: bool = False,
    tts: bool = False
):
    """
    Generate a GIF with translated text.

    - **text**: Single text to translate
    - **text_array**: Comma-separated list of texts
    - **languages**: Comma-separated language codes or "all"
    - **provider**: Translation provider ("argos", "google", "deepl")
    - **size**: Image size as "width,height"
    - **font_color**: Font color as "r,g,b"
    - **background_color**: Background color as "r,g,b"
    - **delay**: Frame delay in milliseconds
    - **font_path**: Path to font file
    - **animation**: Animation type ("linear", "ease-in", "ease-out", "bounce")
    - **smart_color**: Auto-select contrasting font color
    - **tts**: Generate TTS audio files
    """
    try:
        # Parse arguments
        lang_list = languages.split(",") if languages != "all" else ["all"]
        text_arr = text_array.split(",") if text_array else None

        # Create config (mock argparse args)
        class MockArgs:
            pass

        args = MockArgs()
        args.text = text
        args.text_array = text_arr
        args.languages = lang_list
        args.provider = provider
        args.size = size
        args.font_color = font_color
        args.background_color = background_color
        args.delay = delay
        args.sine_delay = 0  # Not used in API
        args.font_size = 32
        args.font_path = font_path
        args.gif_path = None  # Will set below
        args.log_level = "INFO"
        args.animation = animation
        args.smart_color = smart_color
        args.tts = tts
        args.background_images = None

        config = Config.from_args.__func__(args)  # Call the classmethod with mock args

        # Generate unique output path
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
            config.gif_path = tmp.name

        # Generate the GIF
        if config.text:
            translator = Translator(provider=config.provider)
            text_list = translator.get_translations(config.text, config.languages)
        elif config.text_array:
            text_list = config.text_array
        else:
            raise HTTPException(status_code=400, detail="Must provide either text or text_array")

        generator = GifGenerator(config)
        generator.generate(text_list)

        # Return the file
        return FileResponse(
            config.gif_path,
            media_type="image/gif",
            filename="generated.gif"
        )

    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Mister Worldwide GIF Generator API", "docs": "/docs"}