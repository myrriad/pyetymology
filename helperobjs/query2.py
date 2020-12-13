from typing import Union, Tuple

from pyetymology.etyobjects import LemmaRelation, EtyRelation


def node_to_qparts(node: Union[EtyRelation, LemmaRelation, None]) -> Tuple[str, str, str]:
    if node:
        word = node.word
        if node.lang:
            langname = node.lang  # this is necessary for say Latin plico. We find the existing template from the suggestion,
            # then we deduct the actual word and lang
        else:
            langname = ""
        found = True
        return word, langname, None # TODO: store def_id info in the node, perhaps by keeping track of it in the originator
    # TODO: rename originator into a QueryInfo object that stores info on the query, including the def_id
    # TODO: because def_id is essentially metainfo that isn't retained in the template.
    return None, None, None

def query_to_qparts(query: str):
    def_id = None
    terms = query.split("#")
    if len(terms) == 1:
        word = query
        # lang = input("Language not detected! Please input one: ")
        lang = ""
    elif len(terms) == 2:
        word, lang = terms
    elif len(terms) == 3:
        word, lang, def_id = terms
    else:
        raise Exception(
            f'Query string "{query}" has an unsupported number of arguments! There should be either one or two \'#\'s only,')
    return word, lang, def_id
