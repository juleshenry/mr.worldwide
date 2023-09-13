'''
import argostranslate.package
import argostranslate.translate

from_code = "en"
to_code = "es"

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())

# Translate
translatedText = argostranslate.translate.translate("Hello World", from_code, to_code)
print(translatedText)
# '¡Hola Mundo!'
'''
import argostranslate.package
import argostranslate.translate



def from_to_text(from_code,to_code,text):
    # Download and install Argos Translate package
    argostranslate.package.update_package_index()
    try:
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
            )
        )
        argostranslate.package.install_from_path(package_to_install.download())

        # Translate
        tt = argostranslate.translate.translate(text, from_code, to_code)
        return tt
    except:
        return None

def get_trans(text, languages=None):
    '''
    languages must be a list of 
    '''
    all_langs = [x['code'] for x in argostranslate.apis.LibreTranslateAPI().languages()]
    if any(l not in all_langs for l in languages):
        raise ValueError(f"Invalid lang supplied in following list: {languages}")
    if not languages:
        languages = all_langs
    from_code = "en"
    trans =[]
    for to_code in languages:
        if to_code == from_code:continue
        if text!=(u:=from_to_text(from_code,to_code,text)) and u:
            print(u)
            trans+=[u.replace('*','')]
    return trans

if __name__=='__main__':
    text = "Hello"
    get_trans(text)
# '¡Hola Mundo!'    