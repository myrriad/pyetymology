from pyetymology.eobjects.wikikey import WikiKey


def test_wkey_from_url():
    return True # don't stress the servers too badly
    wkey = WikiKey.from_regurl("https://en.wiktionary.org/wiki/comprar#Spanish")  # TODO implement resolve_multilang
    assert wkey.Lang.langname == 'Spanish'
    print('h')