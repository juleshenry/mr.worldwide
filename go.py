import os

if __name__ == "__main__":
    cmd = ('python3 mr-worldwide.py --size "256,256" --text "Your mileage may vary" --font_path fonts/arial.ttf '+
        '--font_color "256,32,32" --font_size=32 --background_color "256,256,256" --languages pt id es --delay 300')
    print(cmd)
    os.system(
        cmd
    )
    
