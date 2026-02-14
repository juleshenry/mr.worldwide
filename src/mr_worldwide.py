import argparse
import os
import sys

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm
from src.utils import get_path, sine_adder
from src.assets_manager import get_trans
from src.renderer import get_actual_text_width, create_frame


def create_gif(params):
    text = params.text
    text_array = []
    if params.text_array:
        text_array = [(t.strip(), "und") for t in params.text_array.split(",")]

    if not text and not text_array:
        raise ValueError("need text or text array")

    if text:
        text_array = get_trans(text, languages=params.languages)

    # Deduplicate
    unique_text_array = []
    seen_texts = set()
    for t, l in text_array:
        clean_t = t.lower().strip()
        if clean_t not in seen_texts:
            unique_text_array.append((t, l))
            seen_texts.add(clean_t)
    text_array = unique_text_array

    width, height = (int(x) for x in params.size.split(","))
    base_font_size = params.font_size if params.font_size != 32 else height // 4

    text_configs = {}
    print(f"Analyzing {len(text_array)} translations...")
    for t, l in text_array:
        f_size = base_font_size
        t_width, b_left, b_right = get_actual_text_width(
            t,
            l,
            params.font_path,
            f_size,
            char_by_char=params.use_flag_colors or params.rainbow,
        )
        if t_width == 0 and t.strip():
            text_configs[(t, l)] = (0, 0, 0, 0)
            continue
        while t_width > width * 0.9 and f_size > 8:
            f_size -= 2
            t_width, b_left, b_right = get_actual_text_width(
                t,
                l,
                params.font_path,
                f_size,
                char_by_char=params.use_flag_colors or params.rainbow,
            )
        text_configs[(t, l)] = (f_size, t_width, b_left, b_right)

    frames = []
    used_images_paths = set()

    print(f"Generating frames...")
    for i, (t, l) in enumerate(tqdm(text_array, desc="Progress")):
        if text_configs[(t, l)][1] == 0 and t.strip():
            continue
        frame = create_frame(
            t, l, params, text_configs[(t, l)], i, len(text_array), used_images_paths
        )
        frames.append(frame)

    if not frames:
        print("No frames created.")
        return

    duration = params.delay
    if params.sine_delay > 0:
        frames = sine_adder(frames, params.sine_delay // params.delay)

    frames[0].save(
        params.gif_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration,
    )
    print(f"\nSuccess! GIF saved to {params.gif_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Mr. Worldwide: Animated Translation GIFs"
    )
    parser.add_argument("--text", help="The word to translate")
    parser.add_argument("--text_array", help="Comma-separated custom strings")
    parser.add_argument(
        "--delay", type=int, default=100, help="Delay between frames (ms)"
    )
    parser.add_argument(
        "--sine_delay", type=int, default=0, help="Sine-focus duration (ms)"
    )
    parser.add_argument("--font_size", type=int, default=32)
    parser.add_argument("--font_color", default="255,255,255")
    parser.add_argument("--font_path", default=get_path("fonts/NotoSans-Regular.ttf"))
    parser.add_argument("--background_color", default="0,0,0")
    parser.add_argument("--size", default="256,256")
    parser.add_argument("--gif_path", default="output.gif")
    parser.add_argument(
        "--use_icons", action="store_true", help="Use country-specific backgrounds"
    )
    parser.add_argument(
        "--smart_color", action="store_true", help="Auto-contrast text color"
    )
    parser.add_argument(
        "--use_flag_colors", action="store_true", help="Use flag colors for text"
    )
    parser.add_argument("--rainbow", action="store_true", help="Rainbow text effect")
    parser.add_argument(
        "--show_labels", action="store_true", help="Show language/country labels"
    )
    parser.add_argument("--languages", nargs="+", default="all")

    args = parser.parse_args()

    if not args.text and not args.text_array:
        parser.print_help()
        sys.exit(1)

    create_gif(args)


if __name__ == "__main__":
    # Ensure the project root is in sys.path when running as a script
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
