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
    def __init__(self): #, word:str, Lang:Language, qflags: QueryFlags):
        """
        Construct non-null WikiKeys using the WikiKey.from_X() methods
        """
        self.word = None #type: str
        self.Lang = Language(warn=False) #type: Language
        self.qflags = None #type: QueryFlags
        self.result = None #type: Optional[APIResult]
        self.src = None #type: str
        #  moduleimpl.to_link(word, Lang, qflags, warn=False)

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

    def load_wikitext(self, infer_lang=True, override_lang=False):
        """
        if infer_lang=True, you are guaranteed a lang at the end
        """
        self.result.load_wikitext(self, infer_lang=infer_lang, override_lang=override_lang)
    def __bool__(self):
        return bool(self.word or self.Lang)

    @classmethod
    def from_qparts(cls, word: str, Lang: Language, qflags: QueryFlags):
        retn = WikiKey() # word, Lang, qflags)
        retn.word = word
        retn.Lang = Lang
        retn.qflags = qflags
        retn.result = None #type: Optional[APIResult]
        retn.src = moduleimpl.to_link(word, Lang, qflags, warn=False)
        return retn

    @classmethod
    def from_node(cls, node: Union[EtyRelation, LemmaRelation, None]) -> WikiKey:
        word, Lang, qflags = node_to_qparts(node)
        return WikiKey.from_qparts(word, Lang, qflags)

    @classmethod
    def from_query(cls, query: str, warn=True, crash=False) -> Tuple[str, Language, QueryFlags]:
        word, Lang, qflags = query_to_qparts(query, warn, crash)
        return WikiKey.from_qparts(word, Lang, qflags)

    @classmethod
    def from_regurl(cls, url: str, cmlimit=50):
        """
        DOES NO SANITATION. ASSUMES INPUT URL IS VALID AND SANITIZED.
        Duplicates moduleimpl somewhat, with one major exception:
        NO FINICKY ADJUSTMENTS MADE. Method accepts url parameters as is.
        THEREFORE, NO SANITATION IS DONE WHATSOEVER. USE AT OWN RISK
        regurl: a regular url, like "https://en.wiktionary.org/wiki/Reconstruction:Proto-West_Germanic/mak%C5%8Dn"
        cmlimit: Mediawiki term for the number of results in a given category returned.
        """
        if url.startswith("https://"):
            url = url[8:]
        elif url.startswith("http://"):
            url = url[7:]
        assert url.startswith("en.wiktionary.org/wiki/")
        urlpart = url[23:url.index('#')]
        langtag = url[url.index('#')+1:]
        # put this in there to really make sure that no bad data gets in here, debugging wise
        if urlpart.startswith("Category:"):
            return WikiKey.from_fullurl(
                f"http://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle={urlpart}&cmprop=title"
                f"&format=json&cmlimit={cmlimit}#{langtag}")
        return WikiKey.from_fullurl(
            f"https://en.wiktionary.org/w/api.php?action=parse&page={urlpart}&prop=wikitext&formatversion=2&format=json#{langtag}")
    # TODO: SANITATION HELL



    @classmethod
    def from_fullurl(cls, fullurl: str, resolve_multilang=None):
        """
        Returns a WikiKey with result automatically loaded, but wikitext NOT loaded
        """
        wkey = WikiKey()
        wkey.src = fullurl
        wkey.load_result()
        if 'parse' in wkey.result.jsn: # it's kinda rough that we're reading json outside of load_wikitext
            title = wkey.result.jsn['parse']['title'] #type: str
            # there are at least 2 cases
            # case 1: title is simply the word
            # case 2: reconstruction, the title includes the word and lang
            # case 3: ??
            wkey.qflags = QueryFlags(1, False) # since we're parsing, deriv is false
            if title.startswith("Reconstruction:"):
                # langname = title[title.index("Reconstruction:"+len("Reconstruction:")) : title.index('/')].replace('_', ' ')
                # this might be slightly off and will otherwise differ subtly. For that reason it's deprecated and we prefer to infer below
                # wkey.Lang = Language(langname=langname, is_reconstr=True) # make sure we know it's reconstr, ie. a failing example is "Old English"
                wkey.word = title[title.rindex('/')+1 : ]
                wkey.load_wikitext(infer_lang=True)  # requires wkey.deriv and wkey.langname We already know Lang
                # after this word, Lang,
                return wkey
            else: # it's a normal word
                wkey.word = title
                if '#' in fullurl:
                    _sections = fullurl.split('#')  # fullurl uses a # to separate and designate the language
                    # the #s are ignored in api calls
                    # for example https://en.wiktionary.org/w/api.php?action=parse&page=comprar&prop=wikitext&formatversion=2&format=json#Spanish
                    if len(_sections) != 2:
                        raise ValueError(f'fullurl {fullurl} has multiple #s!')
                    langname = _sections[-1]  # take the last after # to take the language
                    wkey.Lang = Language(langname=langname)
                wkey.load_wikitext(infer_lang=True) # BY DEFN, infer_lang should guarantee us a Lang
                assert wkey.Lang
                # if not wkey.Lang:
                return wkey
        elif 'query' in wkey.result.jsn:
            wkey.qflags = QueryFlags(1, False) # since jsn is 'query', deriv is True
            raise NotImplementedError() # TODO FINISH
        else:
            raise TypeError(f"wkey has unexpected result {wkey.result.wikitype}")
