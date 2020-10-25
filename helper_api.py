from typing import List, Generator, Dict

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

from pyetymology.langcode import langcodes


def has_exact_prefix(str, prefix):
    return str.startswith(prefix) and not str.startswith(prefix + "=")


"""
Takes in parameter l, which corresponds to a "main" heading level.
Yields each "main" header of that specified heading level.
If there is a subheader, it will be packaged after the specified main header that precedes it


"""


def get_by_level(sections: List[Wikicode], level: int) -> Generator[List[Wikicode], None, None]:
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


def get_by_lang(sections: List[Wikicode], lang) -> Generator[Wikicode, None, None]:
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

def ety_relation(template: mwparserfromhell.wikicode.Template):
    etyr = EtyRelation(template)
    if(etyr):
        return etyr
    return None

def is_in(elem, abbr_set: Dict[str, str]):
    return elem in abbr_set.keys() or elem in abbr_set.values()

class EtyRelation:
    ety_abbrs = {"derived": "der",
                 "inherited": "inh",
                 "borrowed": "bor",
                 "orthographic borrowing": "obor",
                 "learned borrowing": "lbor",
                 "calque": "cal",
                 "semantic loan": "sl",
                 }
    cog_abbrs = {"cognate": "cog",
                 "noncognate": "ncog",
                 "noncog": "ncog",
                 "nc": "ncog",
                 "doublet": "doublet",
                 "piecewise doublet": "piecewise doublet"
                 }
    sim_abbrs = {"mention": "m"}

    aff_abbrs = {"affix": "af",
                 "prefix": "pre",
                 "confix": "con",
                 "suffix": "suf",
                 "compound": "com"}

    def __init__(self, template: mwparserfromhell.wikicode.Template):
        rtype = str(template.name)
        params = template.params
        lang = word = _selflang = None


        ety_abbrs = EtyRelation.ety_abbrs
        cog_abbrs = EtyRelation.cog_abbrs
        aff_abbrs = EtyRelation.aff_abbrs
        sim_abbrs = EtyRelation.sim_abbrs
        if rtype in ety_abbrs:  # use the abbreviations
            rtype = ety_abbrs[rtype]
        if rtype in cog_abbrs:  # use the abbreviations
            rtype = cog_abbrs[rtype]
        if rtype in aff_abbrs:
            rtype = aff_abbrs[rtype]
        if rtype in sim_abbrs:
            rtype = sim_abbrs[rtype]


        self.null = False
        if rtype in ety_abbrs.values():  # if it's an etymological relation
            _selflang = str(params[0])
            lang = str(params[1])
            word = str(params[2])
        elif rtype in cog_abbrs.values():  # if it's a cognate relation
            lang = str(params[0])
            word = str(params[1])
        elif rtype in aff_abbrs.values(): # affix, prefix, suffix, etc.
            lang = str(params[0])
            word = str(params[1])
        elif rtype in sim_abbrs.values(): # mention
            lang = str(params[0])
            word = str(params[1])
        else:
            self.null = True # if it's none that are recognized, mark self as null

        self.params = params
        self.rtype = rtype
        self.lang = lang
        self.langname = langcodes.name(lang, use_ety=True, use_fam=True)
        if lang and not self.langname:
            print(f"{lang} is None")
        self._selflang = _selflang
        self._selflangname = langcodes.name(_selflang)
        self.word = word

    def __str__(self):
        if(not self):
            return "{{" + self.rtype + " null " + repr(self.params) + "}}"
        assert self.word is not None
        assert self.langname is not None
        paramsc = repr(self.params[3:]) # slice off the first 3 args
        paramsc = "" if paramsc == "[]" else " "+ paramsc # convert []s to ""

        return "{" + self.rtype + "|" + self.langname + "|" + self.word + paramsc + "}"
    def __repr__(self):
        return str(self)
    def __bool__(self):
        return not self.null