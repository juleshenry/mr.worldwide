import argparse
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Config:
    text: Optional[str]
    text_array: Optional[List[str]]
    delay: int
    sine_delay: int
    animation: str
    smart_color: bool
    tts: bool
    font_size: int
    font_color: Tuple[int, ...]
    font_path: str
    background_color: Tuple[int, ...]
    background_images: Optional[List[str]]
    size: Tuple[int, ...]
    gif_path: str
    languages: List[str]
    log_level: str
    provider: str

    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser(
            description="Create a GIF with customizable parameters"
        )
        parser.add_argument("--text", default=None, help="The text to display")
        parser.add_argument("--text_array", default=None, help="The text to display")
        parser.add_argument(
            "--delay", type=int, default=100, help="Delay between frames in milliseconds"
        )
        parser.add_argument(
            "--sine_delay",
            type=int,
            default=0,
            help="If zero, ignored. Else, focuses on each frame for sine_delay seconds, round-robin",
        )
        parser.add_argument(
            "--font_size", type=int, default=32, help="Font size"
        )
        parser.add_argument(
            "--font_color", type=str, default="256,256,256", help="Font color (R,G,B)"
        )
        parser.add_argument(
            "--font_path", default="fonts/arial.ttf", help="Path to the font file"
        )
        parser.add_argument(
            "--background_color", type=str, default="0,0,0", help="Background color (R,G,B)"
        )
        parser.add_argument(
            "--background_images", nargs="+", help="List of background image paths (one per language)"
        )
        parser.add_argument("--size", type=str, default="256,256", help="Image width,height")
        parser.add_argument(
            "--gif_path", default="output.gif", help="Path to save the output GIF"
        )
        parser.add_argument(
            "--languages", nargs="+", default=["all"], help="two letter code list"
        )
        parser.add_argument(
            "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level"
        )
        parser.add_argument(
            "--provider", default="argos", choices=["argos", "google", "deepl"], help="Translation provider to use"
        )
        parser.add_argument(
            "--animation", default="sine", choices=["sine", "linear", "ease-in", "ease-out", "bounce"],
            help="Animation type for frame timing"
        )
        parser.add_argument(
            "--smart-color", action="store_true", help="Automatically choose font color for high contrast"
        )
        parser.add_argument(
            "--tts", action="store_true", help="Generate text-to-speech audio files for each language"
        )
        
        args = parser.parse_args()
        
        # Process arguments
        text_array = args.text_array.split(",") if args.text_array else None
        font_color = tuple(map(int, args.font_color.split(",")))
        background_color = tuple(map(int, args.background_color.split(",")))
        size = tuple(map(int, args.size.split(",")))
        
        return cls(
            text=args.text,
            text_array=text_array,
            delay=args.delay,
            sine_delay=args.sine_delay,
            font_size=args.font_size,
            font_color=font_color,
            font_path=args.font_path,
            background_color=background_color,
            background_images=args.background_images,
            size=size,
            gif_path=args.gif_path,
            languages=args.languages,
            log_level=args.log_level,
            provider=args.provider,
            animation=args.animation,
            smart_color=args.smart_color,
            tts=args.tts
        )
