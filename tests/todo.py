# TODO: Diacritic strip out. See plicō. See
"""
https://en.wiktionary.org/wiki/Template:present_participle_of
|2= (required)
The term to link to (which this page is the present participle of).
This should include diacritics as appropriate to the language (e.g. accents in Russian to mark the stress, vowel diacritics in Arabic, macrons in Latin to indicate vowel length, etc.).
These diacritics will automatically be stripped out in a language-specific fashion in order to create the link to the page.
"""

# TODO: https://en.wiktionary.org/wiki/Wiktionary:Entry_layout#:~:text=Parts%20of%20speech
# TODO: wicked, learned, vino#Spanish etc.: When a lemma form AND an etymology exists, but they're for different definitions
# TODO: display convenience definitions.
    # if the etymology is a multi-ety,  then the definitions will simply be the etymology x's subordinates
    # if the etymology is a single-ety, then its subordinates will be blank, but we know that there is only one total "definition"
    # so we should expect the definitions to simply be the siblings of the etymology entry
    # if single-ety, o_entries should be composed of only [etymology, definition1, definition2, ...]
# TODO: display not-ancestral etymology, ie. cognates
# DID: currently, each wikicode prints recursively and so there's a lot of redundance (fixed with redundance=False default for query())

# TODO: Deprecated testing https://en.wiktionary.org/wiki/Category:Pages_using_deprecated_templates

# DID: llevaron: {{es-verb form of|person=third-person|number=plural|tense=preterit|mood=indicative|ending=ar|llevar}}

# TODO: Verb 2, Noun 2, etc. According to the Entry Layout, this is actually disallowed:
"""
Some POS headers are explicitly disallowed:

...
“(POS) (number)”: Noun 1, Noun 2, etc.
"""
# TODO: Except there are exceptions: see POS_2.txt

# TODO: Template back-formation https://en.wiktionary.org/wiki/Template:back-formation
# TODO: Template portmanteau, blend, coined

# TODO: Entry layout manual: https://en.wiktionary.org/wiki/Wiktionary:Entry_layout
# TODO: Etymology manual: https://en.wiktionary.org/wiki/Wiktionary:Etymology


"""
Etymology jargon
Some words have conventional usage in etymology:

from
Using a bare “from” denotes a single step, with no intermediate steps – a direct descendant or borrowing – as in: “From French, from Latin, from Proto-Italic, from Proto-Indo-European”
ultimately from
Using “ultimately from” indicates that some intermediate steps have been elided, as in “Ultimately from Proto-Indo-European” (but by some other languages in between).
akin / related
The term “akin” is used to indicate an attested word that is presumed to be etymologically related, when the ultimate etymon is not attested. This is used particularly for proto-languages, for language groups, and for unattested terms in attested languages.
For example, in tracing an English word back to Proto-Indo-European (which is not attested), presumed cognates of the Old English word can be referred to as “from Old English X, akin to Old High German Y, Latin Z, etc.”
Similarly, if a word can be traced back to an indeterminate Germanic language, one can give examples of related attested words, but not state a specific etymon (because unknown), writing for instance “of Germanic origin; akin to Old Saxon X” (but might be from Old Frisian or another language).
“Akin” can also be used when the specific etymon is not attested in an otherwise attested language, for example: “connive: ultimately from Latin com- (“together”) + base akin to nictō (“I wink”)” (but *nivō is not attested).
"Akin" is a weaker claim than "cognate to". The former only implies relationship in some, possibly so far undetermined fashion, while the latter is commonly understood to imply descent from a common ancestor.
"""

# TODO: Inh
"""
A significant category of words in a language are the so-called ‘native’ or ‘inherited’ words; 
in some languages, but not all, they form the majority of words.
 This means that they have developed from an earlier form of the language which may or may not have gone by the same name. 
 Some of these ancestor-languages were written down and are well-attested, but others are not. 
 For example, French, Spanish, Italian, Romanian and Portuguese all developed from Latin. 
 The French word clef, for instance, and the Spanish word llave both evolved from the Latin word clāvis (“key”) (they are cognates). 
They were not borrowed from Latin; the Latin language evolved naturally in different areas into the different forms.
"""

# TODO: Handling Etymology 1s is a pain, because it changes the nesting:
"""
Note that in the case of multiple etymologies, 
all subordinate headers need to have their levels increased by 1 in order 
to comply with the fundamental concept of showing dependence through nesting.
"""


# TODO: origin indexing is broken with lemmas

# TODO: Homograph testing https://www.thoughtco.com/some-spanish-homophones-3080303

# TODO: example of if there are 2 different Noun definitions: https://en.wiktionary.org/wiki/flamenco#Spanish

# LEMMA https://en.wiktionary.org/wiki/Category:Form-of_templates
# https://en.wiktionary.org/wiki/Module:form_of/data
# Wiktionary templates: https://en.wiktionary.org/wiki/Category:Template_interface_modules
# all templates: https://en.wiktionary.org/wiki/Special:AllPages?from=&to=&namespace=10
# ^^ Note: Capitals are displayed before lowercase
# Note: spaces are replaced with underlines in urls

# TODO: remove duplicate templates if they're the same
# Partially done: fixed bug

# TODO: proper querying for reconstructed languages

# DID: llevar#Spanish contains entry levō, but querying levō fails. TODO: Test this
# DID: proper querying and connecting with Latin macrons; ie. plicō, which must be queried by "plico" TODO: Test this
# See: https://en.wiktionary.org/wiki/Wiktionary:About_Latin#Do_not_use_diacritical_marks_in_page_names

# DID: test_.fetch_query() and wikt_api.query() have different footprints3333
# DID: fetch_query() doesn't return the last 2 values of query()

# TODO: query() is totally untested, because it is emulated by fetch_query(

# TODO: for origins, show their old AND new o_id

# TODO: Offline mode using a dump at https://dumps.wikimedia.org/enwiktionary/

# TODO: test auto_lang. For example test "llegar"

# TODO: better lemma testing: for example ine-form's