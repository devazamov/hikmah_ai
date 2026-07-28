from locales.uz import UZ
from locales.ar import AR

LOCALES = {
    "uz": UZ,
    "ar": AR,
}


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """Get localized text by key and language."""
    locale = LOCALES.get(lang, LOCALES["uz"])
    text = getattr(locale, key, None)
    if text is None:
        text = getattr(LOCALES["uz"], key, key)
    if kwargs and isinstance(text, str):
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
