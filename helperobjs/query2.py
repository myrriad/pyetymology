from typing import Union, Tuple

from pyetymology.etyobjects import LemmaRelation, EtyRelation
from pyetymology.helperobjs.langhelper import Lang


def node_to_qparts(node: Union[EtyRelation, LemmaRelation, None]) -> Tuple[str, Lang, str]:
    if node:
        word = node.word
        if node.lang:
            langname = node.lang  # this is necessary for say Latin plico. We find the existing template from the suggestion,
            # then we deduct the actual word and lang
            lang = Lang(langname=langname)

        else:
            langname = ""
            lang = None
        found = True
        return word, lang, None # TODO: store def_id info in the node, perhaps by keeping track of it in the originator
    # TODO: rename originator into a QueryInfo object that stores info on the query, including the def_id
    # TODO: because def_id is essentially metainfo that isn't retained in the template.
    return None, None, None

def query_to_qparts(query: str) -> Tuple[str, str, str]:
    def_id = None
    terms = query.split("#")
    if len(terms) == 1:
        word = query
        # lang = input("Language not detected! Please input one: ")
        lang = ""
    elif len(terms) == 2:
        word, langqstr = terms
    elif len(terms) == 3:
        word, langqstr, def_id = terms
    else:
        raise Exception(
            f'Query string "{query}" has an unsupported number of arguments! There should be either one or two \'#\'s only,')
    _Lang = Lang(langqstr=lang)
    return word, _Lang, def_id
