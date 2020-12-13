import builtins
import json
import pickle
import string
import urllib
import warnings

import grandalf
import mwparserfromhell as mwp
import requests
from mwparserfromhell.wikicode import Wikicode

from pyetymology.helperobjs import query2
from pyetymology.helperobjs.langhelper import Lang
from pyetymology.helperobjs.querying import ThickQuery
from pyetymology.langcode.cache import Cache
import grandalf.utils as grutils
import networkx as nx

import matplotlib
# matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

import pyetymology.etyobjects
from pyetymology import simple_sugi, lexer
import pyetymology.langcode as langcode

### START helper_api.py
from typing import List, Generator, Dict, Any, Tuple

import mwparserfromhell
# from mwparserfromhell.wikicode import Wikicode

from pyetymology.etyobjects import EtyRelation, Originator, LemmaRelation, MissingException
from pyetymology.lexer import Header
from pyetymology.module import moduleimpl


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


def sections_by_level(sections: List[Wikicode], level: int, recursive=True, flat=False) -> Generator[Wikicode, None, None]:
    """
    Takes in parameter l, which corresponds to a "main" heading level.
    Yields each "main" header of that specified heading level.
    If there is a subheader, it will be packaged after the specified main header that precedes it
    """

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

            # Antiredundance removed b/c of possible injection; plus, there's a better way of making mwp return it flat in query()
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

    if builder:
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


def all_lang_sections(sections: List[Wikicode], recursive=False, flat=True) -> Generator[Wikicode, None, None]:
    return sections_by_level(sections, 2, recursive=recursive, flat=flat)


_is_plot_active = False


def is_in(elem, abbr_set: Dict[str, str]):
    return elem in abbr_set.keys() or elem in abbr_set.values()


def contains_originator(G: nx.Graph, origin: Originator):
    """
    Returns the node that contains the originator; otherwise returns false
    """
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


def wikitextparse(wikitext: str, redundance=False) -> Tuple[Wikicode, List[Wikicode]]:
    res = mwp.parse(wikitext)  # type: Wikicode
    # res = wtp.parse(wikitext)
    dom = res.get_sections(flat=not redundance)
    return res, dom


"""
Returns sections of only 1 lang
"""


def reduce_to_one_lang(dom: List[Wikicode], use_lang=None, permit_abbrevs=True) -> Tuple[List[Wikicode], str, str, str]:
    lang = ""
    # try to extract lang from dom
    found_langs = all_lang_sections(dom, flat=True)

    def _compr(found_langs):
        for found_lang in found_langs:
            found_lang: Wikicode
            h = found_lang[2:]  # EDIT: with flat=True, disregard the following. found_lang should be array of length 1, because recursive is false
            yield h[:h.index("==")]

    lang_options = list(_compr(found_langs))
    if len(lang_options) == 0:
        raise MissingException("Zero langs detected !? !?", missing_thing="language_sections")
    elif len(lang_options) == 1:
        lang = lang_options[0]
    else:
        if not lang:
            if use_lang:
                usrin = use_lang
            else:
                usrin = input("Choose a lang from these options: " + str(lang_options))
            if usrin in lang_options:
                lang = usrin
            elif permit_abbrevs:
                for lang_opt in lang_options: # abbreviations
                    if str.lower(lang_opt).startswith(str.lower(usrin)):
                        lang = lang_opt
            if not lang:
                raise MissingException(f"Your input \"{usrin}\" is not recognized in the options {str(lang_options)}", missing_thing="language_section")

    # me = word + "#" + lang
    lang_secs = list(sections_by_lang(dom, lang))

    if not lang_secs:
        raise MissingException(f"No entry was found in wikitext under language {lang} !? !? "
                               f"(Unless there is a bug, this exception shouldn't be called!) DOM: \n\t{repr(dom)}", missing_thing="language_section")
    return lang_secs, lang


