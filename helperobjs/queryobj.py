import urllib
from typing import List, Tuple, Union

from mwparserfromhell.wikicode import Wikicode

from pyetymology.etyobjects import Originator, EtyRelation, LemmaRelation, lyse_query
from pyetymology.langcode import langcodes
from pyetymology.module import module


def _setup_f_parts(self, word: str, langcode: str = None, langname: str = None,
                   def_id=None):  # TODO: when given only the langname, determine if it's reconstr

    is_deconstr = langcodes.is_reconstruction(langcode)
    if not langname:
        langname = langcodes.name(langcode)

    self._setup(word=word, langname=langname, def_id=def_id, is_deconstr=is_deconstr)


def _setup_f_str(self, usrin: str):
    word, lang, def_id = lyse_query(usrin)
    is_deconstr = False
    if lang.startswith("R:"):
        lang = lang[2:]
        is_deconstr = True
    elif lang.startswith("Reconstruction:"):
        lang = lang[15:]  # len("Reconstruction:") == 15
        is_deconstr = True
    self._setup(word=word, langname=lang, def_id=def_id, is_deconstr=is_deconstr)
    return self

def _setup_f_node(self, node: Union[EtyRelation, LemmaRelation, None]):
    if node:
        assert node.lang
        return _setup_f_parts(self, word=node.word, langcode=node.lang)

class SlimQuery:
    """
    Query object that corresponds to a single user input string query, such as "prototype#English" or "(s)tewp-#R:Proto-Indo-European"
    Can be mutated
    """
    def __init__(self, *args, **kwargs):
        if args or kwargs:
            self._setup(*args, **kwargs)

    def _setup(self, word: str, langname: str, def_id: str=None, is_deconstr: bool=False):
        """
        TRUE CONSTRUCTOR! # TODO: UGH, I HATE THIS
        """
        self.word = word
        self.lang = langname
        self.def_id = def_id
        self.deconstr = is_deconstr


    @classmethod
    def from_str(cls, usrin: str):
        return _setup_f_str(cls(), usrin) # cls() creates an instance to be setup

    @classmethod
    def from_parts(cls, word: str, langcode: str, langname: str=None, def_id=None):
        return _setup_f_parts(cls(), word=word, langcode=langcode, langname=langname, def_id=def_id)

    @classmethod
    def from_node(cls, node: Union[EtyRelation, LemmaRelation, None]):
        # TODO: def_id is lost, because the node is an EtyRelation, which relies on the Template, which loses info in form of defn id.
        # TODO: possible fix: change origin -> just an object that tracks the query in general
        # TODO: put def_id in that origin, which can be renamed QueryInfo, and use that
        return _setup_f_node(cls(), word=node.word, langcode=node.lang)

    @property
    def urlword(self):
        return module.urlword(self.word, self.lang)
    @property
    def urllang(self):
        return urllib.parse.quote_plus(self.lang.replace(" ", "-"))  # TODO: refine this

    @property
    def me(self):
        return self.query()
    @property
    def query(self):
        if self.deconstr:
            return self.word + "#Reconstruction:" + self.lang
        else:
            return self.word + "#" + self.lang

    def to_link_part(self):
        if self.deconstr:
            return "Reconstruction:" + self.urllang + "/" + self.urlword
        else:
            return self.urlword

    def api_link(self):
        return "https://en.wiktionary.com/w/api.php?action=parse&page=" + self.to_link_part() + "&prop=wikitext&formatversion=2&format=json"

    def raw_link(self):
        return "https://en.wiktionary.org/wiki/" + self.to_link_part() + "#" + self.urllang


class ThickQuery(SlimQuery):
    """
    This should include both the user's string query, or `usrquery`, and the corresponding wiktionary response and wikicode.
    """
    def __init__(self,
                 word: str, lang: str, def_id: str,
                 res: Wikicode, wikitext: str, dom: List[Wikicode],
                 origin: Originator):

        _setup_f_parts(self, word=word, langname=lang, def_id=def_id)
      # TODO: understand how python's class wrapping works

        self.res = res
        self.wikitext = wikitext
        self.dom = dom

        self.origin = origin

    @classmethod
    def from_tupled(cls, query: Tuple[str,str, str, str], wikiresponse: Tuple[Wikicode, str, List[Wikicode]],
                    origin: Originator):
        """
        query has 4 elements for legacy.
        the first element is ignored, and it can safely be put as None
        """
        return ThickQuery(word=query[1], lang=query[2], def_id=query[3], res=wikiresponse[0], wikitext=wikiresponse[1], dom=wikiresponse[2],
                          origin=origin)
    def to_tupled(self):
        return (self.me, self.word, self.lang, self.def_id), (self.res, self.wikitext, self.dom), self.origin
    def query_tupled(self):
        return self.me, self.word, self.lang, self.def_id






