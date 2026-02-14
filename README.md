# Mr. Worldwide 🌎

Mr. Worldwide is a Python tool that generates animated GIFs of a single word translated into many languages, each displayed against a culturally relevant background image.

![Mr. Worldwide Demo](worldwide_demo.gif)

## Features

- **Multi-language Support**: Automatically translates words like "Hello" and "Love" into over 100 languages.
- **Dynamic Backgrounds**: Uses country-specific images when available (from `hello_assets/` and `love_assets/`).
- **Smart Color Selection**: Automatically chooses the best text color and outline for maximum contrast against dynamic backgrounds.
- **Automatic Font Scaling**: Ensures long translations fit perfectly within the image dimensions.
- **Regional Ordering**: Frames are ordered by region (Europe, Asia, Africa, etc.) for a logical flow.
- **Unicode Excellence**: Automatically selects the correct Noto font for different scripts (Arabic, Devanagari, CJK, etc.).
- **Visual Effects**: Supports rainbow text and flag-colored text.
- **Flexible Timing**: Supports constant delay or "round-robin" timing.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/enrique/mr.worldwide.git
    cd mr.worldwide
    ```

2.  **Run the setup script**:
    This script creates a virtual environment, installs dependencies, and downloads the necessary Unicode fonts.
    ```bash
    bash setup.sh
    source venv/bin/activate
    ```

3.  **(Optional) Download assets**:
    Download some initial background images from Wikimedia Commons:
    ```bash
    python3 download_assets.py
    ```

## Usage

### Basic Example
Generate a simple GIF with a solid background:
```bash
python3 mr-worldwide.py --text "Hello" --size "512,512" --delay 500
```

### Mr. Worldwide Mode (The Full Experience)
Generate a GIF with background images, smart colors, and regional ordering:
```bash
python3 mr-worldwide.py --text "Love" --use_icons --smart_color --delay 500 --gif_path "love_worldwide.gif"
```

### Custom Text Array
Provide your own list of words:
```bash
python3 mr-worldwide.py --text_array "Hola, Bonjour, Ciao, привет" --size "400,200" --rainbow --delay 300
```

### Advanced Options

| Option | Description | Default |
| :--- | :--- | :--- |
| `--text` | The word to translate (e.g., "Hello", "Love"). | `None` |
| `--text_array` | A comma-separated list of custom strings. | `None` |
| `--use_icons` | Enable country-specific background images. | `False` |
| `--smart_color` | Pick high-contrast text colors automatically. | `False` |
| `--rainbow` | Apply a shifting rainbow effect to the text. | `False` |
| `--use_flag_colors` | Color the text based on the country's flag. | `False` |
| `--size` | Image dimensions in `width,height`. | `256,256` |
| `--delay` | Time between frames in milliseconds. | `100` |
| `--sine_delay` | Focus on each frame for N ms in a loop. | `0` |
| `--languages` | List of ISO codes or `all`. | `all` |
| `--font_path` | Path to a custom TTF/OTF font file. | `fonts/NotoSans-Regular.ttf` |

## Asset Organization

- `hello_assets/`: Folders named by country containing images for the word "Hello".
- `love_assets/`: Folders named by country containing images for the word "Love".
- `fonts/`: Contains Unicode-compliant Noto fonts.
- `translations.json`: Dictionary of hardcoded translations.

## Advanced: Refilling Assets
If you want to use the Pexels API to download more high-quality background images, you can use `pexels_refill.py`. You will need a Pexels API key saved in a `.1nv` file as `PEXELS_API_KEY=your_key_here`.

```bash
python3 pexels_refill.py
```

## Requirements

- Python 3.12+
- Pillow
- NumPy
- SciPy

*Note: Setup script handles most of these automatically.*