def query(me, query_id=0, mimic_input=None, redundance=False, working_G: nx.DiGraph=None) -> ThickQuery:
    if not me:
        me = input("Enter a query: " + me)

    found = False
    if working_G:
        node = find_existent_query(working_G, me)
        word, lang, def_id = query2.node_to_qparts(node)
        found = word or lang
    if not found:
        word, lang, def_id = query2.query_to_qparts(me)
    if lang is None:
        lang = Lang()
    # word_urlify = urllib.parse.quote_plus(word)
    # src = "https://en.wiktionary.com/w/api.php?action=parse&page=" + word_urlify + "&prop=wikitext&formatversion=2&format=json"
    src = moduleimpl.to_link(word, lang.langname) # we take the word and lang and parse it into the corresponding wikilink
    # TODO: we don't know that the lang is Latin until after we load the page if we're autodetecting
    # TODO: and to load the page we need to know the word_urlify
    # TODO: and word_urlify must remove macrons
    # https://en.wiktionary.com/w/api.php?action=parse&page=word&prop=wikitext&formatversion=2&format=json
    if online:
        global session
        res = session.get(src)
        #cache res TODO: implement better caching with test_'s fetch stuff
    else:
        raise Exception("offline browsing not implemented yet")

    txt = res.text
    jsn = json.loads(txt) #type: json
    if "parse" in jsn:
        wikitext = jsn["parse"]["wikitext"]
    elif "error" in jsn:
        print(src)
        print(f"https://en.wiktionary.org/wiki/{moduleimpl.urlword(word, lang.langname)}")
        raise MissingException("Response returned an error! Perhaps the page doesn't exist? \nJSON: " + str(jsn["error"]), missing_thing="Everything")
    else:
        raise Exception("Response malformed!" + str(jsn))
    # print(wikitext)

    res, dom = wikitextparse(wikitext, redundance=redundance)
    # Here was the lang detection

    dom, langname = reduce_to_one_lang(dom, use_lang=mimic_input if mimic_input else lang.langname)
    me = word + "#" + langname
    assert word
    assert langname

    origin = Originator(me, o_id=query_id)
    bigQ = ThickQuery(me=me, word=word, langname=langname, def_id=def_id, res=res, wikitext=wikitext, dom=dom, origin=origin)
    return bigQ



def find_existent_query(GG: nx.DiGraph, query: str):
    # _ = [print(x) for x in GG.nodes]
    for node in GG.nodes:
        if type(node) is EtyRelation:
            node: EtyRelation
            if node.matches_query(query):
                return node
        elif type(node) is LemmaRelation:
            node: LemmaRelation
            if node.matches_query(query):
                return node
        elif type(node) is Originator:
            warnings.warn("Why is it matching the originator?")
        else:
            raise ValueError(f"node has unexpected type {type(node)}")


