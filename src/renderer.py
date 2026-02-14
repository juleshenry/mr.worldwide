import numpy as np
import colorsys
from scipy.cluster.vq import kmeans, vq
from PIL import Image, ImageDraw, ImageFont, ImageStat
from src.assets_manager import (
    get_font_for_lang,
    get_background_image,
    get_flag_colors_for_text,
    get_rainbow_colors_for_text,
)
from src.config import LANG_TO_COUNTRY, EPONYMS


def get_contrast_colors(image, region, default_color=None):
    """Calculate the best text color by analyzing background contrast."""
    if region[2] <= region[0] or region[3] <= region[1]:
        return (255, 255, 255), (0, 0, 0)

    crop = image.crop(region).convert("RGB")
    small_crop = crop.copy()
    small_crop.thumbnail((32, 32))
    ar = np.asarray(small_crop)
    pixels = ar.reshape(-1, 3).astype(float)

    try:
        codes, _ = kmeans(pixels, 3)
        vecs, _ = vq(pixels, codes)
        counts, _ = np.histogram(vecs, bins=range(len(codes) + 1))
        sorted_indices = np.argsort(counts)[::-1]
        bg_colors = [colorsys.rgb_to_hls(*(codes[i] / 255.0)) for i in sorted_indices]
        bg_weights = [counts[i] / len(pixels) for i in sorted_indices]
    except:
        stat = ImageStat.Stat(crop)
        bg_colors = [colorsys.rgb_to_hls(*(np.array(stat.mean[:3]) / 255.0))]
        bg_weights = [1.0]

    avg_l = sum(c[1] * w for c, w in zip(bg_colors, bg_weights))
    target_l = 0.15 if avg_l > 0.5 else 0.85

    best_h = 0
    max_score = -1
    for i in range(36):
        test_h = i / 36.0
        score = 0
        for (bh, bl, bs), weight in zip(bg_colors, bg_weights):
            if bs > 0.1:
                h_dist = min(abs(test_h - bh), 1.0 - abs(test_h - bh)) * 2.0
                score += (h_dist**2) * weight * bs
            else:
                score += weight * 0.5

        vibrancy_bonus = 0
        for v_h in [0.0, 0.16, 0.33, 0.5, 0.66, 0.83]:
            v_dist = min(abs(test_h - v_h), 1.0 - abs(test_h - v_h)) * 2.0
            if v_dist < 0.1:
                vibrancy_bonus = 0.1

        final_score = score + vibrancy_bonus
        if final_score > max_score:
            max_score = final_score
            best_h = test_h

    tr, tg, tb = colorsys.hls_to_rgb(best_h, target_l, 0.95)
    text_rgb = (int(tr * 255), int(tg * 255), int(tb * 255))
    text_brightness = (text_rgb[0] * 299 + text_rgb[1] * 587 + text_rgb[2] * 114) / 1000
    outline_color = (0, 0, 0) if text_brightness > 127 else (255, 255, 255)

    return text_rgb, outline_color


def get_actual_text_width(
    text, lang_code, preferred_font_path, font_size, char_by_char=False
):
    """Calculate the actual rendered width of text."""
    font_path = get_font_for_lang(lang_code, text, preferred_font_path)
    if not font_path:
        return 0, 0, 0
    font = ImageFont.truetype(font_path, font_size)
    temp_image = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(temp_image)

    if char_by_char:
        if not text:
            return 0, 0, 0
        w_advance = 0
        b_left, b_right = 0, 0
        for i, char in enumerate(text):
            char_bbox = draw.textbbox((w_advance, 0), char, font=font)
            if i == 0:
                b_left = char_bbox[0]
            if i == len(text) - 1:
                b_right = char_bbox[2]
            w_advance += draw.textlength(char, font=font)
        return b_right - b_left, b_left, b_right
    else:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[0], bbox[2]


def create_frame(
    text, lang_code, params, config, frame_idx, total_frames, used_images_paths
):
    """Renders a single frame of the GIF."""
    width, height = (int(x) for x in params.size.split(","))
    font_size, text_width, b_left, b_right = config

    if params.use_icons:
        image, img_path = get_background_image(
            lang_code,
            (width, height),
            word=params.text or "hello",
            used_images=used_images_paths,
        )
        if img_path:
            used_images_paths.add(img_path)
    else:
        bg_color = tuple(map(int, params.background_color.split(",")))
        image = Image.new("RGB", (width, height), color=bg_color)

    draw = ImageDraw.Draw(image)
    font_path = get_font_for_lang(lang_code, text, params.font_path)
    if not font_path:
        return image
    font = ImageFont.truetype(font_path, font_size)

    x = (width - (b_left + b_right)) / 2
    y = (height - font_size) / 2
    bbox = draw.textbbox((x, y), text, font=font)

    # Multi-color logic
    if params.use_flag_colors or params.rainbow:
        char_colors = (
            get_rainbow_colors_for_text(text, frame_idx, total_frames)
            if params.rainbow
            else get_flag_colors_for_text(text, lang_code)
        )
        outline_color = (
            (64, 64, 64)
            if params.use_flag_colors
            else (
                get_contrast_colors(image, bbox)[1]
                if (params.use_icons or params.smart_color)
                else None
            )
        )
        stroke_width = max(2, font_size // 15) if outline_color else 0

        current_x = x
        for i, char in enumerate(text):
            draw.text(
                (current_x, y),
                char,
                font=font,
                fill=char_colors[i % len(char_colors)],
                stroke_width=stroke_width,
                stroke_fill=outline_color,
            )
            current_x += draw.textlength(char, font=font)
    else:
        if params.use_icons or params.smart_color:
            color, outline_color = get_contrast_colors(
                image, bbox, default_color=tuple(map(int, params.font_color.split(",")))
            )
            stroke_width = max(2, font_size // 15)
        else:
            color = tuple(map(int, params.font_color.split(",")))
            outline_color = None
            stroke_width = 0
        draw.text(
            (x, y),
            text,
            font=font,
            fill=color,
            stroke_width=stroke_width,
            stroke_fill=outline_color,
        )

    # Optional labels
    if getattr(params, "show_labels", False):
        country = LANG_TO_COUNTRY.get(lang_code, "Unknown")
        label = f"{EPONYMS.get(country, country).capitalize()} ({lang_code})"
        label_font_size = max(10, height // 20)
        label_font_path = get_font_for_lang("en", label, None)
        if label_font_path:
            try:
                label_font = ImageFont.truetype(label_font_path, label_font_size)
                l_bbox = draw.textbbox((0, 0), label, font=label_font)
                lx = (width - (l_bbox[2] - l_bbox[0])) / 2
                ly = height - label_font_size - 10
                draw.text(
                    (lx, ly),
                    label,
                    font=label_font,
                    fill=(200, 200, 200),
                    stroke_width=1,
                    stroke_fill=(0, 0, 0),
                )
            except:
                pass

    return image
