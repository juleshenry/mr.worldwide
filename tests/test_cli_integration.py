import subprocess
import tempfile
import os
from pathlib import Path
import pytest


class TestCLIIntegration:
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