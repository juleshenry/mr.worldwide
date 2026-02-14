import os
from pathlib import Path

# Navigate to project root
root = Path(__file__).parent.parent.parent
os.chdir(root)

def run():
    cmd = 'python3 src/mr_worldwide.py --text "Colors" --font_color "255,0,0" --background_color "0,255,255" --gif_path examples/outputs/custom_colors.gif'
    print(f"Running: {cmd}")
    os.system(cmd)

if __name__ == "__main__":
    run()
