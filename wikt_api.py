import builtins
import json
import pickle
import string
import urllib

import grandalf
import mwparserfromhell as mwp
import requests
from mwparserfromhell.wikicode import Wikicode

from pyetymology.langcode.cache import Cache
import grandalf.utils as grutils
import networkx as nx

import matplotlib
# matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

import pyetymology.etyobjects
from pyetymology import simple_sugi
import pyetymology.langcode as langcode

### START helper_api.py
from typing import List, Generator, Dict, Any, Tuple

import mwparserfromhell
# from mwparserfromhell.wikicode import Wikicode

from pyetymology.etyobjects import EtyRelation, Originator, LemmaRelation, MissingException


def input(__prompt: Any) -> str:
    global _is_plot_active
    if _is_plot_active:
        print("Close MatplotLib to Continue")
        plt.show()
    return builtins.input(__prompt)

online = True # TODO: online=False displays wrong versions of ety trees without throwing an exception

session = requests.Session()
session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))  # retry up to 2 times
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))


def has_exact_prefix(str, prefix):
    return str.startswith(prefix) and not str.startswith(prefix + "=")


"""
Takes in parameter l, which corresponds to a "main" heading level.
Yields each "main" header of that specified heading level.
If there is a subheader, it will be packaged after the specified main header that precedes it

"""


def sections_by_level(sections: List[Wikicode], level: int, recursive=True, flat=False, antiredundance=False) -> Generator[List[Wikicode], None, None]:


    in_section = False
    prefix = "=" * level
    childprefix = prefix + "="
    builder = []

    def yieldme(builder):
        if not recursive and flat:
            assert len(builder) == 1
            return builder[0]
        else:
            return builder
    for sec in sections:

        if has_exact_prefix(sec, prefix):  # we've reached the next header
            if in_section:
                yield yieldme(builder) # if we're already in section, that means yield previous work
            else:
                in_section = True # don't yield if we're just starting out, as it will be empty

            if antiredundance: # if we're antiredundance,
                # substring our string to cut out the children, which automatically come packaged with the parent
                # TODO: possible injection
                try:
                    added = sec[:str(sec).index(childprefix)]
                except ValueError:
                    added = sec
            else:
                added = sec
            builder = [added]  # start building
            continue
        if not in_section: # skip everything until we get to our first header
            continue
        if sec.startswith(childprefix):  # if it's a child (this will be skipped until we actually get in to the first section.)
            if recursive:
                builder.append(sec)
            continue
        break # we're in section, but it's neither a child nor a sibling, therefore it's a parent and we should exit.

    yield yieldme(builder) # yield stragglers


def sections_by_lang(sections: List[Wikicode], lang: string) -> Generator[Wikicode, None, None]:
    in_section = False
    for sec in sections:

        if not in_section and sec.startswith("==" + lang):  # we've reached the desired section
            # print(repr(sec))
            in_section = True
            yield sec
            continue
        if in_section and sec.startswith("==="):
            # print(repr(sec))
            yield sec
            continue
        if in_section and has_exact_prefix(sec, "=="):  # we've reached the next header
            in_section = False
            break


def all_lang_sections(sections: List[Wikicode], recursive=False, flat=True, antiredundance=False) -> Generator[List[Wikicode], None, None]:
    return sections_by_level(sections, 2, recursive, flat, antiredundance)


_is_plot_active = False
def draw_graph(G, origin, simple=False):
    print("...drawing graph...")

    if simple:
        poses = simple_sugi.pos(G)
    else:
        g = grutils.convert_nextworkx_graph_to_grandalf(G)
        from grandalf.layouts import SugiyamaLayout

        class DefaultView(object):
            w, h = 10, 10

        for v in g.V(): v.view = DefaultView()
        sug = SugiyamaLayout(g.C[0])
        sug.init_all()  # roots=[V[0]]) #, inverted_edges=[V[4].e_to(V[0])])
        sug.draw()
        poses = {v.data: (-v.view.xy[0], -v.view.xy[1]) for v in g.C[0].sV}

    node_colors = nx.get_node_attributes(G, 'color')
    nx.draw(G, pos=poses, with_labels=True, node_color=node_colors.values())
    # x.draw_networkx_edges(G, pos=poses)

    # plt.show()
    # plt.pause(0.01) pauses for 0.01s, and runs plt's GUI main loop
    plt.pause(0.01)
    global _is_plot_active
    _is_plot_active = True


def is_in(elem, abbr_set: Dict[str, str]):
    return elem in abbr_set.keys() or elem in abbr_set.values()


"""
Returns the node that contains the originator; otherwise returns false
"""


def contains_originator(G: nx.Graph, origin: Originator):
    for node in G.nodes:
        if isinstance(node, EtyRelation):
            node: EtyRelation
            if node.matches_query(origin.me):
                return node
        if isinstance(node, LemmaRelation):
            node: LemmaRelation
            if node.matches_query(origin.me):
                return node
    return None


