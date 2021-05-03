from pyetymology.eobjects.wikikey import WikiKey


def test_wkey_from_url():
    wkey = WikiKey.from_regurl("https://en.wiktionary.org/wiki/comprar#Spanish")  # TODO implement resolve_multilang