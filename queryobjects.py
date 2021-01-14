from typing import List, Tuple, Union

from mwparserfromhell.wikicode import Wikicode

from pyetymology.etyobjects import Originator, EtyRelation, LemmaRelation
from pyetymology.langhelper import Language
from pyetymology.module.moduleimpl import QueryFlags
from pyetymology.module import moduleimpl



class ThickQuery():
    def __init__(self,
                 me: str, word: str, langname: str, def_id: str,
                 res: Wikicode, wikitext: str, dom: List[Wikicode],
                 origin: Originator, qflags: QueryFlags = None):
        self.me = me
        # self.word = word
        # self.lang = langname

        _word, _Lang, _qflags = query_to_qparts(me)
        # _def_id = _qflags.def_id
        self.queryflags = _qflags
        assert def_id == _qflags.def_id
        self.def_id = _qflags.def_id

        self.word = _word

        self.lang = _Lang.langname
        assert word == self.word
        assert langname == self.lang
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
        return (self.me, self.word, self.lang, self.def_id), (self.res, self.wikitext, self.dom), self.origin
    @property
    def query(self):
        return (self.me, self.word, self.lang, self.def_id)
    @property
    def word_urlify(self):
        # return moduleimpl.urlword(self.word, self.lang)
         return moduleimpl.urlword(self.word, self.biglang(), crash=True) # we should actually crash because queries *must* have a language defined
    @property
    def wikitext_link(self):
        return moduleimpl.to_link(self.word, self.biglang())


class DummyQuery(ThickQuery):
    def __init__(self, me:str, origin:Originator, child_queries: List[str], with_lang:Language):
        word, _Lang, _qflags = query_to_qparts(me)
        biglang = with_lang

        me2 = word + "#" + biglang.langqstr
        lang = biglang.langname
        def_id = _qflags.def_id
        super().__init__(me=me2, word=word, langname=lang, def_id=def_id, res=None, wikitext=None, dom=None, origin=origin, qflags=_qflags)
        self.child_queries = child_queries

def from_tupled(query: Tuple[str, str, str, str], wikiresponse: Tuple[Wikicode, str, List[Wikicode]], origin: Originator):
    return ThickQuery(*query, *wikiresponse, origin)


def node_to_qparts(node: Union[EtyRelation, LemmaRelation, None]) -> Tuple[str, Language, QueryFlags]:
    if node:
        word = node.word
        if node.lang:
            # this is necessary for say Latin plico. We find the existing template from the suggestion,
            langcode = node.lang
            # langname = node.langname
            # then we deduct the actual word and lang
            lang = Language(langcode=langcode)

        else:
            # langname = ""
            lang = None
        found = True
        return word, lang, None # TODO: store def_id info in the node, perhaps by keeping track of it in the originator
    # TODO: rename originator into a QueryInfo object that stores info on the query, including the def_id
    # TODO: because def_id is essentially metainfo that isn't retained in the template.
    return None, None, None


def query_to_qparts(query: str, warn=True, crash=False) -> Tuple[str, Language, QueryFlags]:
    assert query
    do_deriv = ""
    if query.startswith("#"):
        # user switch to tell them to look for the Terms_derived_from_the_<lang>_root_<word> page
        # ie. #*dakaz would enable derivations of #*dakaz#Proto-Indo-European to be
        do_deriv = "TD"
        query = query[1:]
    terms = query.split("#")
    def_id = None
    if len(terms) == 1:
        word = query
        # lang = input("Language not detected! Please input one: ")
        # warnings.warn("Language not detected for query " + me)
        langqstr = ""

    elif len(terms) == 2:
        word, langqstr = terms
    elif len(terms) == 3:
        word, langqstr, def_id = terms
    else:
        raise Exception(
            f'Query string "{query}" has an unsupported number of arguments! There should be either 1-3 terms only,')
    if not langqstr and crash:
        raise ValueError("Language inferral (or having a blank language in your query) is not permitted/expected.")
    _Lang = Language(langqstr=langqstr, warn=warn)
    # The only time langqstr can be empty is if the function was specifically authorized to allow no-langs.
    return word, _Lang, QueryFlags(def_id=def_id, deriv=do_deriv)