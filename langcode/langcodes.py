from pyetymology.langcode import famcodes, etycodes, gencodes


def name(code, use_ety=False, use_fam=False) -> str:
    val = gencodes.m.get(code, None)
    if val is None and use_ety:
        dict = etycodes.m.get(code, None)
        if dict is not None:
            val = dict["canonicalName"]
    if val is None and use_fam:
        dict = famcodes.m.get(code, None)
        if dict is not None:
            val = dict["canonicalName"]
    return val

def is_reconstr(code) -> bool:
    return code[-4:] == "-pro"

def is_name_reconstr(langname) -> bool:

    return langname.startswith("Proto-")