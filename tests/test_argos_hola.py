import pytest
from unittest.mock import patch, MagicMock
from argos_hola import get_trans, from_to_text


class TestFromToText:
    @patch('argos_hola.argostranslate.package.update_package_index')
    @patch('argos_hola.argostranslate.package.get_available_packages')
    @patch('argos_hola.argostranslate.package.install_from_path')
    @patch('argos_hola.argostranslate.translate.translate')
    def test_from_to_text_success(self, mock_translate, mock_install, mock_get_packages, mock_update):
        # Mock the package installation process
        mock_package = MagicMock()
        mock_package.download.return_value = 'fake_path'
        mock_get_packages.return_value = [mock_package]
        mock_translate.return_value = 'Hola Mundo'

        result = from_to_text('en', 'es', 'Hello World')

        assert result == 'Hola Mundo'
        mock_translate.assert_called_once_with('Hello World', 'en', 'es')

    @patch('argos_hola.argostranslate.package.update_package_index')
    @patch('argos_hola.argostranslate.package.get_available_packages')
    def test_from_to_text_no_package(self, mock_get_packages, mock_update):
        # No package available for the language pair
        mock_get_packages.return_value = []

        result = from_to_text('en', 'es', 'Hello World')

        assert result is None

    @patch('argos_hola.argostranslate.package.update_package_index')
    @patch('argos_hola.argostranslate.package.get_available_packages')
    @patch('argos_hola.argostranslate.package.install_from_path')
    @patch('argos_hola.argostranslate.translate.translate')
    def test_from_to_text_translation_error(self, mock_translate, mock_install, mock_get_packages, mock_update):
        # Translation fails
        mock_package = MagicMock()
        mock_package.download.return_value = 'fake_path'
        mock_get_packages.return_value = [mock_package]
        mock_translate.side_effect = Exception('Translation failed')

        result = from_to_text('en', 'es', 'Hello World')

        assert result is None


class TestGetTrans:
    @patch('argos_hola.from_to_text')
    def test_get_trans_single_language(self, mock_from_to_text):
        mock_from_to_text.return_value = 'Hola'

        result = get_trans('Hello', ['es'])

        assert result == ['Hello', 'Hola']

    @patch('argos_hola.from_to_text')
    def test_get_trans_multiple_languages(self, mock_from_to_text):
        mock_from_to_text.side_effect = ['Hola', 'Bonjour', None]  # None for unsupported language

        result = get_trans('Hello', ['es', 'fr', 'de'])

        assert result == ['Hello', 'Hola', 'Bonjour']

    @patch('argos_hola.from_to_text')
    def test_get_trans_same_language(self, mock_from_to_text):
        # Should skip English to English
        result = get_trans('Hello', ['en'])

        assert result == ['Hello']
        mock_from_to_text.assert_not_called()

    @patch('argos_hola.from_to_text')
    def test_get_trans_identical_translation(self, mock_from_to_text):
        # If translation is same as original, skip
        mock_from_to_text.return_value = 'Hello'

        result = get_trans('Hello', ['es'])

        assert result == ['Hello']

    def test_get_trans_no_languages(self):
        # Test with None languages (should handle gracefully or raise error)
        with pytest.raises(TypeError):
            get_trans('Hello', None)