### END helper_api.py


colors = ["#B1D4E0", "#2E8BC0", "#0C2D48", "#145DA0", "#1f78b4"]  #


def wikitextparse(wikitext: str, redundance=True) -> Tuple[Wikicode, List[Wikicode]]:
    res = mwp.parse(wikitext)  # type: Wikicode
    # res = wtp.parse(wikitext)

    dom = res.get_sections(flat=not redundance)

    return res, dom


"""
Returns sections of only 1 lang
"""


def auto_lang(dom: List[Wikicode], me: str, word: str, lang: str, mimic_input=None) -> Tuple[List[Wikicode], str, str, str]:
    if not lang or lang == "" or lang is None:
        # try to extract lang from dom
        found_langs = all_lang_sections(dom, flat=True)

        def _compr(found_langs):
            for found_lang in found_langs:
                h = found_lang[2:]  # EDIT: with flat=True, disregard the following. found_lang should be array of length 1, because recursive is false
                yield h[:h.index("==")]

        lang_options = list(_compr(found_langs))
        if len(lang_options) == 1:
            lang = lang_options[0]
        else:
            while not lang or lang == "" or lang is None:
                if mimic_input:
                    lang = mimic_input
                else:
                    lang = input("Choose a lang from these options: " + str(lang_options))

    me = word + "#" + lang
    lang_secs = list(sections_by_lang(dom, lang))

    if not lang_secs:
        raise MissingException(f"Word \"{word}\" has no entry under language {lang}", missing_thing="language_section")
    return lang_secs, me, word, lang

def parse_and_graph(query, wikiresponse, origin, replacement_origin=None, make_mentions_sideways=False) -> nx.DiGraph:
    return _parse_and_graph(query, wikiresponse, origin, replacement_origin, make_mentions_sideways)
