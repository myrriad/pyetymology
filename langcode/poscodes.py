"""
Header codes allowed by Wiktionary
According to https://en.wiktionary.org/wiki/Wiktionary:Entry_layout#Part_of_speech
Includes and encapsulates "POS"

"""
from mwparserfromhell.wikicode import Wikicode

pos = ["Adjective", "Adverb", "Ambiposition", "Article", "Circumposition", "Classifier", "Conjunction", "Contraction",
        "Counter", "Determiner", "Ideophone", "Interjection", "Noun", "Numeral", "Participle", "Particle",
        "Postposition", "Preposition", "Pronoun", "Proper noun", "Verb"]

morphemes = ["Circumfix", "Combining form", "Infix", "Interfix", "Prefix", "Root", "Suffix"]

symbols = ["Diacritical mark", "Letter", "Ligature", "Number", "Punctuation mark", "Syllable", "Symbol"]

phrases = ["Phrase", "Proverb", "Prepositional phrase"]

hanzi = ["Han character", "Hanzi", "Kanji", "Hanja"]

romanization = ["Romanization"]

all = pos + morphemes + symbols + phrases + hanzi + romanization

def is_defn(wc: Wikicode):

    return any(wc.startswith("===" + x) for x in all) or any(wc.startswith("====" + x) for x in all)  #TODO: support lvl5 headers
