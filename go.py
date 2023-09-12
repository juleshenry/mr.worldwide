import os

if __name__ == "__main__":
    cmd = ('python3 mr-worldwide.py --size "256,256" --text love --font_path fonts/arial.ttf '+
        '--font_color "256,32,32" --background_color "0,0,0" --languages all --delay 300')
    print(cmd)
    os.system(
        cmd
    )
    
