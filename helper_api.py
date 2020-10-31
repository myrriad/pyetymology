from typing import List, Generator, Dict

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

from pyetymology.etyobjects import EtyRelation, Originator


def has_exact_prefix(str, prefix):
    return str.startswith(prefix) and not str.startswith(prefix + "=")


"""
Takes in parameter l, which corresponds to a "main" heading level.
Yields each "main" header of that specified heading level.
If there is a subheader, it will be packaged after the specified main header that precedes it


"""


def sections_by_level(sections: List[Wikicode], level: int, recursive=True) -> Generator[List[Wikicode], None, None]:
    in_section = False
    prefix = "=" * level
    childprefix = prefix + "="
    builder = []
    for sec in sections:

        if not in_section:
            if has_exact_prefix(sec, prefix):  # we've reached the desired section
                # print(repr(sec))
                in_section = True
                builder.append(sec)
                continue
            continue
        if sec.startswith(childprefix):  # if it's a child
            # print(repr(sec))
            if recursive:
                builder.append(sec)
            continue
        if has_exact_prefix(sec, prefix):  # we've reached the next header
            yield builder  # yield it
            builder = []  # start building again
            builder.append(sec)
            continue
        # if it's neither a child nor a sibling, therefore it's a parent
        break
    yield builder


def sections_by_lang(sections: List[Wikicode], lang) -> Generator[Wikicode, None, None]:
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

def all_lang_sections(sections: List[Wikicode], recursive=False) -> Generator[Wikicode, None, None]:
    return sections_by_level(sections, 2, recursive)
import grandalf.utils as grutils
import networkx as nx
import matplotlib.pyplot as plt

def draw_graph(G, origin):
    print("...drawing graph...")

    g = grutils.convert_nextworkx_graph_to_grandalf(G)
    from grandalf.layouts import SugiyamaLayout

    class defaultview(object):
        w, h = 10, 10

    for v in g.V(): v.view = defaultview()
    sug = SugiyamaLayout(g.C[0])
    sug.init_all()  # roots=[V[0]]) #, inverted_edges=[V[4].e_to(V[0])])
    sug.draw()
    poses = {v.data: (-v.view.xy[0], -v.view.xy[1]) for v in g.C[0].sV}

    node_colors = nx.get_node_attributes(G, 'color')
    nx.draw(G, pos=poses, with_labels=True, node_color=node_colors.values())
    # x.draw_networkx_edges(G, pos=poses)

    plt.show()



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
    return None
