import urllib
from typing import Tuple


def urllang(lang: str):
    return urllib.parse.quote_plus(lang.langname.replace(" ", "_")) # Proto-West Germanic --> Proto-West_Germanic


def urlify(word):
    return urllib.parse.quote_plus(word)


def mimicked_keyword(word: str, langname: str=None, is_reconstr=None, strip_reconstr_star=True) -> Tuple[str, str]:
    """
    Formerly mimicked_link_keyword
    """
    if langname == "Latin":
        for a, b in anti_macron:
            word = word.replace(a, b)

    if word.startswith("*") and strip_reconstr_star:
        if is_reconstr or langname and langname.startswith("Proto"):  # TODO: Old English
            word = word[1:]

    return word
    # urlword = urllib.parse.quote_plus(word)

    # return urlword #design a function that mimics the behavior of https://en.wiktionary.org/wiki/Module:links


def empirical_keyword(key, ground_truth):
    # using  resultant html, find the corresponding link that corresponds to the key that gets actually created
    # this can be done using the parse api https://www.mediawiki.org/wiki/API:Parsing_wikitext and passing text to the Parse API (to the text argument?)
    """
    There are several ways to specify the text to parse:
    Specify content explicitly, using text, title, revid, and contentmodel.
    """
    pass


def emulated_keyword(key):
    pass # actually run the Module links.lua and use that to generate the link


def keyword(word: str, langname: str=None, is_reconstr=None, strip_reconstr_star=True):
    return mimicked_keyword(word, langname, is_reconstr=is_reconstr, strip_reconstr_star=strip_reconstr_star)


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