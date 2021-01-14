from bs4 import NavigableString, CData, Tag, BeautifulSoup, Comment



def all_text_linked(elem, strip=False, types=(NavigableString, CData), amount="full"):
    ancestry = amount == "until_period"
    for descendant in elem.descendants:
        # return "a" string representation if we encounter it
        if isinstance(descendant, Tag) and descendant.name == 'a':
            to = descendant['href']
            if 'wikipedia.org' in to:
                to = to[to.index('wikipedia.org/wiki') + 18:]
                to = 'pedia' + to
            child = descendant.string
            yield '<' + child + '|' + str(to) + '>'

        #  inner text node inside each "a"
        if isinstance(descendant, NavigableString) and descendant.parent.name == 'a':
            continue # Ignore for now

        if (
                (types is None and not isinstance(descendant, NavigableString))
                or
                (types is not None and type(descendant) not in types)):
            continue
        if strip:
            descendant = descendant.strip()
            if len(descendant) == 0:
                continue
        if ancestry and '.' in descendant:  # if we're returning only ancestry, then break if we reach a period
            yield descendant[:descendant.index('.')+1]
            return
        yield descendant


def links_only(elem, strip=False, types=(NavigableString, CData), target="full", wikipedia=False):
    ancestry = target == "until_period"
    for descendant in elem.descendants:
        # return "a" string representation if we encounter it
        if isinstance(descendant, Tag) and descendant.name == 'a':
            to = descendant['href']
            if 'wikipedia.org' in to:
                if not wikipedia:
                    continue
                to = to[to.index('wikipedia.org/wiki') + 18:]
                to = 'pedia' + to
            elif '/wiki/' in to:
                to = to[to.index('/wiki/') + 6:]
            elif '&action=edit&redlink=1' in to:
                if to.index('/w/index.php?title=') != 0:
                    raise Exception(to + " is an unexpected redlink")
                to= '?' + to[19:to.index('&action=edit&redlink=1')]
            child = descendant.string
            # yield child + '<' + str(to) + '>'
            yield str(to)

        if ancestry and '.' in descendant:  # if we're returning only ancestry, then break if we reach a period
            return

        #  inner text node inside each "a"
        if isinstance(descendant, NavigableString) and descendant.parent.name == 'a':
            continue # Ignore for now

        if (
                (types is None and not isinstance(descendant, NavigableString))
                or
                (types is not None and type(descendant) not in types)):
            continue
        if strip:
            descendant = descendant.strip()
            if len(descendant) == 0:
                continue







def fetch(query, session):
    if query.startswith('?'):
        raise Exception(query + " starts with a ?. ? is used internally to signify redlinks")
    if query.startswith('Reconstruction:'):
        url = "https://en.wiktionary.org/wiki/" + query + "?printable=yes"
        word = query[query.index('/')+1:]
        lang = query[query.index(':')+1:query.index('/')]
    else:
        tup = query.split('#')
        if len(tup) != 2:
            raise Exception(tup)
        word, lang = tup
        url = "https://en.wiktionary.org/wiki/" + word + "?printable=yes"

    # formatting
    lang = lang.title()  # language capitalized

    response = session.get(url)
    soup = BeautifulSoup(response.text.replace('>\n<', '><'),
                         'html.parser')  # remove newlines between tags (ie. <a></a> /n <div></div>)

    unwanted_classes = ['sister-wikipedia', 'thumb', 'mw-references-wrap', 'cited-source', 'reference']
    for unw in soup.find_all(True, {'class': unwanted_classes}):
        unw.extract()
        # unw.parent.extract()
    comments = soup.find_all(text=lambda text: isinstance(text, Comment))
    for comment in comments:  # remove comments
        comment.extract()

    langnames = soup.find(id=lang).parent  # type: PageElement
    ancestry = progeny = []

    for tag in langnames.next_siblings:
        if tag.name == "h2":  # break if we have reached the next language subsection
            if tag.find("span", {"class": "mw-headline"}):
                break
            else:
                raise Exception("Unexpected h2 tag without a span: " + tag)

        # continue execution here
        if tag.name == 'h3':
            headl = tag.find_next('span', {"class": "mw-headline"})
            if headl and headl['id'].startswith('Etymology'):  # parse etymology
                for sib in tag.next_siblings:  # this should be the ety
                    if sib.name == 'h3':  # break if we have reached the next language subsection
                        if sib.find("span", {"class": "mw-headline"}):
                            break
                        else:
                            raise Exception("Unexpected h3 tag without a span: " + sib)
                    str = ''.join(all_text_linked(sib, amount="until_period"))
                    # ancestry = str.split('.')[0]
                    ancestry = list(links_only(sib, target="until_period"))
                    continue # continue until we reach the next language subsection
        if tag.name == 'h4':
            headl = tag.find_next('span', {"class": "mw-headline"})
            if headl and headl['id'].startswith('Descendants'):  # parse descendants
                for sib in tag.next_siblings:  # this should be the descendants
                    if sib.name == 'h3' or sib.name == 'h4':  # break if we reach a header
                        if sib.find("span", {"class": "mw-headline"}):
                            break
                        else:
                            raise Exception("Unexpected " + sib.name + " tag without a span: " + sib)
                    str = ''.join(all_text_linked(sib, amount="full"))
                    # ancestry = str.split('.')[0]
                    progeny.extend(links_only(sib, target="full"))
                    continue # continue until we break
            if headl and headl['id'].startswith('Derived_terms'):  # parse derived terms
                for sib in tag.next_siblings:  # this should be the descendants
                    if sib.name == 'h3' or sib.name == 'h4':  # break if we reach a header
                        if sib.find("span", {"class": "mw-headline"}):
                            break
                        else:
                            raise Exception("Unexpected " + sib.name + " tag without a span: " + sib)
                    # str = ''.join(all_text_linked(sib, amount="full"))
                    progeny.extend(links_only(sib, target="full"))
                    # print(progeny)
                    continue # continue until we break
                # Ancestry: get all links in first sentence
    #print("ancestry: " + ", ".join(ancestry))
    #print("progeny: " + ", ".join(progeny))
    return ancestry, progeny
