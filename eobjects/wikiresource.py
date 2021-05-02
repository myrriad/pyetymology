from typing import Union

import pyetymology.emulate.template2url
from pyetymology.emulate.moduleimpl import QueryFlags
from pyetymology.etyobjects import LemmaRelation, EtyRelation, WordRelation
from pyetymology.emulate import template2url
from pyetymology.emulate.template2url import urllang,urlify
from pyetymology.queryobjects import ThickQuery

"""
ANALOG TO moduleimpl.to_link()
"""

def template_word_to_keyword(word, langname):
    """
    The template word is different from the word wiktionary uses in urls.
    For example, templates have macrons in them (plicо̄), but urls have those macrons removed.
    This function takes template words and turns them into url words.
    """
    # FROM moduleimpl.keyword(word, langname)
    return template2url.keyword(word, langname)

class WikiResource:
    def __init__(self, relation: WordRelation):
        self._relation = relation
        self.keywordvital = template_word_to_keyword(relation.word, relation.langname)

    def word(self):
        return self._relation.word
    def langname(self):
        return self._relation.langname
    def url_langname(self):
        return urllang(self.langname())
    def template_vital(self) -> str:
        """
        Returns the string as found or used in template.
        """
        return self.word()
    def keyword_vital(self):
        """
        Returns the string that would be used to query this resource with query().
        NOT url escaped. For example Niño = Niño
        """
        return self.keywordvital
    def _url_vital(self):
        """
        Returns the string that should be appended to the general wiktionary link to provide the url associated with resource.
        Generally not useful except when asking for full url.
        However, useful when subclasses contain different behavior (such as Reconstruction:Proto-Indo-European
        IS url escaped. For example Niño -> Ni%C3%B1o
        """
        return urlify(self.keyword_vital())
    def url(self):
        """
        Returns the full url associated with resource.
        """
        return f"https://en.wiktionary.org/wiki/{self.url_vital()}"
    def url_api(self):
        return f"http://en.wiktionary.org/w/api.php?action=parse&page={self._url_vital()}&prop=wikitext&formatversion=2&format=json"

class WikiResourceFromQueryStr(WikiResource):
    def __init__(self, word: str, langname: str):
        self.word = word
        self.langname = langname
        self._relation = None
        self.keywordvital = template_word_to_keyword(self._relation.word, self._relation.langname)
    def word(self):
        return self.word
    def langname(self):
        return self.langname
    # TODO: Ambiguity.
    # Should we assume the query is template-style, plicо̄#Latin,
    # Or should we assume the query is keyword-style, plico#Latin?

    # Solution - First take the input in as Template-style, and search the existing graph for the correct node
    # - On the website, search the cytoscape graph for a node that matches the template-style input
    # Search only Template-style, because the graph is stored template-style and not keyword-style
    # If the node cannot be found, we have two options
    # 1) ASSUME that the input is keyword-style
    # This is a reasonable assumption, because keyword-style is what is found in the URL
    # (Template-style we only deal with after wiktionary)
    # Even the word#lang pair should be assumed keyword style because plico#Latin is the expected input
    # 2) APPLY template_word_to_keyword anyway
    # We can abuse the fact that plicо̄ --f--> plico, but also plico --f--> plico
    # where f = template_word_to_keyword
    # to proactively apply f to everything
    # but there is no guarantee that this f works for everthing
    # for example if there was such an imaginary transformation 1) jabe --f--> jabé 2) jabé --f--> jabe'
    # then we'd have issues


class WikiResourceReconstruction(WikiResource):
    def __init__(self, relation: WordRelation):
        # WikiResourceCommon.__init__(self, relation)
        self.relation = relation
        assert relation.word.startswith("*") # if it's a reconstruction, the template kw should start with a star
        # EDIT: Reconstructions don't have to be proto-langs. FOr example Old English has reconsturcted words
        vital = relation.word[1:]

        self.keywordvital = template_word_to_keyword(vital, relation.langname)
    def _url_vital(self):  # we can put it in _url_vital because this works for both url() and url_api() so I guess wiktionary treats the Reconstruction:<lang> as a discrete unit
        return f"Reconstruction:{self.url_langname()}/{urlify(self.keyword_vital())}"

class WikiResourceTermsDerivedFrom(WikiResource):

    def __init__(self, relation: WordRelation, qflags:QueryFlags=None, target_lang:str= "English", target_results:int=50):
        WikiResource.__init__(self, relation)
        # self.qflags = qflags  # TODO: qFlags for entirety of WIkiResource
        self.target_lang = target_lang
        self.target_results = target_results
    # from moduleimpl
    def url(self):
        return f"https://en.wiktionary.org/wiki/Category:{self.target_lang}_terms_derived_from_the_{self.url_langname()}_root_{template2url.urlify(self.keyword_vital())}"
    def url_api(self):
        # we use the urlified keyword lang, because
        # example links such as https://en.wiktionary.org/wiki/Category:Terms_derived_from_the_Proto-Indo-European_root_*h%E2%82%81ed-
        # incorporate the asterik *, which suggests that we take the urlified keyword directly
        return f"http://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=" \
                   f"Category:{self.target_lang}_terms_derived_from_the_{self.url_langname()}_root_{urlify(self.keyword_vital())}&cmprop=title" \
                   f"&format=json&cmlimit={self.target_results}"


def from_relation(relation: WordRelation) -> WikiResource:
    word = relation.word
    if word.startswith("*"):
        if not word in ['*','*nix','* *','*band','nices','*69','*nixes','*bands','*/']:
            return WikiResourceReconstruction(relation)
        # if the length is exactly 1, then the template word is "*", which should redirect to the wiktionary special charactor page for *
        # there are exceptions: see https://en.wiktionary.org/wiki/*nix https://en.wiktionary.org/wiki/Category:English_terms_spelled_with_*
        # TODO: auto update this section of exceptions
        # TODO: I think we have to do something with the
        # TODO or actually implement the mediawiki emulation sandboxing
    return WikiResource(relation)

def from_url(url: str) -> WikiResource:

    pass