#!/bin/bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download Unicode fonts
mkdir -p fonts
BASE_URL="https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf"
fonts=(
  "NotoSans/NotoSans-Regular.ttf"
  "NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
  "NotoSansArabic/NotoSansArabic-Regular.ttf"
  "NotoSansBengali/NotoSansBengali-Regular.ttf"
  "NotoSansThai/NotoSansThai-Regular.ttf"
  "NotoSansHebrew/NotoSansHebrew-Regular.ttf"
  "NotoSansTamil/NotoSansTamil-Regular.ttf"
  "NotoSansTelugu/NotoSansTelugu-Regular.ttf"
  "NotoSansGurmukhi/NotoSansGurmukhi-Regular.ttf"
  "NotoSansKannada/NotoSansKannada-Regular.ttf"
  "NotoSansMalayalam/NotoSansMalayalam-Regular.ttf"
  "NotoSansSinhala/NotoSansSinhala-Regular.ttf"
  "NotoSansKhmer/NotoSansKhmer-Regular.ttf"
  "NotoSansLao/NotoSansLao-Regular.ttf"
  "NotoSansEthiopic/NotoSansEthiopic-Regular.ttf"
  "NotoSansArmenian/NotoSansArmenian-Regular.ttf"
  "NotoSansGeorgian/NotoSansGeorgian-Regular.ttf"
)

for font in "${fonts[@]}"; do
  filename=$(basename "$font")
  if [ ! -f "fonts/$filename" ]; then
    echo "Downloading $filename..."
    curl -L "$BASE_URL/$font" -o "fonts/$filename"
  fi
done

# Eliminate old/unreliable fonts if they exist
rm -f fonts/arial.ttf
rm -f fonts/Quivira-A8VL.ttf

echo "Environment set up successfully!"
echo "To use it, run: source venv/bin/activate"
