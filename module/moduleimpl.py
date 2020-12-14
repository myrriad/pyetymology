
# https://en.wiktionary.org/wiki/Module:links
import urllib
import warnings
from typing import Tuple, Union

from pyetymology.helperobjs.langhelper import Lang
from pyetymology.langcode import langcodes


def to_link(word_or_urlword: str, lang_or_none:Union[Lang, str, None] = None):
    if lang_or_none is None:
        _urlword = word_or_urlword
        return "https://en.wiktionary.com/w/api.php?action=parse&page=" + _urlword + "&prop=wikitext&formatversion=2&format=json"
    else:
        word = word_or_urlword
        lang = lang_or_none
        if isinstance(lang, str):
            return to_link(urlword(word=word, lang=lang))
        elif isinstance(lang, Lang):
            return to_link(urlword(word=word, lang=lang))
        else:
            raise TypeError(f"lang has unexpected type {type(lang)}")

def urlword(word: str, lang: Union[str, Lang, None]) -> str:  # TODO: test this

    if not lang:
        warnings.warn("retrieving urlword without a lang! language-deterministic checks such as macrons won't work!")
        return mimicked_link_keyword(word)
    if isinstance(lang, str):
        # lang is langname
        return mimicked_link_keyword(word, lang)
    assert isinstance(lang, Lang)
    if lang.reconstr:
        urllang = urllib.parse.quote_plus(lang.langname.replace(" ", "-"))  # TODO: refine this
        assert isinstance(lang.langname, str)
        return "Reconstruction:" + urllang + "/" + urlword(word, lang.langname)
    else:
        return urlword(word, lang.langname)
    raise TypeError(f"lang has unexpected type {type(lang)}!")




# Below are implementations of urlword(word, lang: str)

anti_macron = [
    ("Ā", "A"),
    ("ā", "a"),
    ("Ē", "E"),
    ("ē", "e"),
    ("Ī", "I"),
    ("ī", "i"),
    ("Ō", "O"),
    ("ō", "o"),
    ("Ū", "U"),
    ("ū", "u"),
    ("Ȳ", "Y"),
    ("ȳ", "y")]
def mimicked_link_keyword(word: str, langname: str=None, is_deconstr=None) -> Tuple[str, str]:
    if langname == "Latin":
        for a, b in anti_macron:
            word = word.replace(a, b)

    if word.startswith("*"):
        if is_deconstr or langcodes.is_name_reconstr(langname):
            word = word[1:]

    urlword = urllib.parse.quote_plus(word)

    return urlword #design a function that mimics the behavior of https://en.wiktionary.org/wiki/Module:links

def empirical_link_keyword(key, ground_truth):
    # using  resultant html, find the corresponding link that corresponds to the key that gets actually created
    # this can be done using the parse api https://www.mediawiki.org/wiki/API:Parsing_wikitext and passing text to the Parse API (to the text argument?)
    """
    There are several ways to specify the text to parse:
    Specify content explicitly, using text, title, revid, and contentmodel.
    """
    pass


def emulated_link_keyword(key):
    pass # actually run the Module links.lua and use that to generate the link


def matches(word1, langname1, word2, langname2):
    return langname1 == langname2 and urlword(word1, langname1) == urlword(word2, langname2)