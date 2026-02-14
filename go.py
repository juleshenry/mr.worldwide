import os

if __name__ == "__main__":
    # No frills, all language simple
    simplest_cmd = 'python3 mr-worldwide.py --text "Hello"'

    # Basic cmd, using all the options
    basic_cmd = (
        'python3 mr-worldwide.py --size "256,256" --text "Your mileage may vary" --font_path fonts/arial.ttf '
        + '--font_color "256,32,32" --font_size=32 --background_color "256,256,256" --languages all --delay 300'
    )
    # Example of --text_array
    text_array_cmd = (
        'python3 mr-worldwide.py --size "1024,256" --text_array "你好, Hola, Hello, नमस्ते, السلام عليكم, হ্যালো, Olá, Привет, こんにちは, ਸਤ ਸ੍ਰੀ ਅਕਾਲ, Hallo, Halo, 呵呵, హలో, Xin chào, नमस्कार, 안녕하세요, Bonjour, வணக்கம், Merhaba, اسلام و علیکم, 哈囉, สวัสดี, નમસ્તે, Pronto" --font_path fonts/arial.ttf '
        + '--font_color "0,0,0" --font_size=32 --background_color "256,256,256" --languages all --delay 300'
    )
    # Example of --text_array
    sine_cmd = (
        'python3 mr-worldwide.py --size "1024,256" --text_array "你好, Hola, Hello, नमस्ते, السلام عليكم, হ্যালো, Olá, Привет, こんにちは, ਸਤ ਸ੍ਰੀ ਅਕਾਲ, Hallo, Halo, 呵呵, హలో, Xin chào, नमस्कार, 안녕하세요, Bonjour, வணக்கம், Merhaba, اسلام و علیکم, 哈囉, สวัสดี, નમસ્તે, Pronto" --font_path fonts/arial.ttf --font_color "0,0,0" --font_size=32 --background_color "256,256,256" --languages all --delay 20 --sine_delay 200 --gif_path="simple_output.gif"'
    )

    # Mr. Worldwide mode: using images and smart color contrast
    worldwide_cmd = (
        'python3 mr-worldwide.py --text "Hello" --use_images --languages all --delay 500 --gif_path "mr_worldwide.gif"'
    )

    print((c := worldwide_cmd))
    os.system(c)
