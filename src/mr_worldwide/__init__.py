from __future__ import annotations

import argparse
from functools import wraps
from typing import Iterable, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

from .config import Config
from .gif_generator import GifGenerator
from .translator import Translator

# Backwards-compatible, module-level API expected by older callers/tests.

lang_fudge = {"ja": 4.2, "ko": 4}


def get_max_width(trans: Sequence[str], languages: Sequence[str], font_size: int) -> int:
	"""Estimate a max width using language-specific fudge factors."""
	mx = 0.0
	for t, l in zip(trans, languages):
		adj_len = len(t) * lang_fudge.get(l, 2.1) * font_size
		mx = adj_len if mx < adj_len else mx
	return int(mx)


def sine_adder(frames: Sequence[Image.Image], d: int) -> List[Image.Image]:
	"""Expand frames using the original sine-delay expansion algorithm."""
	nf: List[Image.Image] = []
	for robin in range(len(frames)):
		for pre in frames[0:robin]:
			nf.append(pre)
		for _ in range(d):
			nf.append(frames[robin])
		for post in frames[robin + 1 :]:
			nf.append(post)
	return nf


def get_trans(text: str, *, languages: Sequence[str] | None = None) -> List[str]:
	"""Legacy helper: translate text into the requested languages."""
	if languages is None:
		languages = ["all"]
	return Translator().get_translations(text, list(languages))


def _parse_size(size: str) -> Tuple[int, int]:
	w_str, h_str = size.split(",")
	return int(w_str), int(h_str)


def _parse_rgb(rgb: str) -> Tuple[int, int, int]:
	r, g, b = rgb.split(",")
	return int(r), int(g), int(b)


class _LegacyGifCreator:
	def create_image(
		self,
		text: str,
		font_path: str,
		font_color: Tuple[int, int, int],
		background_color: Tuple[int, int, int],
		*,
		size: Tuple[int, int] = (256, 256),
		font_size: int = 32,
	) -> Image.Image:
		image = Image.new("RGB", size, color=background_color)
		draw = ImageDraw.Draw(image)
		font = ImageFont.truetype(font_path, font_size)
		draw.text((0, 0), text, font=font, fill=font_color)
		return image


_DEFAULT_CREATOR = _LegacyGifCreator()


def _create_gif(params, creator: _LegacyGifCreator = _DEFAULT_CREATOR):
	text = getattr(params, "text", None)
	text_array = getattr(params, "text_array", None)
	if not text and not text_array:
		raise ValueError("need text or text array")

	size_str = getattr(params, "size", "256,256")
	width, height = _parse_size(size_str)

	if text:
		languages = list(getattr(params, "languages", []))
		trans = get_trans(text, languages=languages)
		max_width = get_max_width(trans, languages, int(getattr(params, "font_size", 32)))
		frame_texts = trans
		frame_width = max_width
	else:
		frame_texts = [t.strip() for t in str(text_array).split(",") if t.strip()]
		frame_width = width

	font_path = getattr(params, "font_path", "fonts/arial.ttf")
	font_color = getattr(params, "font_color", (255, 255, 255))
	background_color = getattr(params, "background_color", (0, 0, 0))
	font_size = int(getattr(params, "font_size", 32))

	frames = [
		creator.create_image(
			t,
			font_path,
			font_color,
			background_color,
			size=(frame_width, height),
			font_size=font_size,
		)
		for t in frame_texts
	]

	delay = int(getattr(params, "delay", 100))
	sine_delay = int(getattr(params, "sine_delay", 0) or 0)
	if sine_delay > 0 and delay > 0:
		d = sine_delay // delay
		frames = sine_adder(frames, d)

	gif_path = getattr(params, "gif_path", "mr_worldwide.gif")
	frames[0].save(
		gif_path,
		save_all=True,
		append_images=frames[1:],
		loop=0,
		duration=delay,
	)


@wraps(_create_gif)
def create_gif(params, creator: _LegacyGifCreator = _DEFAULT_CREATOR):
	return _create_gif(params, creator=creator)


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--text")
	parser.add_argument("--text-array")
	parser.add_argument("--delay", type=int, default=100)
	parser.add_argument("--sine-delay", type=int, default=0)
	parser.add_argument("--font-color", default="255,255,255")
	parser.add_argument("--background-color", default="0,0,0")
	parser.add_argument("--font-path", default="fonts/arial.ttf")
	parser.add_argument("--font-size", type=int, default=32)
	parser.add_argument("--languages", nargs="*", default=["all"])
	parser.add_argument("--size", default="256,256")
	parser.add_argument("--gif-path", default="mr_worldwide.gif")
	args = parser.parse_args()

	if isinstance(args.font_color, str):
		args.font_color = _parse_rgb(args.font_color)
	if isinstance(args.background_color, str):
		args.background_color = _parse_rgb(args.background_color)

	create_gif(args)
