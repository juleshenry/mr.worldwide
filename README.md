# mister-worldwide
Consumes a single word. Produces a gif of that word translating between many languages.

Basic 

```
python3 start.py --size 256 256 --text love --font_path fonts/Poppins-Medium.ttf --font_color-color green --background-color blue --languages all --interval-ms 50
```

Intermediate


mister-worldwide --size 256 256 --text love --font poppins --font-color green --background-color blue -background-image back.jpg -fit-method stretch  --languages es zh ru pt kr --interval round-robin-sinosoidal --interval-ms 50


**round-robin-sinosoidal**
Start at A_0, emphasizing for interval-ms time, then cycle through all other options until A_1 for interval-ms time, then A_2, and so on.
Come to think of it, it's a misnomer : it's more a piecewise saw-tooth function.
