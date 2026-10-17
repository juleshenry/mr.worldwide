import numpy as np
import colorsys
import unicodedata
from itertools import accumulate
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


def get_actual_text_width(text, lang_code, preferred_font_path, font_size):
    """Calculate the actual rendered width of text."""
    font_path = get_font_for_lang(lang_code, text, preferred_font_path)
    if not font_path:
        return 0, 0, 0
    font = ImageFont.truetype(font_path, font_size)
    temp_image = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(temp_image)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[0], bbox[2]


def get_text_vertical_bounds(draw, text, font):
    """Top and bottom of the inked text when drawn at y=0."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[1], bbox[3]


ZERO_WIDTH_JOINERS = ("\u200c", "\u200d")


def split_clusters(text):
    """
    Splits text into the units that get one colour each: a letter with its combining
    marks, and virama-joined conjuncts (Indic, Khmer, Myanmar) kept whole.
    """
    clusters = []
    for char in text:
        prev = clusters[-1][-1] if clusters else None
        if prev is not None and (
            unicodedata.category(char).startswith("M")
            or char in ZERO_WIDTH_JOINERS
            or prev in ZERO_WIDTH_JOINERS
            or unicodedata.combining(prev) == 9  # virama
        ):
            clusters[-1] += char
        else:
            clusters.append(char)
    return clusters


def is_rtl(text):
    """Whether the first strongly-directional character is right-to-left."""
    for char in text:
        direction = unicodedata.bidirectional(char)
        if direction in ("R", "AL"):
            return True
        if direction == "L":
            return False
    return False


def draw_multicolor_text(image, xy, clusters, font, colors, stroke_width=0, stroke_fill=None):
    """
    Draws the text as one shaped run, so Arabic letters join, Hebrew runs right to left
    and Indic marks stay on their letters, then fills each cluster's span in its colour.
    """
    text = "".join(clusters)
    draw = ImageDraw.Draw(image)
    if stroke_width and stroke_fill:
        draw.text(
            xy, text, font=font, fill=stroke_fill, stroke_width=stroke_width, stroke_fill=stroke_fill
        )
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255)

    # Where each cluster starts, from the shaped width of the text before it
    total = draw.textlength(text, font=font)
    rtl = is_rtl(text)
    lefts, offset = [], 0
    for cluster in clusters:
        start = draw.textlength(text[:offset], font=font)
        offset += len(cluster)
        end = draw.textlength(text[:offset], font=font)
        lefts.append(total - end if rtl else start)

    order = list(range(len(clusters)))[:: -1 if rtl else 1]  # left to right on screen
    cuts = [0] + [round(xy[0] + lefts[i]) for i in order[1:]] + [image.width]
    cuts = list(accumulate(cuts, max))
    for k, i in enumerate(order):
        x0, x1 = max(0, cuts[k]), min(image.width, cuts[k + 1])
        if x1 > x0:
            box = (x0, 0, x1, image.height)
            image.paste(colors[i % len(colors)], box, mask.crop(box))


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

    # Centre the ink, not the font's em box: scripts with tall line metrics
    # (Arabic, Tibetan, Myanmar) otherwise sit far below the middle.
    x = (width - (b_left + b_right)) / 2
    b_top, b_bottom = get_text_vertical_bounds(draw, text, font)
    y = (height - (b_top + b_bottom)) / 2
    bbox = draw.textbbox((x, y), text, font=font)

    # Multi-color logic
    if params.use_flag_colors or params.rainbow:
        clusters = split_clusters(text)
        cluster_colors = (
            get_rainbow_colors_for_text(clusters, frame_idx, total_frames)
            if params.rainbow
            else get_flag_colors_for_text(clusters, lang_code)
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
        draw_multicolor_text(
            image, (x, y), clusters, font, cluster_colors, stroke_width, outline_color
        )
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
