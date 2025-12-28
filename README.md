# mister-worldwide

Consumes a single word. Produces a gif of that word translating between many languages.

## Installation

Install the required dependencies using Poetry:

```bash
poetry install
```

For development and testing (includes dev dependencies):
```bash
poetry install --with dev
```

Basic 

```
python3 mr-worldwide.py --size "256,256" --text hello! --font_path fonts/arial.ttf --font_color "256,32,32" --background_color "256,256,256" --languages all --delay 300
```

Intermediate Examples
```
TEXT ARRAY:

python3 mr-worldwide.py --size "1024,256" --text_array "你好, Hola, Hello, नमस्ते, السلام عليكم, হ্যালো, Olá, Привет, こんにちは, ਸਤ ਸ੍ਰੀ ਅਕਾਲ, Hallo, Halo, 呵呵, హలో, Xin chào, नमस्कार, 안녕하세요, Bonjour, வணக்கம், Merhaba, اسلام و علیکم, 哈囉, สวัสดี, નમસ્તે, Pronto" --font_path fonts/arial.ttf --font_color "0,0,0" --font_size=32 --background_color "256,256,256" --languages all --delay 300
```

```
SINUSOIDAL:

python3 mr-worldwide.py --size "256,256" --text hello! --font_path fonts/arial.ttf --font_color "256,32,32" --background_color "256,256,256" --languages all --delay sine:"500,100" 

```

## API

The project includes a REST API for programmatic GIF generation using FastAPI.

### Starting the API Server

```bash
poetry run uvicorn src.mr_worldwide.web_api:app --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### API Endpoints

#### POST `/generate-gif`

Generate a GIF with translated text.

**Parameters:**
- `text` (optional): Single text to translate
- `text_array` (optional): Comma-separated list of texts
- `languages` (default: "all"): Language codes or "all"
- `provider` (default: "argos"): Translation provider
- `size` (default: "256,256"): Image dimensions
- `font_color` (default: "255,255,255"): Font color as RGB
- `background_color` (default: "0,0,0"): Background color as RGB
- `delay` (default: 100): Frame delay in ms
- `animation` (default: "linear"): Animation type
- `smart_color` (default: false): Auto-contrast font color
- `tts` (default: false): Generate TTS audio

**Example:**
```bash
curl -X POST "http://localhost:8000/generate-gif" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "languages": "es,fr,de"}' \
  --output hello_translations.gif
```

## Testing

The project includes comprehensive unit and integration tests using pytest. To run the tests:

### Installation

First, install the development dependencies:

```bash
poetry install --with dev
```

### Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test files:
```bash
pytest tests/test_argos_hola.py
pytest tests/test_mr_worldwide.py
pytest tests/test_cli_integration.py
```

### Test Coverage

The test suite covers:

- **Translation functionality** (`tests/test_argos_hola.py`):
  - `from_to_text()` function with success and error cases
  - `get_trans()` function with various language configurations

- **Core image generation** (`tests/test_mr_worldwide.py`):
  - `get_max_width()` for text sizing calculations
  - `sine_adder()` for animation frame manipulation
  - Argument parsing and color conversion in `main()`
  - GIF creation logic in `create_gif()`

- **CLI integration** (`tests/test_cli_integration.py`):
  - Command-line argument parsing
  - Error handling for invalid inputs
  - Help text display

Tests use mocking to avoid dependencies on external services and focus on unit behavior.

``` TODO
--round_robin true #true or false
--background_images #list of image paths, stretched to fit box size, must equal number of languages
--smart_color_picker (from background, highest maximal contrast, <3)
```

**round-robin-sinosoidal**
Start at A_0, emphasizing for interval-ms time, then cycle through all other options until A_1 for interval-ms time, then A_2, and so on.
Come to think of it, it's a misnomer : it's more a piecewise saw-tooth function.
