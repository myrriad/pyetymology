
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

def exceptioninfo(word: str, lang: str) -> Tuple[str, str]:
    urlword = mimicked_link_keyword(word, lang)
    return link(urlword), urlword

def urlword(word: str, lang: str) -> str:
    return mimicked_link_keyword(word, lang)

"""
EITHER:
1) a is word, b is lang, OR:
2) a is urlword
"""
def link(a: str, b: str=None) -> str:
    if b is None:
        urlword_ = a
    else:
        urlword_ = urlword(a, b)
    link = "https://en.wiktionary.com/w/api.php?action=parse&page=" + urlword_ + "&prop=wikitext&formatversion=2&format=json"
    return link



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