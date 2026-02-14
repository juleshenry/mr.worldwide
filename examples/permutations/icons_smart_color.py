import os
from pathlib import Path

# Navigate to project root
root = Path(__file__).parent.parent.parent
os.chdir(root)

def run():
    cmd = 'python3 src/mr_worldwide.py --text "Love" --use_icons --smart_color --gif_path examples/outputs/icons_smart_color.gif'
    print(f"Running: {cmd}")
    os.system(cmd)

if __name__ == "__main__":
    run()
