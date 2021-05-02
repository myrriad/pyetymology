
# https://en.wiktionary.org/wiki/Module:links
import warnings
from typing import Union

from pyetymology.emulate.template2url import urllang, urlify, keyword
from pyetymology.langhelper import Language


class QueryFlags:
    def __init__(self, def_id, deriv=False):
        self.def_id = def_id
        self.deriv = deriv


def to_link(word_or_urlword: str, lang_or_none:Union[Language, str, None] = None, qflags:QueryFlags=None, target_lang:str= "English", target_results:int=50, warn=True):
    if lang_or_none is None:
        _urlword = word_or_urlword
        return "http://en.wiktionary.org/w/api.php?action=parse&page=" + _urlword + "&prop=wikitext&formatversion=2&format=json"
    else:
        word = word_or_urlword
        lang = lang_or_none
        if qflags and qflags.deriv:
            # apparently you have to use an entirely different API (https://stackoverflow.com/questions/19285346/how-to-download-a-category-of-words-from-wiktionary)
            return f"http://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=" \
                   f"Category:{target_lang}_terms_derived_from_the_{urllang(lang)}_root_{urlword(word, lang.langname, strip_reconstr_star=False, warn=warn)}&cmprop=title" \
                   f"&format=json&cmlimit={target_results}"
            #  to_link(urlword(word=word, lang=lang))
        elif isinstance(lang, str) or isinstance(lang, Language):
            return to_link(urlword(word=word, lang=lang, warn=warn))
        else:
            raise TypeError(f"lang has unexpected type {type(lang)}")

def urlword(word: str, lang: Union[str, Language, None], strip_reconstr_star=True, warn=True, crash=False) -> str:  # TODO: test this
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
        if crash:
            raise ValueError(f"{word}'s lang is blank!")
        if warn:
            warnings.warn(f"retrieving {word}'s urlword without a lang! no macrons etc.")
        return urlify(keyword(word, strip_reconstr_star=strip_reconstr_star))
    if isinstance(lang, str):
        # lang is langname
        return urlify(keyword(word, lang, strip_reconstr_star=strip_reconstr_star))
    assert isinstance(lang, Language)
    if lang.reconstr:
        _urllang = urllang(lang)  # TODO: refine this
        assert isinstance(lang.langname, str)
        return "Reconstruction:" + _urllang + "/" + urlify(keyword(word, lang.langname))
    else:
        return urlword(word, lang.langname, warn=warn, crash=crash)

# Below are implementations of urlword(word, lang: str)


def matches(word1, langname1, word2, langname2, strict=False, ultra_strict=False):
    if langname1 and langname2: # if there are two defined languages
        lang_check = (langname1 == langname2)
        return lang_check and urlword(word1, langname1, crash=True) == urlword(word2, langname2, crash=True) # we should never be warned, because they should be defined
    else:
        # otherwise, one of them must be blank
        # therefore, compensation for macrons and sht is messed up
        if ultra_strict:
            return False
        # if we are lenient
        if strict:
            return urlword(word1, langname1, warn=False) == urlword(word2, langname2, warn=False) # we expect missing languages
            """
            Equality is well defined: transitive, etc. everything you'd expect from equality
            plicō#Latin == plico#Latin == plico =/= plicō
            plicō#Latin, plico#Latin =/= plicō
            plicō =/= plico
            """
        else:
            return word1 == word2 or urlword(word1, langname1, warn=False) == urlword(word2, langname2, warn=False)
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
