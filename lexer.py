from typing import List, Union

from mwparserfromhell.wikicode import Wikicode

import pyetymology.eobjects.mwparserhelper
from pyetymology import wikt_api as wikt
from pyetymology.langcode import poscodes


def get_header_type(wc: Wikicode, lvl: int):
    breve: str = wc[lvl:]  # len("===") == 3 # "===Pronunciation===" --> "Pronunciation==="
    header_type = breve[:breve.index("=" * lvl)]  # "Pronunciation===" -> "Pronunciation"
    return header_type


class Header:

    def __init__(self, wikicode: Wikicode, subordinates: List[Wikicode], header_type: str = None, idx: int = None,
                 metainfo=None, lvl: int = 3):
        assert wikicode.startswith("="*lvl) and not wikicode.startswith("="*(lvl+1))  # assert that the level is correct
        if header_type is None:  # auto header type deduce
            breve: str = wikicode[lvl:]  # len("===") == 3 # "===Pronunciation===" --> "Pronunciation==="
            header_type = breve[:breve.index("="*lvl)]  # "Pronunciation===" -> "Pronunciation"

            if idx is None and header_type.startswith("Etymology "):  # auto idx deduce
                assert len(header_type) >= 11  # len("Etymology 1")
                idx = int(header_type[10:])
                assert idx and type(idx) == int
                header_type = "Etymology"
            defn_flag = header_type in poscodes.all
            if defn_flag and metainfo is None:
                metainfo = "Definition"


        self.wikicode = wikicode
        self.subordinates = subordinates
        self.idx = idx
        self.header_type = header_type
        self.metainfo = header_type if metainfo is None else metainfo  # TODO: make it into an enum
        self.lvl = lvl


    @property
    def exact_header(self):
        return "=" * self.lvl + self.header_type + ("" if self.idx is None else " " + str(self.idx)) + "=" * self.lvl

    def __str__(self):
        return str(self.wikicode)

class Entry:

    def __init__(self, ety: Header, extras: List[Header], desc: List[Header]):
        assert ety or extras or desc # can't all be blank
        assert ety is None or isinstance(ety, Header)
        self.ety = ety  # type: Header
        self.extras = extras  # type: List[Header]
        self.desc = desc
def lex(dom: List[Wikicode]) -> List[Entry]:
    is_multi_ety = None

    ety = None  # type: Header
    nonetys = []  # type: List[Header]
    entries = []  # type: List[Entry]
    preety = []
    desc = []  # type: List[Header]
    did_lemma = False
    for lvl3plus in pyetymology.eobjects.mwparserhelper.sections_by_level(dom, 3):

        lvl3 = lvl3plus[0]
        if lvl3.startswith("===Etymology"):
            assert did_lemma is False  # Etymology should ALWAYS come before lemmas

            if lvl3.startswith("===Etymology==="):
                assert is_multi_ety is None  # There Should be Exactly one ety
                is_multi_ety = False
                assert not ety  # There should be exactly one ety
                ety = Header(lvl3, lvl3plus[1:])
                lvl4s = pyetymology.eobjects.mwparserhelper.sections_by_level(lvl3plus[1:], 4)
                for lvl4plus in lvl4s:
                    lvl4 = lvl4plus[0]
                    h = Header(lvl4, lvl4plus[1:], lvl=4)
                    nonetys.append(h)
            else:  # multiple etys
                assert is_multi_ety is not False
                assert is_multi_ety in [None, True]
                is_multi_ety = True

                # package the previous
                if ety or nonetys:
                    entry = Entry(ety, nonetys, desc)
                    entries.append(entry)

                ety = Header(lvl3, lvl3plus[1:])
                nonetys = []
                desc = []
        elif lvl3.startswith("===Root"):
            # Reconstructed langs
            # TODO: Do the Descendants tab in for nonReconstructed langs
            lvl4s = pyetymology.eobjects.mwparserhelper.sections_by_level(lvl3plus[1:], 4)
            for lvl4plus in lvl4s:
                lvl4 = lvl4plus[0]
                h = Header(lvl4, lvl4plus[1:], lvl=4)
                desc.append(h)
            pass
        else:
            # Something other than an Etymology: is it a POS?

            h = Header(lvl3, lvl3plus[1:])
            if poscodes.is_defn(lvl3):
                assert not is_multi_ety  # if there's multiple etymologies, then the verbs SHOULD have been put in a nested level
                assert "Definition" in h.metainfo
                did_lemma = True
            if is_multi_ety is None:
                # uhhh
                # ie. could be Pronunciation, which precedes Etymology
                # this is a difficult situation, because we don't know whether it is multi_ety or not
                # we only want to package it Only if it's single ety or zero ety, but NOT multi_ety
                # But by passing here,
                # We omit everything that occurs before the Etymology
                preety.append(h)
            elif is_multi_ety is False:
                nonetys.append(h)
    if is_multi_ety is None or is_multi_ety is False:
        assert entries == []
        nonetys = preety + nonetys


    # package remnants
    if ety or nonetys or desc:
        entry = Entry(ety, nonetys, desc)
        entries.append(entry)
    # o_entries = Entries(headers, is_multi_ety=is_multi_ety, did_ety=(is_multi_ety is not None), did_pos=did_lemma)
    return entries
