from typing import List, Tuple, Optional

from mwparserfromhell.wikicode import Wikicode

from pyetymology.eobjects.wikikey import WikiKey
from pyetymology.etyobjects import Originator
from pyetymology.langhelper import Language
from pyetymology.emulate.moduleimpl import QueryFlags
from pyetymology.emulate import moduleimpl

from pyetymology.queryutils import query_to_qparts


class ThickQuery():
    def __init__(self,
                 me: str, word: str, langname: str, def_id: str,
                 res: Wikicode, wikitext: str, dom: List[Wikicode],
                 origin: Originator, qflags: QueryFlags = None, wkey=None):
        """
        Deprecated.
        ThickQuery.from_key(wkey) is HIGHLY recommended.

        """
        if not wkey:
            wkey = WikiKey.from_qparts(word=word, Lang=Language(langname=langname), qflags=QueryFlags(def_id))
        self.wkey = wkey

        self.me = me
        # self.word = word
        # self.lang = langname

        _word, _Lang, _qflags = query_to_qparts(me)
        # _def_id = _qflags.def_id
        assert _qflags.def_id is not None # change: this will be 1 and is nonnull
        self.queryflags = _qflags
        if def_id is not None: # we have to permit None def_id because of archaic tupling pickling
            if def_id != _qflags.def_id:
                raise ValueError(f"{def_id} != {_qflags.def_id}")
        self.def_id = _qflags.def_id

        self.word = _word

        self.langname = _Lang.langname
        assert word == self.word
        assert langname == self.langname
        # assert def_id == qdef_id
        self.Lang = _Lang
        assert self.Lang  # It must not be blank.

        self.res = res
        self.wikitext = wikitext
        self.dom = dom

        self.origin = origin




    def biglang(self):
        return self.Lang
    def to_tupled(self):
        return (self.me, self.word, self.langname, self.def_id), (self.res, self.wikitext, self.dom), self.origin
    @property
    def query(self):
        return (self.me, self.word, self.langname, self.def_id)
    @property
    def word_urlify(self):
        # return moduleimpl.urlword(self.word, self.lang)
         return moduleimpl.urlword(self.word, self.biglang(), crash=True) # we should actually crash because queries *must* have a language defined
    @property
    def wikitext_link(self):
        return moduleimpl.to_link(self.word, self.biglang())

    @classmethod
    def from_key(cls, wkey: WikiKey, origin, me:str=None):
        retn = ThickQuery.__new__(ThickQuery)
        retn._init_from_wkey(wkey, origin, me)
        return retn

    def _init_from_wkey(self, wkey: WikiKey, origin, me:str=None, allow_none_result=False):
        if not me:
            me = wkey.me
        if allow_none_result and not wkey.result:
            res = wikitext = dom = None
        else:
            result = wkey.result
            assert result is not None
            res = result.wikiresponse
            wikitext = result.wikitext
            dom = result.dom
        self.__init__(me=me, word=wkey.word, langname=wkey.Lang.langname, def_id=wkey.def_id, res=res, wikitext=wikitext, dom=dom, origin=origin, qflags=wkey.qflags,
                      wkey=wkey)

class DummyQuery(ThickQuery):
    def __init__(self, wkey: WikiKey, with_lang:Language, origin:Originator,me:Optional[str]=None):
        if not me:
            me = wkey.me
        """
                derivs = result.derivs
        origin = Originator(me, o_id=query_id)
        return DummyQuery(me=me, origin=origin, child_queries=derivs, with_lang=Language(langcode="en"))
        """
        word, _, _qflags = query_to_qparts(me)

        # me2 = word + "#" + with_lang.langqstr
        # langname = with_lang.langname
        # def_id = _qflags.def_id

        wkey2 = WikiKey.from_qparts(word, with_lang, _qflags)
        assert wkey2.result is None
        # wkey2.me == word +"#"+with_lang.qstr
        super()._init_from_wkey(wkey2, origin, allow_none_result=True)
        # (me=wkey2.me, word=wkey.word, langname=wkey.Lang.langname, def_id=wkey.def_id, res=wkey.result.wikiresponse, wikitext=wkey.result.wikitext, dom=wkey.result.dom, origin=origin)
        # (me=me2, word=word, langname=langname, def_id=def_id, res=None, wikitext=None, dom=None, origin=origin, qflags=_qflags)

        # perfectly equivalent to old code
        self.child_queries = wkey.result.derivs

def from_tupled(query: Tuple[str, str, str, str], wikiresponse: Tuple[Wikicode, str, List[Wikicode]], origin: Originator):
    """
    Archaic terribleness from before the usage of WikiKey.
    """

    # me, word, langname, def_id = query
    # res, wikitext, dom = wikiresponse
    # origin: Originator, qflags: QueryFlags = None
    # wkey = WikiKey.from_me(me)
    # wkey2 = WikiKey.from_qparts(word, Language(langname=langname),qflags=QueryFlags(def_id=def_id))
    return ThickQuery(*query, *wikiresponse, origin)