def parse_and_graph(_Query, existent_node: EtyRelation=None, make_mentions_sideways=False) -> nx.DiGraph:
    me, word, lang, def_id = _Query.query
    dom = _Query.dom
    query_origin = _Query.origin
    existent_origin = existent_node if existent_node else query_origin # TODO: pass replacement_origin through origin constructor to wrap and create an origin _id
    prev = existent_origin # origin that is guaranteed already exists
    # TODO: existent node and the origin must be the same, or else they don't compose properly.
    # TODO: brainstorm workarounds. ie. OriginsTracker. TODO: finish implementing that
    new_origin = query_origin  #type: Originator # new_origin should have the updated o_id
    ety_flag = False
    lemma_flag = False

    def add_node(G, node, color=None):
        assert type(node) in [EtyRelation, LemmaRelation, Originator]
        global colors
        color = colors[node.o_id] if color is None else color
        G.add_node(node, id=node.o_id, color=color)

    G = nx.DiGraph()

    if type(prev) is Originator and prev.o_id == 0:
        # True Origin
        add_node(G, prev, color="#ff0000")
    else:
        add_node(G, prev)
    # if replacement_origin is not the origin, then that means that the origin was replaced
    # by a preexisting node that was already colored
    # therefore we should not colorize it

    entries = lexer.lex2(dom)  #type: List[Entry]
    if def_id is None and len(entries) > 1:
        def_id = input("Multiple definitions detected. Enter an ID: ")
        if def_id == "":
            def_id = 1
        entry = entries[int(def_id) - 1] # wiktionary is 1-indexed, but our lists are 0-indexed
    # for entry in entries.entrylist:
    else:
        entry = entries[0]
    # sec = entry.main_sec


    # if sec.startswith("===Etymology===") or sec.startswith(f"===Etymology {def_id}"):
    # if entry.entry_type == "Etymology":
    ety = entry.ety #type: Header
    if ety:
        assert (len(entries) > 1) == (ety.idx is not None)
        # if multi_ety, then the idx should not be None
        # and vice versa: if single ety, then idx should be None
        assert ety.idx is None or ety.idx == int(def_id)  # if either there's no idx, or the idx matches, continue
        if not ety_flag:
            ety_flag = True
        else:
            raise Exception("Etymology is being parsed twice? This should be impossible")

        dotyet = False
        firstsentence = []
        for node in ety.wikicode.ifilter(recursive=False):  # type: mwp.wikicode.Node
            # .filter_templates(): #type: mwp.wikicode.Template
            # if etytemp

            if isinstance(node, mwp.wikicode.Template):
                etyr = EtyRelation(new_origin, node)
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
    #if sec.startswith("===Verb===") or sec.startswith(f"===Verb {def_id}"):
    # for subsec in sections_by_level(entry.subordinates, 4):
    for defn in entry.extras:  # type: Header
        assert defn is None or isinstance(defn, Header)
        if defn.metainfo != "Definition":
            continue
        lemma_rels = []
        for node in defn.wikicode.ifilter(recursive=False):
            if isinstance(node, mwp.wikicode.Template):
                node: mwp.wikicode.Template
                templ_name = node.name
                if templ_name[-3:] == " of":
                    if ety_flag:
                        raise Exception("both Ety and Lemma are being parsed?")
                    #lang = node.params[0]
                    # word = node.params[1]
                    # print(f"Found lemma?: lang: {lang} word: {word}")
                    lemma_rel = LemmaRelation(query_origin, node)
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

    if not ety_flag:
        if lemma_flag:
            pass  # raise MissingException("Definition detected, but etymology not detected. (Perhaps it's lemmatized?)", missing_thing="etymology")
        else:
            raise MissingException("Neither definition nor etymology detected.", missing_thing="definition", G=G)
    return G


# def graph(query, wikiresponse, origin, src, word_urlify, replacement_origin=None):
def graph(_Query: ThickQuery, replacement_origin=None) -> nx.DiGraph:
    try:
        G = parse_and_graph(_Query, existent_node=replacement_origin)
    except MissingException as e:
        if e.missing_thing == "definition":
            warnings.warn(str(e))
            G = e.G
            # DID: soft crash
        else:
            raise e
    except Exception as e:
        raise e
    finally:
        print(_Query.wikitext_link)
        print(f"https://en.wiktionary.org/wiki/{_Query.word_urlify}")

    # print(len(G))
    assert type(G) == nx.DiGraph # assert only 1 graph
    return G

# addition F55D3E-
colors = ["#B1D4E0", "#2E8BC0", "#878E88", "#F7CB15", "#76BED0", "#0C2D48", "#145DA0", "#1f78b4"]  #

def draw_graph(G, simple=False, pause=False):
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
    if node_colors:
        nx.draw(G, pos=poses, with_labels=True, node_color=node_colors.values())
    else:
        global colors
        node_colors = {node: colors[node.o_id] for node in G.nodes}
        nx.draw(G, pos=poses, with_labels=True, node_color=node_colors.values())

    # x.draw_networkx_edges(G, pos=poses)

    if pause:
        plt.show()
    else:
        # plt.pause(0.01) pauses for 0.01s, and runs plt's GUI main loop
        plt.pause(0.01)
    global _is_plot_active
    _is_plot_active = True