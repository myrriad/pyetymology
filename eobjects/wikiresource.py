from typing import Union

from pyetymology.etyobjects import LemmaRelation, EtyRelation, WordRelation
from pyetymology.module import moduleimpl



def template_word_to_keyword(word, langname):
    """
    The template word is different from the word wiktionary uses in urls.
    For example, templates have macrons in them (plicо̄), but urls have those macrons removed.
    This function takes template words and turns them into url words.
    """
    # FROM moduleimpl.keyword(word, langname)
    return moduleimpl.keyword(word, langname)

class WikiResourceCommon:
    def __init__(self, relation: WordRelation):
        self.relation = relation
        self.keywordvital = template_word_to_keyword(relation.word, relation.langname)

    def template_vital(self) -> str:
        """
        Returns the string as found or used in template.
        """
        return self.relation.word
    def keyword_vital(self):
        """
        Returns the string that would be used to query this resource with query().
        """
        return self.keywordvital
    def _url_vital(self):
        """
        Returns the string that should be appended to the general wiktionary link to provide the url associated with resource.
        Generally not useful except when asking for full url.
        However, useful when subclasses contain different behavior (such as Reconstruction:Proto-Indo-European
        """
        return moduleimpl.urlify(self.keyword_vital())
    def url(self):
        """
        Returns the full url associated with resource.
        """
        return f"https://en.wiktionary.org/wiki/{self.url_vital()}"
    def langcode(self):
        return self.relation.langcode
    def langname(self):
        return self.relation.langname

class WikiResourceReconstruction(WikiResourceCommon):
    def __init__(self, relation: WordRelation):
        # WikiResourceCommon.__init__(self, relation)
        self.relation = relation
        assert relation.word.startswith("*") # if it's a reconstruction, the template kw should start with a star
        # EDIT: Reconstructions don't have to be proto-langs. FOr example Old English has reconsturcted words
        vital = relation.word[1:]

        self.keywordvital = template_word_to_keyword(vital, relation.langname)
    def _url_vital(self):
        return f"Reconstruction:{self.langname()}/{moduleimpl.urlify(self.keyword_vital())}"
