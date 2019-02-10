from ..tools.tools import clean


def _find_word_links_in_def(soup, base_word):
    words_list = set()
    list1 = soup.find_all(" div", {"class": "def-content"})
    for item1 in list1:
        list2 = item1.find_all("a", {"class": "dbox-xref"})
        for item2 in list2:
            word = clean(str(item2.contents[0]))
            if _check_validity(word, base_word):
                words_list.add(word)
    return words_list


def _find_related_forms(soup, base_word):
    words_list = set()
    list1 = soup.find_all("div", {"class": "tail-type-relf"})
    for item1 in list1:
        list2 = item1.find_all("span", {"class": "dbox-bold"})
        for item2 in list2:
            word = clean(str(item2.contents[0]))
            if _check_validity(word, base_word):
                words_list.add(word)
    return words_list


def _find_word_forms(soup, base_word):
    words_list = set()
    list1 = soup.find_all("header", {"class": "luna-data-header"})
    for item1 in list1:
        list2 = item1.find_all("span", {"class": "dbox-bold"})
        for item2 in list2:
            word = clean(str(item2.contents[0]))
            if _check_validity(word, base_word):
                words_list.add(word)
    return words_list


def _find_related_words(soup, base_word):
    words_list = set()
    list1 = soup.find_all("section", {"class": "related-words-box"})
    for item1 in list1:
        list2 = item1.find_all("a")
        for item2 in list2:
            word = clean(str(item2.contents[0]))
            if _check_validity(word, base_word):
                words_list.add(word)
    return words_list


def _find_origin_words(soup, base_word):
    words_list = set()
    list1 = soup.find_all("div", {"class": "tail-elements"})
    for item1 in list1:
        list2 = item1.find_all("a", {"class": "dbox-xref"})
        for item2 in list2:
            word = clean(str(item2.contents[0]))
            if _check_validity(word, base_word):
                words_list.add(word)
    return words_list


def _check_validity(related, base):
    if related is None or base is None:
        return False

    else:
        short_match_one = len(related) <= 5 and related.startswith(base[:1])
        long_match_two = len(related) > 5 and related.startswith(base[:2])
        one_word = len(related.split(" ")) == 1
        return (short_match_one or long_match_two) and one_word


def get_related_words(soup, base_word):
    if soup is None:
        return set()
    all_relations = {base_word}
    definition_words = _find_word_links_in_def(soup, base_word)
    # print("Definition Words:", definition_words)
    related_forms = _find_related_forms(soup, base_word)
    # print("Related Forms:", related_forms)
    word_forms = _find_word_forms(soup, base_word)
    # print("Word Forms:", word_forms)
    related_words = _find_related_words(soup, base_word)
    # print("Related Words:", related_words)
    origin_words = _find_origin_words(soup, base_word)
    # print("Origin Words:", origin_words)
    all_relations |= definition_words | related_forms | word_forms | related_words | origin_words
    # print("All:", all_relations)
    return all_relations
