import mwparserfromhell
import mwparserfromhell as mwp
# import wikitextparser as wtp
import requests
import json

from pyetymology import helper_api, helper_api as helper

import networkx as nx #rumored to be slow, but I'm just using it temporarily
import grandalf.graphs as grand

import pyetymology.langcode.cache
import pickle

import matplotlib.pyplot as plt

online = False

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
    with open('response.pkl', 'wb') as output:
        pickle.dump(res, output, pickle.HIGHEST_PROTOCOL)
else:
    with open('response.pkl', 'rb') as _input:
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
res = mwp.parse(wikitext)
# res = wtp.parse(wikitext)


dom = res.get_sections()
# print(pprint(dom))
dom = helper.get_by_lang(dom, lang)

_exhausted = object()
if not dom or next(dom, _exhausted) == _exhausted:
    raise Exception(f"Word \"{word}\" has no entry under language {lang}")

ety_flag = False
sections = helper.get_by_level(dom, 3)

for sec in sections:

    """
    if sec[0].startswith("===Verb==="):
        for subsec in helper.get_by_level(sec, 4):
            pass# print("-"+repr(subsec))
    el"""
    if sec[0].startswith("===Etymology") and not sec[0].startswith("===Etymology==="):
        #Therefore, if it starts with something like ===Etymology 1===
        if def_id is None:
            def_id = input("Multiple definitions detected. Enter an ID: ")
    if sec[0].startswith("===Etymology===") or sec[0].startswith(f"===Etymology {def_id}"):
        if not ety_flag:
            ety_flag = True
        else:
            raise Exception("Etymology is being parsed twice? ")
        # for node in sec[0].ifilter_templates(): #type: mwparserfromhell.wikicode.Template
        #     sec[0].remove(node)

        dotyet = False
        firstsentence = []
        for node in sec[0].ifilter(recursive=False): #type: mwparserfromhell.wikicode.Node
            # .filter_templates(): #type: mwparserfromhell.wikicode.Template
            # if etytemp

            if isinstance(node, mwparserfromhell.wikicode.Template):
                etyr = helper.EtyRelation(node)
                # print(str(etyr))
                if not dotyet:
                    firstsentence.append(etyr)

            else:
                # print(str(node))
                if not dotyet: # if we're in the first sentence
                    if("." in node): # if we reach the end
                        firstsentence.append(node[:node.index(".") + 1]) # get everything up to, and including, the period
                        dotyet = True
                    else:
                        firstsentence.append(node) # if we haven't reached the period, we're in the middle. capture that node


        print("1st " + repr(firstsentence))
        ancestry = []
        G = nx.DiGraph()
        prev = me
        G.add_node(me, pos=(0,0))

        between_text = []

        check_type = False
        cache = pyetymology.langcode.cache.Cache(4)
        for bib in firstsentence: # time to analyze the immediate etymology ("ancestry")
            if bib is None:
                continue
            if isinstance(bib, helper.EtyRelation):
                bib: helper.EtyRelation
                cache.put(bib)

                if any(helper_api.is_in(bib.rtype, x) for x in (helper.EtyRelation.ety_abbrs, helper.EtyRelation.aff_abbrs, helper.EtyRelation.sim_abbrs)):
                    # inh, der, bor, m
                    # print(between_text)
                    if any("+" in s for s in between_text): # or helper_api.is_in(bib.rtype, helper_api.EtyRelation.aff_abbrs):
                        prevs_parents = G.edges(nbunch=prev) #
                        # prev2 = cache.nth_prev(2)
                        # print("parnt: " + str(parnt))
                        parnt = next(iter(prevs_parents),(None, None))[1]
                        # parnt = prev2
                        G.add_node(bib)
                        G.add_edge(bib, parnt)
                        # print(cache.array)

                        # sister node
                    else:
                        G.add_node(bib)
                        if prev:
                            G.add_edge(bib, prev)
                    prev = bib
                else:
                    print(bib)
                between_text = []
            else:
                between_text.append(bib)



        print("...drawing graph...")
        # print(G.size())
        pos = nx.get_node_attributes(G, 'pos')
        '''
        spring = nx.spring_layout(G, pos={me:(0,0)}, fixed=[me])
        nx.draw(G, pos=spring, with_labels=True)
        '''
        # p = nx.drawing.nx_pydot.to_pydot(G)
        # p.write_png('example.png', encoding="utf-8")
        """
        import temp
        pos = temp.hierarchy_pos(G)
        # pos = [(x, -y) for (x, y) in pos]
        nx.draw(G, pos=pos, with_labels=True)
        import matplotlib.pyplot as plt
        plt.show()
        """
        Vdict = {n : grand.Vertex(n) for n in G.nodes}
        V = list(Vdict.values())
        E = [grand.Edge(Vdict[e[0]], Vdict[e[1]]) for e in G.edges]
        g = grand.Graph(V, E)
        from grandalf.layouts import SugiyamaLayout

        class defaultview(object):
            w, h = 10, 10


        for v in V: v.view = defaultview()
        sug = SugiyamaLayout(g.C[0])
        sug.init_all() # roots=[V[0]]) #, inverted_edges=[V[4].e_to(V[0])])
        sug.draw()
        poses = {v.data: (-v.view.xy[0], -v.view.xy[1]) for v in g.C[0].sV}
        nx.draw(G, pos=poses, with_labels=True)
        plt.show()

    else:
        pass # print(repr(sec))

if not ety_flag:
    print("Etymology not detected. (If a word has multiple definitions, you must specify it.)")
