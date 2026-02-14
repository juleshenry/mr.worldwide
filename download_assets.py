import urllib.request
import urllib.parse
import json
import os
import sys
import time

UA = "MrWorldwideBot/1.0 (https://github.com/enrique/mr.worldwide; enrique@example.com) Python/3.x"


def get_image_url(query):
    try:
        # Search for file
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json"
        req = urllib.request.Request(search_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if not data["query"]["search"]:
                return None
            filename = data["query"]["search"][0]["title"]

        # Get direct URL
        info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(filename)}&prop=imageinfo&iiprop=url&format=json"
        req = urllib.request.Request(info_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data["query"]["pages"]
            page = next(iter(pages.values()))
            url = page["imageinfo"][0]["url"]

            # Use a thumbnail URL to avoid 429s on original files
            # Original: https://upload.wikimedia.org/wikipedia/commons/d/da/Filename.jpg
            # Thumb: https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Filename.jpg/1024px-Filename.jpg
            if "upload.wikimedia.org/wikipedia/commons/" in url:
                parts = url.split("/")
                # Original: https://upload.wikimedia.org/wikipedia/commons/d/da/Filename.jpg
                # parts: 0:https, 1:, 2:upload.wikimedia.org, 3:wikipedia, 4:commons, 5:d, 6:da, 7:Filename.jpg
                if len(parts) >= 8:
                    hash1 = parts[5]
                    hash2 = parts[6]
                    filename_only = parts[7]
                    thumb_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{hash1}/{hash2}/{filename_only}/1024px-{filename_only}"
                    return thumb_url

            return url

    except Exception as e:
        print(f"Error fetching {query}: {e}", file=sys.stderr)
        return None


def download_image(query, target_path):
    url = get_image_url(query)
    if not url:
        print(f"No URL found for {query}")
        return

    # Check if file exists and is not a dummy
    if os.path.exists(target_path):
        try:
            from PIL import Image

            with Image.open(target_path) as img:
                img.load()
            if os.path.getsize(target_path) > 5000:
                print(f"Skipping {target_path}, already exists and seems valid.")
                return
        except:
            print(f"Existing file {target_path} is invalid, redownloading...")
            os.remove(target_path)

    print(f"Downloading {query} from {url} to {target_path}...")
    try:
        time.sleep(2)  # Be nice to Wikimedia
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req) as response:
            with open(target_path, "wb") as f:
                f.write(response.read())
        print(f"Successfully downloaded {target_path}")
    except Exception as e:
        print(f"Error downloading {target_path}: {e}")
        # Try original URL if thumb fails
        # (omitted for brevity, or just rely on the thumb)


tasks = [
    ("Hallgrimskirkja", "picture_assets/iceland/hallgrimskirkja.jpg"),
    ("Skogafoss", "picture_assets/iceland/skogafoss.jpg"),
    ("Cliffs of Moher", "picture_assets/ireland/cliffs_of_moher.jpg"),
    ("Rock of Cashel", "picture_assets/ireland/rock_of_cashel.jpg"),
    ("Angkor Wat", "picture_assets/cambodia/angkor_wat.jpg"),
    ("Shwedagon Pagoda", "picture_assets/myanmar/shwedagon.jpg"),
    ("Table Mountain", "picture_assets/south_africa/table_mountain.jpg"),
    ("Milford Sound", "picture_assets/new_zealand/milford_sound.jpg"),
    ("Zuma Rock", "picture_assets/nigeria/zuma_rock.jpg"),
    ("Lalibela Church", "picture_assets/ethiopia/lalibela.jpg"),
    ("Edinburgh Castle", "picture_assets/united_kingdom/edinburgh_castle.jpg"),
    ("Snowdonia National Park", "picture_assets/united_kingdom/snowdonia.jpg"),
    ("Mount Ararat Khor Virap", "picture_assets/armenia/khor_virap.jpg"),
    ("Gergeti Trinity Church", "picture_assets/georgia/gergeti.jpg"),
]

for query, path in tasks:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    download_image(query, path)
