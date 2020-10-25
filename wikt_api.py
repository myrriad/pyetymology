import mwparserfromhell
import mwparserfromhell as mwp
# import wikitextparser as wtp
import requests
import json

from pyetymology import helper_api as helper, wikt_api_parser

import networkx as nx #rumored to be slow, but I'm just using it temporarily
import grandalf.graphs as grand

import pyetymology.langcode.cache
import pickle

import matplotlib.pyplot as plt

online = True

session = requests.Session()
session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))  # retry up to 2 times
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))

me = "lleno#Spanish"#llenar#Spanish"#"conflate#English"
#"llegar#Spanish"
#me = "Reconstruction:Proto-Italic/feiljos#"
terms = me.split("#")
def_id = None
if len(terms) == 2:
    word, lang = terms
elif len(terms) == 3:
    word, lang, def_id = terms
else:
    raise Exception(f'Query string "{me}" has an unsupported number of arguments! There should be either one or two \'#\'s only,')

src = "https://en.wiktionary.com/w/api.php?action=parse&page=" + word + "&prop=wikitext&formatversion=2&format=json"
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
json = json.loads(txt) #type: json
if "parse" in json:
    wikitext = json["parse"]["wikitext"]
elif "error" in json:
    raise Exception("Response returned an error! Perhaps the page doesn't exist? \nJSON: " + str(json["error"]))
else:
    raise Exception("Response malformed!" + str(json))
# print(wikitext)

wikt_api_parser.ety_parse_routine(wikitext, me, word, lang, def_id)




