import os
import re
import json


def extract_colors_with_positions(svg_content):
    # Find all tags that might have colors
    tag_pattern = re.compile(r"<(path|rect|circle|polygon|ellipse|g)\s+([^>]+)>")

    color_positions = []
    for tag_type, attrs in tag_pattern.findall(svg_content):
        # Extract color
        color_match = re.search(r'fill="([^"]+)"', attrs)
        if not color_match:
            color_match = re.search(r'stroke="([^"]+)"', attrs)

        if color_match:
            color = color_match.group(1)
            if color == "none":
                continue

            # Try to find a representative X and Y position
            # We use the midpoint of bounding boxes if available
            x_pos = 0.0
            y_pos = 0.0

            width = 0.0
            height = 0.0

            x_match = re.search(r'x="([-?0-9.]+)"', attrs)
            w_match = re.search(r'width="([-?0-9.]+)"', attrs)
            y_match = re.search(r'y="([-?0-9.]+)"', attrs)
            h_match = re.search(r'height="([-?0-9.]+)"', attrs)

            if x_match:
                x_pos = float(x_match.group(1))
            if w_match:
                width = float(w_match.group(1))
            if y_match:
                y_pos = float(y_match.group(1))
            if h_match:
                height = float(h_match.group(1))

            if not x_match or not y_match:
                d_match = re.search(r'd="M\s*([-?0-9.]+)[,\s]([-?0-9.]+)', attrs)
                if d_match:
                    if not x_match:
                        x_pos = float(d_match.group(1))
                    if not y_match:
                        y_pos = float(d_match.group(2))

            # Centroid approximation
            cx = x_pos + width / 2
            cy = y_pos + height / 2

            color_positions.append((cx, cy, color))

    # Determine if the flag is more vertical or horizontal based on centroid distribution
    if not color_positions:
        return []

    xs = [c[0] for c in color_positions]
    ys = [c[1] for c in color_positions]

    x_range = max(xs) - min(xs) if xs else 0
    y_range = max(ys) - min(ys) if ys else 0

    if x_range >= y_range:
        # Sort by X position (vertical stripes)
        color_positions.sort(key=lambda x: x[0])
    else:
        # Sort by Y position (horizontal stripes)
        color_positions.sort(key=lambda x: x[1])

    ordered_colors = []
    for _, _, c in color_positions:
        # Standardize color
        if c.startswith("#"):
            c_hex = c[1:]
            if len(c_hex) == 3:
                c_hex = "".join([char * 2 for char in c_hex])
            ordered_colors.append("#" + c_hex.upper())
        elif c.lower() == "white":
            ordered_colors.append("#FFFFFF")
        elif c.lower() == "black":
            ordered_colors.append("#000000")
        elif c.lower() == "red":
            ordered_colors.append("#FF0000")

    return ordered_colors


def analyze_flags(banderas_dir):
    flag_data = {}
    # Manual overrides for accuracy on major flags
    overrides = {
        "France": ["#002654", "#FFFFFF", "#CE1126"],
        "Germany": ["#000000", "#FF0000", "#FFCE00"],
        "Italy": ["#009246", "#FFFFFF", "#CE2B37"],
        "Spain": ["#AA151B", "#F1BF00", "#AA151B"],
        "Russia": ["#FFFFFF", "#0039A6", "#D52B1E"],
        "India": ["#FF9933", "#FFFFFF", "#128807"],
        "Brazil": ["#009739", "#FEDF00", "#012169"],
        "United_States": ["#B22234", "#FFFFFF", "#3C3B6E"],
        "United_Kingdom": ["#012169", "#FFFFFF", "#C8102E"],
        "Japan": ["#FFFFFF", "#BC002D", "#FFFFFF"],
        "South_Korea": ["#FFFFFF", "#CD2E3A", "#0047A0", "#000000"],
        "China": ["#DE2910", "#FFDE00"],
        "Netherlands": ["#AE1C28", "#FFFFFF", "#21468B"],
        "Belgium": ["#000000", "#FDDA24", "#EF3340"],
        "Ireland": ["#169B62", "#FFFFFF", "#FF883E"],
        "Republic_of_Ireland": ["#169B62", "#FFFFFF", "#FF883E"],
        "Poland": ["#FFFFFF", "#DC143C"],
        "Ukraine": ["#0057B7", "#FFD700"],
        "Esperanto": ["#009900", "#FFFFFF"],
    }

    filenames = os.listdir(banderas_dir)
    for filename in filenames:
        if filename.endswith(".svg"):
            country = filename[:-4]
            if country in overrides:
                flag_data[country] = overrides[country]
                continue

            with open(os.path.join(banderas_dir, filename), "r") as f:
                content = f.read()
                colors = extract_colors_with_positions(content)
                # Remove duplicates while preserving order
                unique_colors = []
                for c in colors:
                    if c not in unique_colors:
                        unique_colors.append(c)

                if unique_colors:
                    flag_data[country] = unique_colors
    return flag_data


if __name__ == "__main__":
    banderas_dir = "/Users/enrique/Desktop/fun_repos/mr.worldwide/banderas"
    data = analyze_flags(banderas_dir)
    with open("flag_colors.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Analyzed {len(data)} flags.")
