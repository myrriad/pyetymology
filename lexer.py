from typing import List

from mwparserfromhell.wikicode import Wikicode

import pyetymology.wikt_api as wikt

class Entry:


    def __init__(self, entry: Wikicode, subordinates: List[Wikicode], header_type: str, idx: int = None, entry_type=None):
        self.main_sec = entry
        self.subordinates = subordinates
        self.idx = idx
        self.header_type = header_type
        self.entry_type = header_type if entry_type is None else entry_type

    @property
    def exact_header(self):
        return "===" + self.header_type + ("" if self.idx is None else " " + str(self.idx)) + "==="



class Entries:
    def __init__(self, entries: List[Entry], is_multi_ety=False, did_pos=False, did_ety=False):
        self.entries = entries
        self.is_multi_ety = is_multi_ety
        self.did_pos = did_pos
        self.did_ety = did_ety

def lex(dom: List[Wikicode]) -> Entries:
    sections = wikt.sections_by_level(dom, 3)
    is_multi_ety = None
    entries = []
    did_lemma = False
    for lvl3plus in sections:

        lvl3 = lvl3plus[0]
        if lvl3.startswith("===Etymology"):
            assert did_lemma is False # Etymology should ALWAYS come before lemmas

            if lvl3.startswith("===Etymology==="):
                assert is_multi_ety is None  # There Should be Exactly one ety
                is_multi_ety = False
                assert entries == []
                entry = Entry(lvl3, lvl3plus[1:], header_type="Etymology")
                entries.append(entry)
            else:  #
                assert is_multi_ety is not False
                assert is_multi_ety in [None, True]
                is_multi_ety = True
                breve: str = lvl3[13:] # len("===Etymology ") == 13 # "===Etymology 1===" --> "1==="
                ety_idx = breve[:breve.index("===")] # "1===" -> "1"
                idx = int(ety_idx)
                assert idx and type(idx) == int  # assert that it's an int
                entry = Entry(lvl3, lvl3plus[1:], header_type="Etymology", idx=idx)
                entries.append(entry)
        # TODO: Lemma forms: (POS)
        elif any(lvl3.startswith(x) for x in ["===Verb", "===Noun", "===Adjective"]): # Lemma TODO: add support for more POS
            assert not is_multi_ety # if there's multiple etymologies, then the verbs SHOULD have been put in a nested level
            # ie. ===Etymology 1=== ====Verb====

            breve: str = lvl3[3:]  # len("===") == 3 # "===Verb===" --> "Verb==="
            POS = breve[:breve.index("===")]  # "Verb===" -> "Verb"

            entry = Entry(lvl3, lvl3plus[1:], header_type=POS, entry_type="Lemma POS")
            entries.append(entry)
            did_lemma = True
        else:
            # Something other than an Etymology or a POS
            breve: str = lvl3[3:]  # len("===") == 3 # "===Pronunciation===" --> "Pronunciation==="
            header = breve[:breve.index("===")]  # "Pronunciation===" -> "Pronunciation"
            entry = Entry(lvl3, lvl3plus[1:], header_type=header)
    o_entries = Entries(entries, is_multi_ety=is_multi_ety, did_ety=(is_multi_ety is not None), did_pos=did_lemma)
    return o_entries