def _parse_and_graph(query, wikiresponse, origin, replacement_origin, make_mentions_sideways):
    me, word, lang, def_id = query
    _, _, dom = wikiresponse  # res, wikitext, dom
    if replacement_origin is None:
        replacement_origin = origin

    ety_flag = False
    lemma_flag = False
    sections = sections_by_level(dom, 3)



    def add_node(G, node, color_id=None):
        if color_id is None:
            global colors
            color = colors[origin.o_id]
        else:
            color = colors[color_id]
        G.add_node(node, id=origin.o_id, color=color)

    G = nx.DiGraph()
    prev = replacement_origin

    add_node(G, replacement_origin, color_id=replacement_origin.color_id if replacement_origin else None)
    # if replacement_origin is not the origin, then that means that the origin was replaced
    # by a preexisting node that was already colored
    # therefore we should not colorize it

    for sec in sections:

        # TODO: All parts of speech at https://en.wiktionary.org/wiki/Wiktionary:Entry_layout#:~:text=Parts%20of%20speech
        if (sec[0].startswith("===Etymology") and not sec[0].startswith("===Etymology===")) \
                or (sec[0].startswith("===Verb") and not sec[0].startswith("===Verb===")):
            # Therefore, if it starts with something like ===Etymology 1===
            if def_id is None:
                def_id = input("Multiple definitions detected. Enter an ID: ")
                if def_id == "":
                    def_id = 1

        # TODO: https://en.wiktionary.org/wiki/Wiktionary:Entry_layout#:~:text=Parts%20of%20speech
        if sec[0].startswith("===Verb===") or sec[0].startswith(f"===Verb {def_id}"):
            # LEMMA https://en.wiktionary.org/wiki/Category:Form-of_templates
            # https://en.wiktionary.org/wiki/Module:form_of/data
            # Wiktionary templates: https://en.wiktionary.org/wiki/Category:Template_interface_modules
            # all templates: https://en.wiktionary.org/wiki/Special:AllPages?from=&to=&namespace=10
            # ^^ Note: Capitals are displayed before lowercase
            # Note: spaces are replaced with underlines in urls

            for subsec in sections_by_level(sec, 4):

                lemma_rels = []
                for node in sec[0].ifilter(recursive=False):
                    if isinstance(node, mwp.wikicode.Template):
                        node: mwp.wikicode.Template
                        templ_name = node.name
                        if templ_name[-3:] == " of":
                            if ety_flag:
                                raise Exception("both Ety and Lemma are being parsed?")
                            #lang = node.params[0]
                            # word = node.params[1]
                            # print(f"Found lemma?: lang: {lang} word: {word}")
                            lemma_rel = LemmaRelation(origin, node)
                            # print("-"+repr(subsec))
                            lemma_flag = True

                            if not any(lemma_rel.matches(x) for x in lemma_rels): # if it doesn't match any
                                lemma_rels.append(lemma_rel)
                                # Start graphing
                                add_node(G, lemma_rel)
                                if prev:
                                    G.add_edge(lemma_rel, prev)
                                    # prev = lemma_rel



            # Basic methodology: detect if a template ends in " of", such as "past participle of"

            # lemma_flag = True


        if sec[0].startswith("===Etymology===") or sec[0].startswith(f"===Etymology {def_id}"):
            if not ety_flag:
                ety_flag = True
            else:
                raise Exception("Etymology is being parsed twice? ")
            if lemma_flag:
                raise Exception("Both Lemma and Ety are being parsed?")
            # for node in sec[0].ifilter_templates(): #type: mwp.wikicode.Template
            # sec[0].remove(node)

            dotyet = False
            firstsentence = []
            for node in sec[0].ifilter(recursive=False):  # type: mwp.wikicode.Node
                # .filter_templates(): #type: mwp.wikicode.Template
                # if etytemp

                if isinstance(node, mwp.wikicode.Template):
                    etyr = EtyRelation(origin, node)
                    # print(str(etyr))
                    if not dotyet:
                        firstsentence.append(etyr)

                else:
                    # print(str(node))
                    if not dotyet:  # if we're in the first sentence
                        if isinstance(node, mwparserfromhell.wikicode.Text) and "." in node:  # if we reach the end
                            firstsentence.append(
                                node[:node.index(".") + 1])  # get everything up to, and including, the period
                            dotyet = True
                        else:
                            firstsentence.append(
                                node)  # if we haven't reached the period, we're in the middle. capture that node

            print("1st sentence is " + repr(firstsentence))
            ancestry = []

            # prev = origin
            # start graphing

            between_text = []

            check_type = False
            cache = Cache(4)
            for token in firstsentence:  # time to analyze the immediate etymology ("ancestry")
                if token is None:
                    continue
                if isinstance(token, EtyRelation):
                    token: EtyRelation
                    cache.put(token)

                    if any(is_in(token.rtype, x) for x in
                           (EtyRelation.ety_abbrs, EtyRelation.aff_abbrs,
                            EtyRelation.sim_abbrs)):
                        # inh, der, bor, m
                        if any("+" in s for s in
                               between_text):  # or helper_api.is_in(token.rtype, helper_api.EtyRelation.aff_abbrs):
                            prevs_parents = G.edges(nbunch=prev)  #
                            parnt = next(iter(prevs_parents), (None, None))[1]
                            # parnt = prev2
                            add_node(G, token)
                            G.add_edge(token, parnt)

                            # sister node
                        else:
                            add_node(G, token)
                            if prev:
                                G.add_edge(token, prev)
                        if make_mentions_sideways and is_in(token.rtype, EtyRelation.sim_abbrs):
                            pass # if a mention
                        else:
                            prev = token
                    else:
                        print(token)
                    between_text = []
                else:
                    between_text.append(token)

            # yield G
        else:
            pass  # print(repr(sec))
    if not ety_flag:
        if lemma_flag:
            pass
            # raise MissingException("Definition detected, but etymology not detected. (Perhaps it's lemmatized?)", missing_thing="etymology")
        else:
            raise MissingException("Neither definition nor etymology detected.", missing_thing="definition")
    return G


def query(me, mimic_input=None, redundance=False):
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

    word_urlify = urllib.parse.quote_plus(word)
    src = "https://en.wiktionary.com/w/api.php?action=parse&page=" + word_urlify + "&prop=wikitext&formatversion=2&format=json"
    # https://en.wiktionary.com/w/api.php?action=parse&page=word&prop=wikitext&formatversion=2&format=json

    if online:
        global session
        res = session.get(src)

        #cache res
        with open('response.pkl', 'wb') as output:
            pickle.dump(res, output, pickle.HIGHEST_PROTOCOL)
    else:
        with open('response.pkl', 'rb') as _input:
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

    res, dom = wikitextparse(wikitext, redundance=redundance)
    # Here was the lang detection

    dom, me, word, lang = auto_lang(dom, me, word, lang, mimic_input=mimic_input)
    assert me
    assert word
    assert lang
    assert len(me.split("#")) >= 2

    query = (me, word, lang, def_id)
    wikiresponse = (res, wikitext, dom)
    origin = Originator(me)
    return query, wikiresponse, origin, src, word_urlify
def graph(query, wikiresponse, origin, src, word_urlify, replacement_origin=None):
    try:
        G = parse_and_graph(query, wikiresponse, origin, replacement_origin=replacement_origin)
    except MissingException as e:
        #if e.missing_thing == "etymology":
            #print(e)
            #return
        #else:
        raise e
    except Exception as e:
        raise e
    finally:
        print(src)
        print(f"https://en.wiktionary.org/wiki/{word_urlify}")

    # print(len(G))
    assert type(G) == nx.DiGraph # assert only 1 graph
    return G, origin