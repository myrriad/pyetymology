import grandalf
import mwparserfromhell as mwp

import pyetymology.etyobjects
from pyetymology import helper_api as helper
import networkx as nx
import pyetymology.langcode as langcode
import matplotlib.pyplot as plt

colors = ["#B1D4E0", "#2E8BC0", "#0C2D48", "#145DA0", "#1f78b4"]  #
def parse_and_graph(wikitext, origin, word, lang, def_id, replacement_origin=None):

    if replacement_origin is None:
        replacement_origin = origin
    res = mwp.parse(wikitext)
    # res = wtp.parse(wikitext)

    dom = res.get_sections()
    # print(pprint(dom))
    if not lang or lang == "" or lang is None:
        # try to extract lang from dom
        found_langs = helper.all_lang_sections(dom)
        def _compr(found_langs):
            for found_lang in found_langs:
                h = found_lang[0][2:] # found_lang should be array of length 1, because recursive is false
                yield h[:h.index("==")]
        lang_options = list(_compr(found_langs))
        if len(lang_options) == 1:
            lang = lang_options[0]
        else:
            lang = input("Choose a lang from these options: " + str(lang_options))

    dom = helper.sections_by_lang(dom, lang)

    _exhausted = object()
    if not dom or next(dom, _exhausted) == _exhausted:
        raise Exception(f"Word \"{word}\" has no entry under language {lang}")

    ety_flag = False
    lemma_flag = False
    sections = helper.sections_by_level(dom, 3)

    def add_node(G, node, colorize=True):
        if colorize:
            global colors
            color = colors[origin.o_id]
            G.add_node(node, id=origin.o_id, color=color)
        else:
            G.add_node(node, id=origin.o_id)

    for sec in sections:

        if (sec[0].startswith("===Etymology") and not sec[0].startswith("===Etymology===")) \
                or (sec[0].startswith("===Verb") and not sec[0].startswith("===Verb===")):
            # Therefore, if it starts with something like ===Etymology 1===
            if def_id is None:
                def_id = input("Multiple definitions detected. Enter an ID: ")
        """
        if sec[0].startswith("===Verb===") or sec[0].startswith(f"===Verb {def_id}"):
            for subsec in helper.sections_by_level(sec, 4):
                for node in sec[0].ifilter(recursive=False):
                    if isinstance(node, mwp.wikicode.Template):

                        pass# print("-"+repr(subsec))
        """

        if sec[0].startswith("===Etymology===") or sec[0].startswith(f"===Etymology {def_id}"):
            if not ety_flag:
                ety_flag = True
            else:
                raise Exception("Etymology is being parsed twice? ")
            # for node in sec[0].ifilter_templates(): #type: mwp.wikicode.Template
            #     sec[0].remove(node)

            dotyet = False
            firstsentence = []
            for node in sec[0].ifilter(recursive=False):  # type: mwp.wikicode.Node
                # .filter_templates(): #type: mwp.wikicode.Template
                # if etytemp

                if isinstance(node, mwp.wikicode.Template):
                    etyr = pyetymology.etyobjects.EtyRelation(origin, node)
                    # print(str(etyr))
                    if not dotyet:
                        firstsentence.append(etyr)

                else:
                    # print(str(node))
                    if not dotyet:  # if we're in the first sentence
                        if ("." in node):  # if we reach the end
                            firstsentence.append(
                                node[:node.index(".") + 1])  # get everything up to, and including, the period
                            dotyet = True
                        else:
                            firstsentence.append(
                                node)  # if we haven't reached the period, we're in the middle. capture that node

            print("1st sentence is " + repr(firstsentence))
            ancestry = []

            G = nx.DiGraph()
            # prev = origin
            prev = replacement_origin
            # add_node(G, origin)
            add_node(G, replacement_origin, colorize=replacement_origin is origin)
            # if replacement_origin is not the origin, then that means that the origin was replaced
            # by a preexisting node that was already colored
            # therefore we should not colorize it

            between_text = []

            check_type = False
            cache = langcode.cache.Cache(4)
            for token in firstsentence:  # time to analyze the immediate etymology ("ancestry")
                if token is None:
                    continue
                if isinstance(token, pyetymology.etyobjects.EtyRelation):
                    token: pyetymology.etyobjects.EtyRelation
                    cache.put(token)

                    if any(helper.is_in(token.rtype, x) for x in
                           (pyetymology.etyobjects.EtyRelation.ety_abbrs, pyetymology.etyobjects.EtyRelation.aff_abbrs,
                            pyetymology.etyobjects.EtyRelation.sim_abbrs)):
                        # inh, der, bor, m
                        # print(between_text)
                        if any("+" in s for s in
                               between_text):  # or helper_api.is_in(token.rtype, helper_api.EtyRelation.aff_abbrs):
                            prevs_parents = G.edges(nbunch=prev)  #
                            # prev2 = cache.nth_prev(2)
                            # print("parnt: " + str(parnt))
                            parnt = next(iter(prevs_parents), (None, None))[1]
                            # parnt = prev2
                            add_node(G, token)
                            G.add_edge(token, parnt)
                            # print(cache.array)

                            # sister node
                        else:
                            add_node(G, token)
                            if prev:
                                G.add_edge(token, prev)
                        prev = token
                    else:
                        print(token)
                    between_text = []
                else:
                    between_text.append(token)

            yield G
        else:
            pass  # print(repr(sec))
    if not ety_flag and not lemma_flag:
        raise Exception("Etymology not detected. (If a word has multiple definitions, you must specify it.)")
