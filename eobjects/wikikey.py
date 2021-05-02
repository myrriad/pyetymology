"""
Use a Wikikey to keep track of wikiresources
"""
from __future__ import annotations # let me type hint class in own class

from typing import Optional, Union, Tuple

from pyetymology.emulate import moduleimpl
from pyetymology.emulate.moduleimpl import QueryFlags
from pyetymology.eobjects.apiresult import APIResult
from pyetymology.etyobjects import EtyRelation, LemmaRelation
from pyetymology.langhelper import Language

from pyetymology.queryutils import node_to_qparts, query_to_qparts



class WikiKey:
    def __init__(self, word:str, Lang:Language, qflags: QueryFlags):
        self.word = word
        self.Lang = Lang
        self.qflags = qflags
        self.result = None #type: Optional[APIResult]
        self.src = moduleimpl.to_link(word, Lang, qflags, warn=False)

    @property
    def fullurl(self):
        return self.src

    @property
    def deriv(self):
        return self.qflags.deriv

    @property
    def def_id(self):
        return self.qflags.def_id

    def load_result(self, result:Optional[APIResult]=None):
        if result:
            self.result = result
        else:
            assert not self.result # make sure that we aren't duplicating results
            self.result = APIResult(self.fullurl)
        return self.result

    def load_wikitext(self):
        self.result.load_wikitext(self)

    def __bool__(self):
        return bool(self.word or self.Lang)

    @classmethod
    def from_qparts(cls, word: str, Lang: Language, qflags: QueryFlags):
        retn = WikiKey(word, Lang, qflags)
        return retn

    @classmethod
    def from_node(cls, node: Union[EtyRelation, LemmaRelation, None]) -> WikiKey:
        word, Lang, qflags = node_to_qparts(node)
        return WikiKey.from_qparts(word, Lang, qflags)

    @classmethod
    def from_query(cls, query: str, warn=True, crash=False) -> Tuple[str, Language, QueryFlags]:
        word, Lang, qflags = query_to_qparts(query, warn, crash)
        return WikiKey.from_qparts(word, Lang, qflags)

