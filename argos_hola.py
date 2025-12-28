import argostranslate.package
import argostranslate.translate
from typing import Optional, List
from concurrent.futures import ProcessPoolExecutor, as_completed


def from_to_text(from_code: str, to_code: str, text: str) -> Optional[str]:
    # Download and install Argos Translate package
    argostranslate.package.update_package_index()
    # try:
    available_packages = argostranslate.package.get_available_packages()
    try:
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
    except IndexError as ie:
        return None
    # print(to_code, len(tt), tt)
    return tt


def get_trans(text: str, languages: Optional[List[str]] = None) -> List[str]:
    """
    languages must be a list of language codes
    """
    if not languages:
        return [text]

    from_code = "en"
    trans = [text]

    # Prepare translation tasks for languages different from source
    translation_tasks = [
        (from_code, to_code, text) for to_code in languages
        if to_code != from_code
    ]

    # Use ProcessPoolExecutor for parallel translation
    with ProcessPoolExecutor() as executor:
        # Submit all translation tasks
        future_to_lang = {
            executor.submit(_translate_single, task): task[1]
            for task in translation_tasks
        }

        # Collect results as they complete
        for future in as_completed(future_to_lang):
            lang_code = future_to_lang[future]
            try:
                result = future.result()
                if result and result != text:
                    cleaned_result = result.replace("*", "").replace(".", "").replace("!", "")
                    trans.append(cleaned_result)
            except Exception as exc:
                print(f'Translation for {lang_code} generated an exception: {exc}')

    return trans


def _translate_single(args):
    """Helper function for parallel translation - must be at module level for pickling"""
    from_code, to_code, text = args
    return from_to_text(from_code, to_code, text)


if __name__ == "__main__":
    text = "The pretty girl has a bouquet of red flags"
    get_trans(text)
# '¡Hola Mundo!'
