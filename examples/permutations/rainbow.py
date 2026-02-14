import os
from pathlib import Path

# Navigate to project root
root = Path(__file__).parent.parent.parent
os.chdir(root)

def run():
    cmd = 'python3 src/mr_worldwide.py --text "Rainbow" --rainbow --gif_path examples/outputs/rainbow.gif'
    print(f"Running: {cmd}")
    os.system(cmd)

if __name__ == "__main__":
    run()
