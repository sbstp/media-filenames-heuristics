from pycountry import languages as _languages

_ALPHA_2 = dict()
_ALPHA_3 = dict()
_BIBLIOGRAPHIC = dict()
_NAME = dict()


def _load():
    global _ALPHA_2, _ALPHA_3, _BIBLIOGRAPHIC, _NAME
    for lang in _languages:
        alpha_2 = getattr(lang, 'alpha_2', None)
        if alpha_2:
            _ALPHA_2[alpha_2] = lang
        alpha_3 = getattr(lang, 'alpha_3', None)
        if alpha_3:
            _ALPHA_3[alpha_3] = lang
        bibliographic = getattr(lang, 'bibliographic', None)
        if bibliographic:
            _BIBLIOGRAPHIC[bibliographic] = lang
        _NAME[lang.name.lower()] = lang


_load()


def lookup(text):
    global _ALPHA_2, _ALPHA_3, _BIBLIOGRAPHIC, _NAME

    text = text.lower()
    size = len(text)
    val = None

    if size == 2:
        val = _ALPHA_2.get(text)
    elif size == 3:
        val = _BIBLIOGRAPHIC.get(text)
        if not val:
            val = _ALPHA_3.get(text)

    if not val:
        val = _NAME.get(text)

    if not val:
        # Needs more testing. Fixes greek.
        candidates = [lang for name, lang in _NAME.items() if text in name and lang.type == 'L']
        if candidates:
            candidates.sort(key=lambda c: 0 if getattr(c, 'bibliographic', None) is not None else 1)
            val = candidates[0]

    return val


def get_code(lang):
    if not lang:
        return None
    code = getattr(lang, 'bibliographic', None)
    if not code:
        code = lang.alpha_3
    return code
