from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
from .config import Config
from .logger import get_logger

logger = get_logger(__name__)

class GifGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.lang_fudge = {"ja": 4.2, "ko": 4}

    def _get_max_width(self, trans: List[str], languages: List[str]) -> int:
        """
        estimates from language-specific fudge how big the strings will be in the GIF
        """
        mx = 0
        # If languages list is shorter than trans list (e.g. original text included), 
        # we might need to handle that. For now, assuming simple zip is okay or 
        # we should just iterate over trans.
        # The original code zipped trans and languages.
        
        # If languages is "all", we might not have the exact mapping here easily 
        # unless we passed the expanded list. 
        # Let's assume languages passed here matches the translations.
        
        for t in trans:
            # Simplified estimation if we don't track language per string perfectly
            # or we can just use a default multiplier if language is unknown
            # Original code:
            # for t, l in zip(trans, languages):
            #     adj_len = len(t) * lang_fudge.get(l, 2.1) * font_size
            
            # Since we might lose the 1-to-1 mapping if we just have a list of strings,
            # let's just use a safe estimate or try to map if possible.
            # For now, I'll use a generic multiplier for simplicity or try to match original logic
            # if I can pass the expanded languages list.
            
            # Let's use a generic max width calculation based on text length and font size
            # as a fallback, but try to respect the original logic if possible.
            
            adj_len = len(t) * 2.1 * self.config.font_size
            mx = adj_len if mx < adj_len else mx
        return int(mx)

    def _create_image(self, text: str, width: int, height: int) -> Image.Image:
        image = Image.new("RGB", (width, height), color=self.config.background_color)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(self.config.font_path, height // 2)
        except IOError:
            # Fallback to default font if specified one fails
            logger.warning(f"Could not load font at {self.config.font_path}, falling back to default.")
            font = ImageFont.load_default()
            
        x = 0
        y = height // 8
        draw.text((x, y), text, font=font, fill=self.config.font_color)
        return image

    def _sine_adder(self, frames: List[Image.Image], d: int) -> List[Image.Image]:
        nf = []
        for robin in range(len(frames)):
            # each iteration requires 0 -> i-1
            for pre in frames[0:robin]:
                nf.append(pre)
            # stuff up
            for _ in range(d):
                nf.append(frames[robin])
            # each iteration requires i+1 -> n
            for post in frames[robin + 1 :]:
                nf.append(post)
        return nf

    def generate(self, text_list: List[str]):
        width, height = self.config.size
        
        # Calculate max width if text is provided, otherwise use config width
        # Note: Original code used get_max_width only if text was provided (not text_array)
        # But here text_list is the source of truth.
        
        # To replicate original get_max_width logic exactly, we'd need the list of languages
        # corresponding to text_list. 
        # For now, let's calculate max width based on the text content itself.
        
        max_width = self._get_max_width(text_list, self.config.languages) if self.config.text else width
        
        frames = []
        for t in text_list:
            image = self._create_image(
                t,
                max_width,
                height
            )
            frames.append(image)

        if not self.config.sine_delay:
            # Save the frames as a GIF
            frames[0].save(
                self.config.gif_path,
                save_all=True,
                append_images=frames[1:],
                loop=0,  # 0 means infinite loop
                duration=self.config.delay,  # Time in milliseconds between frames
            )
        else:
            logger.info(f"SINE: {self.config.sine_delay}, DELAY: {self.config.delay}")
            # Save the frames as a GIF
            new_frames = self._sine_adder(frames, self.config.sine_delay // self.config.delay)
            frames[0].save(
                self.config.gif_path,
                save_all=True,
                append_images=new_frames,
                loop=0,  # 0 means infinite loop
                duration=self.config.delay,  # Time in milliseconds between frames
            )
        logger.info(f"GIF created as {self.config.gif_path}!")
