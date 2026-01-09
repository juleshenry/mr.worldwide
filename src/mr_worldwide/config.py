import argparse
from dataclasses import dataclass
from typing import List, Tuple, Optional


def _parse_int_tuple(value: str, *, expected_len: int, name: str) -> Tuple[int, ...]:
    parts = [p.strip() for p in value.split(",") if p.strip() != ""]
    if len(parts) != expected_len:
        raise ValueError(f"{name} must have {expected_len} comma-separated integers (got '{value}')")
    try:
        return tuple(int(p) for p in parts)
    except ValueError as e:
        raise ValueError(f"{name} must be integers (got '{value}')") from e


def _clamp_rgb(rgb: Tuple[int, ...]) -> Tuple[int, int, int]:
    if len(rgb) != 3:
        raise ValueError(f"RGB color must have 3 components (got {rgb})")
    r, g, b = rgb
    return (
        max(0, min(255, int(r))),
        max(0, min(255, int(g))),
        max(0, min(255, int(b))),
    )


def _parse_rgb(value: str, *, name: str) -> Tuple[int, int, int]:
    # Accepts out-of-range values (e.g. 256 from README) by clamping to 0-255.
    return _clamp_rgb(_parse_int_tuple(value, expected_len=3, name=name))


def _parse_languages(values: List[str]) -> List[str]:
    # argparse uses nargs='+', so users might pass either:
    #   --languages es fr de
    # or:
    #   --languages es,fr,de
    # Normalize both.
    out: List[str] = []
    for item in values:
        for part in item.split(","):
            part = part.strip()
            if part:
                out.append(part)
    return out or ["all"]

@dataclass
class Config:
    text: Optional[str]
    text_array: Optional[List[str]]
    delay: int
    sine_delay: int
    animation: str
    smart_color: bool
    tts: bool
    interactive: bool
    offline: bool
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
    def from_parsed_args(cls, args: argparse.Namespace) -> "Config":
        # Process arguments
        text_array = args.text_array.split(",") if args.text_array else None
        font_color = _parse_rgb(args.font_color, name="font_color")
        background_color = _parse_rgb(args.background_color, name="background_color")
        size = _parse_int_tuple(args.size, expected_len=2, name="size")

        # Normalize languages
        args.languages = _parse_languages(args.languages)

        # Parse delay
        if isinstance(args.delay, str) and args.delay.startswith("sine:"):
            spec = args.delay.split(":", 1)[1]
            parts = [p.strip() for p in spec.split(",") if p.strip() != ""]
            if len(parts) != 2:
                raise ValueError("--delay sine syntax must be 'sine:sine_delay,delay' (e.g. sine:500,100)")
            args.sine_delay = int(parts[0])
            args.delay = int(parts[1])
        else:
            args.delay = int(args.delay)

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
            tts=args.tts,
            interactive=getattr(args, "interactive", False),
            offline=getattr(args, "offline", False),
        )

    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser(
            description="Create a GIF with customizable parameters"
        )
        parser.add_argument("--text", default=None, help="The text to display")
        parser.add_argument("--text_array", default=None, help="The text to display")
        parser.add_argument(
            "--delay",
            type=str,
            default="100",
            help="Delay between frames in milliseconds, or 'sine:sine_delay,delay' (e.g. sine:500,100)"
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
            "--font_color", type=str, default="255,255,255", help="Font color (R,G,B)"
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
        parser.add_argument(
            "--interactive", "-i", action="store_true", help="Run in interactive mode with prompts"
        )
        parser.add_argument(
            "--offline", action="store_true", help="Run in offline mode (requires pre-downloaded translation packages)"
        )
        
        args = parser.parse_args()
        return cls.from_parsed_args(args)
