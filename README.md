# mister-worldwide
Consumes a single word. Produces a gif of that word translating between many languages.

Basic 

```
python3 mr-worldwide.py --size "256,256" --text hello! --font_path fonts/arial.ttf --font_color "256,32,32" --background_color "256,256,256" --languages all --delay 300
```

Intermediate
```
--round_robin true #true or false
--background_color blue #red,blue,green,etc.
--background_images #list of image paths, stretched to fit box size, must equal number of languages
--text_array #
```

**round-robin-sinosoidal**
Start at A_0, emphasizing for interval-ms time, then cycle through all other options until A_1 for interval-ms time, then A_2, and so on.
Come to think of it, it's a misnomer : it's more a piecewise saw-tooth function.
