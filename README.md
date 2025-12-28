# mister-worldwide
Consumes a single word. Produces a gif of that word translating between many languages.

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

## Advanced Features

### Smart Color Picker

Automatically choose text color for optimal readability (contrast) or blending (camouflage) with background images.

**Contrast Mode** - Text color is automatically selected to maximize contrast with the background:
```bash
python3 mr-worldwide.py --text_array "CONTRAST, MODE, DEMO" --size "512,256" --font_path fonts/arial.ttf --background_images bg1.png bg2.png bg3.png --smart_color_picker contrast --delay 500 --languages en
```

**Camouflage Mode** - Text color is automatically selected to blend with the background:
```bash
python3 mr-worldwide.py --text_array "CAMOUFLAGE, MODE, DEMO" --size "512,256" --font_path fonts/arial.ttf --background_images bg1.png bg2.png bg3.png --smart_color_picker camouflage --delay 500 --languages en
```

### Background Images

You can now use custom background images for each frame:
```bash
python3 mr-worldwide.py --text "Hello" --background_images image1.jpg image2.jpg image3.jpg --languages en es fr
```

The images will be:
- Automatically resized to match the GIF dimensions
- Cycled if fewer images than text frames are provided
- Combined with the smart color picker for optimal text visibility



``` TODO
--round_robin true #true or false
```

**round-robin-sinosoidal**
Start at A_0, emphasizing for interval-ms time, then cycle through all other options until A_1 for interval-ms time, then A_2, and so on.
Come to think of it, it's a misnomer : it's more a piecewise saw-tooth function.
