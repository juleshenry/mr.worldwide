import argostranslate.package
import argostranslate.translate
import argostranslate.apis
import urllib.error
from typing import List, Optional
from .logger import get_logger

logger = get_logger(__name__)

class Translator:
    def __init__(self):
        pass

    def validate_languages(self, languages: List[str]) -> List[str]:
        try:
            all_langs = [x["code"] for x in argostranslate.apis.LibreTranslateAPI().languages()]
            if "all" in languages or languages == ["all"]:
                return all_langs
            
            if any(l not in all_langs for l in languages):
                raise ValueError(f"Invalid lang supplied in following list: {languages}")
            return languages
        except urllib.error.HTTPError:
            logger.error('Unable to reach argos server. Translating disabled.')
            return []
        except Exception as e:
            logger.error(f"Error validating languages: {e}")
            return []

    def _from_to_text(self, from_code: str, to_code: str, text: str) -> Optional[str]:
        # Download and install Argos Translate package
        try:
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # FROM 2 TO
            package_to_install = list(
                filter(
                    lambda x: (x.from_code == from_code and x.to_code == to_code),
                    available_packages,
                )
            )[0]
            argostranslate.package.install_from_path(package_to_install.download())
            # Translate
            tt = argostranslate.translate.translate(text, from_code, to_code)
            return tt
        except IndexError:
            logger.warning(f"No translation package found for {from_code}->{to_code}")
            return None
        except Exception as e:
            logger.error(f"Translation error ({from_code}->{to_code}): {e}")
            return None

    def get_translations(self, text: str, languages: List[str]) -> List[str]:
        """
        languages must be a list of language codes
        """
        from_code = "en"
        trans = [text]
        
        # Validate and expand languages if needed
        target_languages = self.validate_languages(languages)
        
        for to_code in target_languages:
            if to_code == from_code:
                continue
            
            translated_text = self._from_to_text(from_code, to_code, text)
            if translated_text and translated_text != text:
                # Clean up translation
                cleaned = translated_text.replace("*", "").replace(".", "".replace("!", ""))
                trans.append(cleaned)
                
        return trans
