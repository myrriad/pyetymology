
# https://en.wiktionary.org/wiki/Module:links
import urllib
from typing import Tuple

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

def to_link(word_or_urlword: str, lang_or_none:str = None):
    if lang_or_none is None:
        return urlword_to_link(word_or_urlword)
    else:
        return qparts_to_link(word_or_urlword, lang_or_none)

def qparts_to_link(word: str, lang: str):
    return urlword_to_link(urlword(word, lang))

def urlword_to_link(urlword: str):
    link = "https://en.wiktionary.com/w/api.php?action=parse&page=" + urlword + "&prop=wikitext&formatversion=2&format=json"
    return link

def urlword(word: str, lang: str) -> str:
    return mimicked_link_keyword(word, lang)





def mimicked_link_keyword(word: str, lang: str) -> Tuple[str, str]:
    if lang == "Latin":
        for a, b in anti_macron:
            word = word.replace(a, b)
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