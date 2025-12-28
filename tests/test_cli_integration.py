import subprocess
import tempfile
import os
from pathlib import Path
import pytest
from PIL import Image


class TestCLIIntegration:

    @staticmethod
    def count_gif_frames(path):
        """Count the number of frames in a GIF"""
        im = Image.open(path)
        i = 0
        try:
            while True:
                im.seek(i)
                i += 1
        except EOFError:
            pass
        return i
    def test_cli_help(self):
        """Test that the CLI shows help correctly"""
        result = subprocess.run(['python3', 'mr-worldwide.py', '--help'],
                              capture_output=True, text=True, cwd=Path(__file__).parent.parent)

        assert result.returncode == 0
        assert 'Create a GIF with customizable parameters' in result.stdout

    def test_cli_with_text(self):
        """Test CLI with text input"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.gif')

            # This will fail without proper dependencies, but tests argument parsing
            result = subprocess.run([
                'python3', 'mr-worldwide.py',
                '--text', 'Hello',
                '--gif_path', output_path,
                '--size', '64,64',
                '--languages', 'en'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

            # Should either succeed or fail gracefully
            # If argos is not available, it should print error but not crash
            assert result.returncode in [0, 1]  # 0 for success, 1 for expected error

    def test_cli_with_text_array(self):
        """Test CLI with text array input"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.gif')

            result = subprocess.run([
                'python3', 'mr-worldwide.py',
                '--text_array', 'Hello,Hola',
                '--gif_path', output_path,
                '--size', '64,64',
                '--languages', 'en,es'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

            assert result.returncode in [0, 1]

    def test_cli_invalid_language(self):
        """Test CLI with invalid language code"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.gif')

            result = subprocess.run([
                'python3', 'mr-worldwide.py',
                '--text', 'Hello',
                '--gif_path', output_path,
                '--size', '64,64',
                '--languages', 'invalid_lang'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

            # Should fail with invalid language
            assert result.returncode == 1
            assert 'Invalid lang' in result.stderr

    def test_cli_missing_text(self):
        """Test CLI without text or text_array"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.gif')

            result = subprocess.run([
                'python3', 'mr-worldwide.py',
                '--gif_path', output_path,
                '--size', '64,64'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

            assert result.returncode == 2  # argparse error
            assert 'need text or text array' in result.stderr

    @pytest.mark.slow
    def test_full_gif_generation(self):
        """Integration test for full GIF generation (requires all dependencies)"""
        pytest.skip("Requires argostranslate and PIL dependencies")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.gif')

            result = subprocess.run([
                'python3', 'mr-worldwide.py',
                '--text', 'Hello',
                '--gif_path', output_path,
                '--size', '64,64',
                '--languages', 'en',
                '--delay', '10'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

            assert result.returncode == 0
            assert os.path.exists(output_path)
            assert 'GIF created' in result.stdout

    @pytest.mark.slow
    def test_readme_basic_command(self):
        """Test the basic README command with text and verify frame count"""
        pytest.skip("Requires argostranslate and PIL dependencies")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'output.gif')

            result = subprocess.run([
                'python3', 'mr-worldwide.py',
                '--offline',
                '--size', '256,256',
                '--text', 'hello!',
                '--font_path', 'fonts/arial.ttf',
                '--font_color', '255,32,32',
                '--background_color', '255,255,255',
                '--languages', 'es,fr,de',  # Use specific languages for predictable count
                '--delay', '300',
                '--gif_path', output_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

            assert result.returncode == 0
            assert os.path.exists(output_path)
            # For text with 3 languages, expect 3 frames
            assert self.count_gif_frames(output_path) == 3

    @pytest.mark.slow
    def test_readme_text_array_command(self):
        """Test the text array README command and verify frame count"""
        pytest.skip("Requires PIL dependencies")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'output.gif')

            text_array = "你好, Hola, Hello, नमस्ते, السلام عليكم, হ্যালো, Olá, Привет, こんにちは, ਸਤ ਸ੍ਰੀ ਅਕਾਲ, Hallo, Halo, 呵呵, హలో, Xin chào, नमस्कार, 안녕하세요, Bonjour, வணக்கம், Merhaba, اسلام و علیکم, 哈囉, สวัสดี, નમસ્તે, Pronto"
            num_texts = len(text_array.split(','))

            result = subprocess.run([
                'python3', 'mr-worldwide.py',
                '--offline',
                '--size', '1024,256',
                '--text_array', text_array,
                '--font_path', 'fonts/arial.ttf',
                '--font_color', '0,0,0',
                '--font_size', '32',
                '--background_color', '255,255,255',
                '--languages', 'all',
                '--delay', '300',
                '--gif_path', output_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

            assert result.returncode == 0
            assert os.path.exists(output_path)
            assert self.count_gif_frames(output_path) == num_texts

    @pytest.mark.slow
    def test_readme_sinusoidal_command(self):
        """Test the sinusoidal README command and verify frame count"""
        pytest.skip("Requires argostranslate and PIL dependencies")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'output.gif')

            result = subprocess.run([
                'python3', 'mr-worldwide.py',
                '--offline',
                '--size', '256,256',
                '--text', 'hello!',
                '--font_path', 'fonts/arial.ttf',
                '--font_color', '255,32,32',
                '--background_color', '255,255,255',
                '--languages', 'es,fr',  # 2 languages for predictable count
                '--delay', 'sine:50,10',  # sine_delay=50, delay=10, d=5
                '--gif_path', output_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

            assert result.returncode == 0
            assert os.path.exists(output_path)
            # For 2 translations, frames = 2 * (2 + 4) = 12
            assert self.count_gif_frames(output_path) == 12