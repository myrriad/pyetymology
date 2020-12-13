from typing import List, Tuple

from mwparserfromhell.wikicode import Wikicode

from pyetymology.etyobjects import Originator
from pyetymology.module import moduleimpl



class ThickQuery():
    def __init__(self,
                 me: str, word: str, langname: str, def_id: str,
                 res: Wikicode, wikitext: str, dom: List[Wikicode],
                 origin: Originator):
        self.me = me
        self.word = word
        self.lang = langname
        self.def_id = def_id

        self.res = res
        self.wikitext = wikitext
        self.dom = dom

        self.origin = origin


    def to_tupled(self):
        return (self.me, self.word, self.lang, self.def_id), (self.res, self.wikitext, self.dom), self.origin
    @property
    def query(self):
        return (self.me, self.word, self.lang, self.def_id)
    @property
    def word_urlify(self):
        return moduleimpl.urlword(self.word, self.lang)
    @property
    def wikitext_link(self):
        return moduleimpl.to_link(self.word_urlify)


def from_tupled(query: Tuple[str, str, str, str], wikiresponse: Tuple[Wikicode, str, List[Wikicode]], origin: Originator):
    return ThickQuery(*query, *wikiresponse, origin)