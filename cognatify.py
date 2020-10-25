from pprint import pprint

from pyetymology.wikt_mod import WiktionaryParser
parser = WiktionaryParser()
parser.include_relation('url')
parser.include_relation('urls')
parser.include_relation('descendants')
word = parser.fetch("llegar", "spanish")

pprint(word[0]["etymology"])
