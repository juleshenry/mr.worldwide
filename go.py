import os

if __name__ == "__main__":
    cmd = ('python3 mr-worldwide.py --size "256,256" --text love --font_path fonts/Quivira-A8VL.ttf '+
        '--font_color "256,256,256" --background_color "256,256,256" --languages all --delay 50')
    print(cmd)
    os.system(
        cmd
    )
    