import warnings

import grandalf as grandalf

import requests
import json

from pyetymology import helper as helper
import pyetymology.langcode.cache

import networkx as nx #rumored to be slow, but I'm just using it temporarily

import pickle

import matplotlib.pyplot as plt

import urllib.parse as urllib



from pyetymology.etyobjects import Originator

#https://iconscout.com/blog/15-classic-color-scheme-generators-to-pick-the-perfect-palette
from pyetymology.helper import draw_graph

online = True

session = requests.Session()
session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))  # retry up to 2 times
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))

original_query = "" #lleno#Spanish"#llenar#Spanish"#"conflate#English"#"llegar#Spanish"#"Reconstruction:Proto-Italic/feiljos#"

def query(me):
    if not me:
        me = input("Enter a query: " + me)
    terms = me.split("#")
    def_id = None
    if len(terms) == 1:
        word = me
        # lang = input("Language not detected! Please input one: ")
        lang = ""
        # me = word + "#" + lang
    elif len(terms) == 2:
        word, lang = terms
    elif len(terms) == 3:
        word, lang, def_id = terms
    else:
        raise Exception(f'Query string "{me}" has an unsupported number of arguments! There should be either one or two \'#\'s only,')

    word_urlify = urllib.quote_plus(word)
    src = "https://en.wiktionary.com/w/api.php?action=parse&page=" + word_urlify + "&prop=wikitext&formatversion=2&format=json"
    # https://en.wiktionary.com/w/api.php?action=parse&page=word&prop=wikitext&formatversion=2&format=json
    if online:
        res = session.get(src)

        #cache res
        with open('pyetymology/response.pkl', 'wb') as output:
            pickle.dump(res, output, pickle.HIGHEST_PROTOCOL)
    else:
        with open('pyetymology/response.pkl', 'rb') as _input:
            res = pickle.load(_input)

    txt = res.text
    jsn = json.loads(txt) #type: json
    if "parse" in jsn:
        wikitext = jsn["parse"]["wikitext"]
    elif "error" in jsn:
        print(src)
        print(f"https://en.wiktionary.org/wiki/{word_urlify}")
        raise Exception("Response returned an error! Perhaps the page doesn't exist? \nJSON: " + str(jsn["error"]))
    else:
        raise Exception("Response malformed!" + str(jsn))
    # print(wikitext)

    res, dom = helper.wikitextparse(wikitext)
    # Here was the lang detection

    dom, me, word, lang = helper.validate(dom, me, word, lang)
    assert me
    assert word
    assert lang
    assert len(me.split("#")) >= 2

    query = (me, word, lang, def_id)
    wikiresponse = (res, wikitext, dom)
    origin = Originator(me) # TODO: origin must be equipped with a me that contains a lang. That means that lang needs to be known at query time, which it currently is known at parse time.
    return query, wikiresponse, origin, src, word_urlify
def graph(query, wikiresponse, origin, src, word_urlify, replacement_origin=None):
    try:
        G = list(iter(helper.parse_and_graph(query, wikiresponse, origin, replacement_origin=replacement_origin)))
    except Exception as e:
        print(src)
        print(f"https://en.wiktionary.org/wiki/{word_urlify}")
        raise e

    print(src)
    print(f"https://en.wiktionary.org/wiki/{word_urlify}")
    assert len(G) == 1 # assert only 1 graph
    return G[0], origin




GG, origin = graph(*query(original_query))
draw_graph(GG, origin)
_ = [print(x) for x in GG.nodes]
while(not original_query): # if original query is "", then keep repeating it
    _query = query(original_query) # parse the query
    _, _, query_origin, _, _ = _query # extract from origin of query from variable scope dump
    GG_origin = helper.contains_originator(GG, query_origin)
    # We want to connect these two graphs,
    # so we take our query's origin and try to find
    # a node from our big, working tree GG.

    G, origin = graph(*_query, replacement_origin=GG_origin)
    draw_graph(G, origin)

    if GG_origin:
        # good, we found a connection
        # fuse the graphs, which should now be connected because we fused and forced our tree G to use a preexisting origin.
        GG2 = nx.compose(GG, G)
    else:
        warnings.warn("Unconnected query " + str(origin))
        GG = G
        continue



    """
    # connect G to GG
    common_link = helper.contains_originator(GG, origin)
    GG2 = nx.compose(GG, G)
    if common_link:
        GG2.add_edge(origin, common_link)
    else:
        raise Exception("Unconnected query " + origin)
    """
    _ = [print(x) for x in GG.nodes]
    draw_graph(GG2, origin)
    GG = GG2



