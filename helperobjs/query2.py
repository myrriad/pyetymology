from typing import Union, Tuple

from pyetymology.etyobjects import LemmaRelation, EtyRelation
from pyetymology.helperobjs.langhelper import Lang


def node_to_qparts(node: Union[EtyRelation, LemmaRelation, None]) -> Tuple[str, Lang, str]:
    if node:
        word = node.word
        if node.lang:
            # this is necessary for say Latin plico. We find the existing template from the suggestion,
            langcode = node.lang
            # langname = node.langname
            # then we deduct the actual word and lang
            lang = Lang(langcode=langcode)

        else:
            # langname = ""
            lang = None
        found = True
        return word, lang, None # TODO: store def_id info in the node, perhaps by keeping track of it in the originator
    # TODO: rename originator into a QueryInfo object that stores info on the query, including the def_id
    # TODO: because def_id is essentially metainfo that isn't retained in the template.
    return None, None, None

def query_to_qparts(query: str) -> Tuple[str, Lang, str]:
    assert query
    do_derivs = False
    if query.startswith("#"):
        # user switch to enable derivations
        # ie. #*dakaz would enable derivations of #*dakaz#Proto-Indo-European to be
        do_derivs = True
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
    _Lang = Lang(langqstr=langqstr)
    return word, _Lang, def_id
