import argostranslate.package
import argostranslate.translate


def from_to_text(from_code, to_code, text):
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


def get_trans(text, languages=None):
    """
    languages must be a list of
    """
    from_code = "en"
    trans = [text]
    for to_code in languages:
        if to_code == from_code:
            continue
        if text != (u := from_to_text(from_code, to_code, text)) and u:
            trans += [u.replace("*", "").replace(".", "".replace("!", ""))]
    return trans


if __name__ == "__main__":
    text = "The pretty girl has a bouquet of red flags"
    get_trans(text)
# '¡Hola Mundo!'
