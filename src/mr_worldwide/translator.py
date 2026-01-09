import argostranslate.package
import argostranslate.translate
import argostranslate.apis
import urllib.error
from typing import List, Optional, Dict, Tuple
from abc import ABC, abstractmethod
from .logger import get_logger

logger = get_logger(__name__)

class BaseTranslator(ABC):
    """Abstract base class for translation providers"""

    @abstractmethod
    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """Translate text from one language to another"""
        pass

    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes"""
        pass

class ArgosTranslator(BaseTranslator):
    """Argos Translate implementation"""

    def __init__(self, offline: bool = False):
        self.translation_cache: Dict[Tuple[str, str, str], Optional[str]] = {}
        self.offline = offline

    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """Translate using Argos Translate"""
        return self._from_to_text(from_lang, to_lang, text)

    def get_installed_languages(self) -> List[str]:
        """Get list of languages from installed packages"""
        try:
            installed_packages = argostranslate.package.get_installed_packages()
            languages = set()
            for package in installed_packages:
                languages.add(package.from_code)
                languages.add(package.to_code)
            return list(languages)
        except Exception as e:
            logger.error(f"Error getting installed languages: {e}")
            return []

    def get_installed_targets(self, from_code: str) -> List[str]:
        """Return target language codes that are installed for a given source language."""
        try:
            installed_packages = argostranslate.package.get_installed_packages()
            targets = {p.to_code for p in installed_packages if p.from_code == from_code}
            return sorted(targets)
        except Exception as e:
            logger.error(f"Error getting installed translation targets for '{from_code}': {e}")
            return []

    def get_supported_languages(self) -> List[str]:
        """Get supported languages from Argos"""
        if self.offline:
            return self.get_installed_languages()

        try:
            return [x["code"] for x in argostranslate.apis.LibreTranslateAPI().languages()]
        except Exception as e:
            logger.warning(f"Error getting supported languages from API: {e}. Falling back to installed packages.")
            return self.get_installed_languages()

    def validate_languages(self, languages: List[str]) -> List[str]:
        all_langs = self.get_supported_languages()
        if not all_langs:
            logger.warning("No supported languages found.")
            return []

        if "all" in languages or languages == ["all"]:
            return all_langs
        
        if any(l not in all_langs for l in languages):
            # Instead of raising error, maybe just log warning and filter?
            # For now, keeping original behavior but logging
            logger.warning(f"Some languages in {languages} might not be supported.")
            # raise ValueError(f"Invalid lang supplied in following list: {languages}")
        return languages

    def _from_to_text(self, from_code: str, to_code: str, text: str) -> Optional[str]:
        # Check cache first
        cache_key = (from_code, to_code, text)
        if cache_key in self.translation_cache:
            logger.debug(f"Cache hit for translation: {from_code}->{to_code} '{text}'")
            return self.translation_cache[cache_key]

        # Try to download package if not offline
        if not self.offline:
            try:
                argostranslate.package.update_package_index()
                available_packages = argostranslate.package.get_available_packages()

                # FROM 2 TO
                package_to_install = next(
                    filter(
                        lambda x: (x.from_code == from_code and x.to_code == to_code),
                        available_packages,
                    ), None
                )
                if package_to_install:
                    argostranslate.package.install_from_path(package_to_install.download())
            except Exception as e:
                logger.warning(f"Could not download package for {from_code}->{to_code}: {e}")

        # Translate
        try:
            tt = argostranslate.translate.translate(text, from_code, to_code)
            # Cache the result
            self.translation_cache[cache_key] = tt
            logger.debug(f"Cached translation: {from_code}->{to_code} '{text}' -> '{tt}'")
            return tt
        except Exception as e:
            logger.error(f"Translation error ({from_code}->{to_code}): {e}")
            self.translation_cache[cache_key] = None
            return None


class GoogleTranslator(BaseTranslator):
    """Google Translate implementation (placeholder)"""

    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """Placeholder for Google Translate API"""
        logger.warning("Google Translate not implemented yet")
        return None

    def get_supported_languages(self) -> List[str]:
        """Placeholder for Google Translate supported languages"""
        # This would need to query Google Translate API
        logger.warning("Google Translate languages not implemented yet")
        return []


class DeepLTranslator(BaseTranslator):
    """DeepL Translate implementation (placeholder)"""

    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """Placeholder for DeepL API"""
        logger.warning("DeepL Translate not implemented yet")
        return None

    def get_supported_languages(self) -> List[str]:
        """Placeholder for DeepL supported languages"""
        logger.warning("DeepL languages not implemented yet")
        return []


class Translator:
    """Main translator class that can use different providers"""

    def __init__(self, provider: str = "argos", offline: bool = False):
        self.provider = provider.lower()
        if self.provider == "argos":
            self.translator = ArgosTranslator(offline=offline)
        elif self.provider == "google":
            self.translator = GoogleTranslator()
        elif self.provider == "deepl":
            self.translator = DeepLTranslator()
        else:
            logger.warning(f"Unknown provider '{provider}', falling back to argos")
            self.translator = ArgosTranslator(offline=offline)

    def validate_languages(self, languages: List[str]) -> List[str]:
        all_langs = self.translator.get_supported_languages()
        if "all" in languages or languages == ["all"]:
            return all_langs

        if any(l not in all_langs for l in languages):
            raise ValueError(f"Invalid lang supplied in following list: {languages}")
        return languages

    def get_translations(self, text: str, languages: List[str]) -> List[str]:
        """
        languages must be a list of language codes
        """
        from_code = "en"
        trans = [text]

        # Validate and expand languages if needed
        try:
            target_languages = self.validate_languages(languages)
        except urllib.error.HTTPError:
            logger.error("Unable to reach translation server. Translating disabled.")
            target_languages = []

        # In offline Argos mode, "all" should mean "all installed en->X targets",
        # not "all language codes seen in packages".
        if ("all" in languages or languages == ["all"]) and isinstance(self.translator, ArgosTranslator) and self.translator.offline:
            target_languages = self.translator.get_installed_targets(from_code)

        if not target_languages and languages:
            raise ValueError(
                "No target languages available for translation. "
                "If you're using --offline, you must install Argos translation packages (e.g. en->es) first."
            )

        failures = 0
        attempted = 0

        for to_code in target_languages:
            if to_code == from_code:
                continue

            attempted += 1
            translated_text = self.translator.translate(text, from_code, to_code)
            if translated_text and translated_text != text:
                # Clean up translation
                cleaned = translated_text.replace("*", "").replace(".", "").replace("!", "")
                trans.append(cleaned)
            else:
                failures += 1

        if attempted > 0 and len(trans) == 1:
            logger.warning(
                "No translations were produced (all attempts failed or returned unchanged text). "
                "This often means the required Argos packages are not installed for 'en-><lang>' in offline mode."
            )

        return trans
