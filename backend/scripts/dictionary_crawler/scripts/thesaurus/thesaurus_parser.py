import json

from ..tools.tools import clean


def get_syns(soup, multi_word=False):
    if soup is None:
        return list()

    # Extract Synonym Components from HTML
    syn_lists = [syn_div.find_all("div", {"class": "relevancy-list"})[0] for syn_div in
                 soup.find_all("div", {"class": "synonyms"})]
    synonyms = list()
    for syn_list in syn_lists:
        syn_items = syn_list.find_all("li")
        for item in syn_items:

            # Extract Text and Relevance from component
            text = clean(item.find_all("span", {"class": "text"})[0].text)

            if text is not None:

                rel = int(json.loads(item.find_all("a")[0].get("data-category"))["name"].split("-")[1]) / 3

                # Check if synonym has more than one word
                if (multi_word or len(text.split(" ")) == 1) and rel is not None:
                    synonyms.append((text, rel))
                if rel is None:
                    print(text, "has no relevance")

            else:
                break

    # Add words in title bar
    title_words = _get_thesaurus_titles(soup)
    if len(title_words) > 0:
        synonyms.extend([(title_word, 1) for title_word in title_words])
    else:
        pass
        # print("No Synonym Titles")

    # Sort by relevance
    synonyms.sort(key=lambda x: x[1], reverse=True)
    return synonyms


def _get_thesaurus_titles(soup):
    words_list = set()
    list1 = soup.find("div", {"class": "mask"}).find_all("a", {"class": "pos-tab"})
    # print(len(list1))
    for item1 in list1:
        list2 = item1.find_all("strong", {"class": "ttl"})
        for item2 in list2:
            titles = item2.contents[0].split(",")
            for title_item in titles:
                if len(title_item.strip().split(" ")) == 1:
                    title = clean(title_item)
                    if title is not None:
                        words_list.add(title)
    return words_list
