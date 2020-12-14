from pyetymology.module import moduleimpl


def test_macron():
    link = moduleimpl.to_link("plicō", "Latin")
    assert link == "https://en.wiktionary.com/w/api.php?action=parse&page=" + "plico" + "&prop=wikitext&formatversion=2&format=json"

