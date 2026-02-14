import os
from PIL import Image


def check_images(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith("."):
                continue
            path = os.path.join(root, file)
            try:
                with Image.open(path) as img:
                    w, h = img.size
                    if w < 100 or h < 100:
                        print(f"Small image: {path} ({w}x{h})")
            except Exception as e:
                print(f"Error identifying {path}: {e}")


if __name__ == "__main__":
    check_images("hello_assets")
    check_images("love_assets")
