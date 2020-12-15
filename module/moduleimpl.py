
# https://en.wiktionary.org/wiki/Module:links
import urllib
import warnings
from typing import Tuple, Union

from pyetymology.helperobjs.langhelper import Lang
from pyetymology.langcode import langcodes

def urllang(lang: str):
    return urllib.parse.quote_plus(lang.langname.replace(" ", "-"))


class QueryFlags:
    def __init__(self, def_id, deriv=False):
        self.def_id = def_id
        self.deriv = deriv


def to_link(word_or_urlword: str, lang_or_none:Union[Lang, str, None] = None, qflags:QueryFlags=None, target_lang:str="English", target_results:int=50):
    if lang_or_none is None:
        _urlword = word_or_urlword
        return "https://en.wiktionary.com/w/api.php?action=parse&page=" + _urlword + "&prop=wikitext&formatversion=2&format=json"
    else:
        word = word_or_urlword
        lang = lang_or_none
        if qflags and qflags.deriv:
            # apparently you have to use an entirely different API (https://stackoverflow.com/questions/19285346/how-to-download-a-category-of-words-from-wiktionary)
            return f"https://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=" \
                   f"Category:{target_lang}_terms_derived_from_the_{urllang(lang)}_root_{urlword(word, lang.langname, strip_reconstr_star=False)}&cmprop=title" \
                   f"&format=json&cmlimit={target_results}"
            #  to_link(urlword(word=word, lang=lang))
        elif isinstance(lang, str) or isinstance(lang, Lang):
            return to_link(urlword(word=word, lang=lang))
        else:
            raise TypeError(f"lang has unexpected type {type(lang)}")

def urlword(word: str, lang: Union[str, Lang, None], strip_reconstr_star=True) -> str:  # TODO: test this
    """
    Generates a urlword from what's used in the template.
    See https://en.wiktionary.org/wiki/Template:mention under "|2= (optional)
    See https://en.wiktionary.org/wiki/Module:languages#Language:makeEntryName

    ``
    if type(self._rawData.entry_name) == "table" then
        text = do_entry_name_or_sort_key_replacements(text, self._rawData.entry_name)
    end
    ``
    Except for Arabic,
    The exact impl. of diacritic removal is impl.'d on the language level, NOT on the Module:language level.
    See https://en.wiktionary.org/wiki/Wiktionary:Languages: "The data itself is not stored in Module:languages,
     but instead is contained in a number of data modules (see Category:Language data modules). These are organised as follows:"
    For example, Latin's macron removal is impl'd in it's specific section in
    https://en.wiktionary.org/wiki/Module:languages/data2: (under Latin)
    ``entry_name = {remove_diacritics = MACRON .. BREVE .. DIAER .. DOUBLEINVBREVE}``
    https://en.wiktionary.org/wiki/Module:languages/data2
    See https://en.wiktionary.org/wiki/Module:languages/data2 under "entry_name"
    See function do_entry_name_or_sort_key_replacements()
    """
    # TODO: Unsupported titles
    # TODO: do all of the entry_name fixes in https://en.wiktionary.org/wiki/Module:languages/data2, etc
    if not lang:
        warnings.warn("retrieving urlword without a lang! language-deterministic checks such as macrons won't work!")
        return mimicked_link_keyword(word, strip_reconstr_star=strip_reconstr_star)
    if isinstance(lang, str):
        # lang is langname
        return mimicked_link_keyword(word, lang, strip_reconstr_star=strip_reconstr_star)
    assert isinstance(lang, Lang)
    if lang.reconstr:
        _urllang = urllang(lang)  # TODO: refine this
        assert isinstance(lang.langname, str)
        return "Reconstruction:" + _urllang + "/" + urlword(word, lang.langname)
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
def mimicked_link_keyword(word: str, langname: str=None, is_deconstr=None, strip_reconstr_star=True) -> Tuple[str, str]:
    if langname == "Latin":
        for a, b in anti_macron:
            word = word.replace(a, b)

    if word.startswith("*") and strip_reconstr_star:
        if is_deconstr or langname and langcodes.is_name_reconstr(langname):
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


def matches(word1, langname1, word2, langname2, strict=False, ultra_strict=False):
    if langname1 and langname2: # if there are two defined languages
        lang_check = (langname1 == langname2)
        return lang_check and urlword(word1, langname1) == urlword(word2, langname2)
    else:
        # otherwise, one of them must be blank
        # therefore, compensation for macrons and sht is messed up
        if ultra_strict:
            return False
        # if we are be lenient
        if strict:
            return urlword(word1, langname1) == urlword(word2, langname2)
            """
            Equality is well defined: transitive, etc. everything you'd expect from equality
            plicō#Latin == plico#Latin == plico =/= plicō
            plicō#Latin, plico#Latin =/= plicō
            plicō =/= plico
            """
        else:
            return word1 == word2 or urlword(word1, langname1) == urlword(word2, langname2)
            # if there's a lang-omitted term ("query") AND a lang-present term:
            # the "query" will match BOTH the literal word-lang OR the reduced word-lang.
            # for example plico will match plicō#Latin b/c plico matches the reduced word-lang.

            # if they're both lang-omitted, then the reduced word-lang IS the literal word-lang
            # so they will only match if the words are literally equal.
            """
            Equality is NOT well defined: NOT transitive!
            plicō#Latin == plico#Latin 
            plicō#Latin == plicō 
            !! plico#Latin =/= plicō 
            !! plicō#Latin == plico
            plico#Latin == plico
            plicō =/= plico
            
            """
            return
    """
    # TODO:
    plicō#Latin == plico#Latin 
    plicō#Latin ?== plicō 
    plico#Latin ?== plicō 
    plicō#Latin ?== plico
    plico#Latin ?== plico
    plicō ?=/= plico
    
    """
