import string
from typing import Tuple, List, Generator

import mwparserfromhell as mwp
from mwparserfromhell.wikicode import Wikicode

from pyetymology.eobjects import fixins
from pyetymology.etyobjects import MissingException


def wikitextparse(wikitext: str, redundance=False) -> Tuple[Wikicode, List[Wikicode]]:
    res = mwp.parse(wikitext)  # type: Wikicode
    # res = wtp.parse(wikitext)
    dom = res.get_sections(flat=not redundance)
    return res, dom


def reduce_to_one_lang(dom: List[Wikicode], use_lang: str=None, permit_abbrevs=True, use_input=True) -> Tuple[List[Wikicode], str, str, str]:
    """
    Returns sections of only 1 lang
    """
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
            elif use_input:  # if it's possible to read input from the console

                usrin = fixins.input("Choose a lang from these options: " + str(lang_options))
            else:  # if such is not possible
                raise MissingException(f"Could not auto-infer language from the languages {str(lang_options)}.", missing_thing="language_specification")
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
    assert lang
    return lang_secs, lang


def all_lang_sections(sections: List[Wikicode], recursive=False, flat=True) -> Generator[Wikicode, None, None]:
    return sections_by_level(sections, 2, recursive=recursive, flat=flat)


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


def has_exact_prefix(str, prefix):
    return str.startswith(prefix) and not str.startswith(prefix + "=")