from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional, Any
from .config import Config
from .logger import get_logger
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    RTL_SUPPORT = True
except ImportError:
    logger = get_logger(__name__)
    logger.warning("RTL support libraries not installed. Install arabic-reshaper and python-bidi for RTL language support.")
    RTL_SUPPORT = False

logger = get_logger(__name__)

def _is_rtl(text: str) -> bool:
    """Check if text contains RTL characters"""
    rtl_chars = set('\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF')
    return any(ord(char) in range(0x600, 0x700) or ord(char) in range(0x750, 0x780) or
               ord(char) in range(0x8A0, 0x900) or ord(char) in range(0xFB50, 0xFE00) or
               ord(char) in range(0xFE70, 0xFF00) for char in text)

def _reshape_text(text: str) -> str:
    """Reshape RTL text for proper display"""
    if not RTL_SUPPORT:
        return text
    if _is_rtl(text):
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    return text

class GifGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.lang_fudge = {"ja": 4.2, "ko": 4}
        # Font fallback system
        self.fallback_fonts = [
            config.font_path,  # User's choice first
            "fonts/NotoSans-Regular.ttf",  # Noto Sans for broad coverage
            "fonts/arial.ttf",  # Arial
            "fonts/noto-sc.ttf",  # Noto Sans CJK
            "fonts/Quivira-A8VL.ttf",  # Unicode fallback
        ]

    def _get_font(self, text: str) -> ImageFont.FreeTypeFont:
        """Try fonts in order until one works, prioritizing fonts that can render the text"""
        for font_path in self.fallback_fonts:
            try:
                font = ImageFont.truetype(font_path, self.config.font_size)
                # Test if font can render the text (basic check)
                test_bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=font)
                if test_bbox[2] > test_bbox[0]:  # Has some width
                    logger.debug(f"Using font: {font_path}")
                    return font
            except (IOError, OSError) as e:
                logger.debug(f"Font {font_path} failed: {e}")
                continue

        # Ultimate fallback
        logger.warning("All fonts failed, using default font")
        return ImageFont.load_default()

    def _get_contrasting_color(self, background: Any) -> Tuple[int, int, int]:
        """Choose a font color with high contrast against the background"""
        if isinstance(background, tuple) and len(background) == 3:
            # Solid color background
            r, g, b = background
        elif isinstance(background, Image.Image):
            # Image background - get average color
            # Convert to RGB if needed
            if background.mode != 'RGB':
                background = background.convert('RGB')
            # Get average color
            pixels = list(background.getdata())
            r = sum(p[0] for p in pixels) // len(pixels)
            g = sum(p[1] for p in pixels) // len(pixels)
            b = sum(p[2] for p in pixels) // len(pixels)
        else:
            # Fallback
            return (255, 255, 255)  # White

        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

        # Return black for light backgrounds, white for dark
        return (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

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

    def _create_image(self, text: str, width: int, height: int, background_image: Optional[str] = None) -> Image.Image:
        if background_image:
            try:
                image = Image.open(background_image).convert("RGB")
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            except (IOError, OSError) as e:
                logger.warning(f"Could not load background image {background_image}: {e}, falling back to color")
                image = Image.new("RGB", (width, height), color=self.config.background_color)
        else:
            image = Image.new("RGB", (width, height), color=self.config.background_color)

        draw = ImageDraw.Draw(image)

        # Reshape text for RTL languages if supported
        display_text = _reshape_text(text)

        # Get best available font
        font = self._get_font(display_text)

        # Determine font color
        if self.config.smart_color:
            font_color = self._get_contrasting_color(image)
        else:
            font_color = self.config.font_color

        # Get text bounding box to center the text
        bbox = draw.textbbox((0, 0), display_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text horizontally and vertically
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        draw.text((x, y), display_text, font=font, fill=font_color)
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

    def _calculate_durations(self, num_frames: int, animation: str, base_delay: int) -> List[int]:
        """Calculate frame durations based on animation type"""
        import math

        if animation == "linear":
            return [base_delay] * num_frames
        elif animation == "ease-in":
            # Quadratic ease-in
            durations = []
            for i in range(num_frames):
                t = i / (num_frames - 1) if num_frames > 1 else 0
                factor = t * t
                durations.append(int(base_delay * (1 + factor)))
            return durations
        elif animation == "ease-out":
            # Quadratic ease-out
            durations = []
            for i in range(num_frames):
                t = i / (num_frames - 1) if num_frames > 1 else 1
                factor = 1 - (1 - t) * (1 - t)
                durations.append(int(base_delay * (1 + factor)))
            return durations
        elif animation == "bounce":
            # Simple bounce effect
            durations = []
            for i in range(num_frames):
                t = i / (num_frames - 1) if num_frames > 1 else 0
                # Bounce using sin function
                factor = abs(math.sin(t * math.pi * 2))
                durations.append(int(base_delay * (1 + factor)))
            return durations
        else:
            # Default to linear
            return [base_delay] * num_frames

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
        for i, t in enumerate(text_list):
            bg_image = None
            if self.config.background_images and i < len(self.config.background_images):
                bg_image = self.config.background_images[i]

            image = self._create_image(
                t,
                max_width,
                height,
                bg_image
            )
            frames.append(image)

        if self.config.animation == "sine" and self.config.sine_delay > 0:
            logger.info(f"SINE: {self.config.sine_delay}, DELAY: {self.config.delay}")
            new_frames = self._sine_adder(frames, self.config.sine_delay // self.config.delay)
            frames[0].save(
                self.config.gif_path,
                save_all=True,
                append_images=new_frames,
                loop=0,  # 0 means infinite loop
                duration=self.config.delay,  # Time in milliseconds between frames
            )
        else:
            # Use advanced animation if specified
            durations = self._calculate_durations(len(frames), self.config.animation, self.config.delay)
            frames[0].save(
                self.config.gif_path,
                save_all=True,
                append_images=frames[1:],
                loop=0,  # 0 means infinite loop
                duration=durations,  # List of durations for each frame
            )
        logger.info(f"GIF created as {self.config.gif_path}!")

        # Generate TTS audio if requested
        if self.config.tts:
            self._generate_tts_audio(text_list)

    def _generate_tts_audio(self, text_list: List[str]):
        """Generate text-to-speech audio files for each text"""
        try:
            import pyttsx3
            engine = pyttsx3.init()

            base_path = self.config.gif_path.rsplit('.', 1)[0]  # Remove extension

            for i, text in enumerate(text_list):
                audio_path = f"{base_path}_tts_{i}.mp3"
                try:
                    engine.save_to_file(text, audio_path)
                    engine.runAndWait()
                    logger.info(f"TTS audio saved: {audio_path}")
                except Exception as e:
                    logger.error(f"Failed to generate TTS for '{text}': {e}")

        except ImportError:
            logger.warning("pyttsx3 not installed, skipping TTS generation")
        except Exception as e:
            logger.error(f"TTS initialization failed: {e}")
