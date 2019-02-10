from threading import Thread, Lock

import requests
from bs4 import BeautifulSoup as bs

from .middleman import MiddleMan
from ..dictionary.dictionary_parser import get_related_words
from ..thesaurus.thesaurus_parser import get_syns
from ..tools.tools import clean


class Crawler(Thread):
    word_queue = set()
    queue_length = 0
    db_lock = Lock()
    word_list_lock = Lock()
    crawled_count = 0

    def __init__(self, _id, verbose=True):
        self._id = _id
        self.verbose = verbose
        Thread.__init__(self)

    def run(self):
        while len(self.word_queue) > 0:

            # Pop and Clean The First Word From List of Words to Crawl
            first_word = clean(self._get_first_word())

            # Crawl Word
            if first_word is not None:
                self.crawl_word(first_word)

            print("Crawler", self._id, ":", self.__class__.crawled_count, "/", self.queue_length, "crawled")
        if self.verbose:
            print("Crawler", self._id, "is done")

    def crawl_word(self, word):

        # Full List of Root Words
        root_words = {word} | self._get_related_words(self._get_dictionary_soup(word), word)
        if self.verbose:
            print("\nCrawler", self._id, "is crawling word", word)
            print("    Root Words Level 1:", root_words)

        words_set, relation_pairs = self.get_relation_pairs(root_words)
        words_set, synonym_list = self.get_synonyms(words_set)

        # print("Word", word, "has", len(relation_pairs), "relation pairs and", len(synonym_list), "synonyms")

        self.db_lock.acquire()
        MiddleMan.update(self._id, words_set, relation_pairs, synonym_list)
        self.__class__.crawled_count += 1
        self.db_lock.release()

    def get_relation_pairs(self, root_words):
        related_words_dict = {}
        relation_pairs = list()
        words_set = root_words.copy()

        for root_word in root_words:

            # Crawl all words that need to be crawled
            if root_word not in related_words_dict:
                related_words_dict[root_word] = self._get_related_words(self._get_dictionary_soup(root_word), root_word)
            for crawled_word in related_words_dict[root_word]:
                if crawled_word not in related_words_dict:
                    related_words_dict[crawled_word] = self._get_related_words(self._get_dictionary_soup(crawled_word),
                                                                               crawled_word)

            # Find Relation Pairs
            for crawled_word in related_words_dict[root_word]:
                if root_word in related_words_dict[crawled_word] and root_word != crawled_word:
                    relation_pairs.append((root_word, crawled_word))
                    words_set.add(crawled_word)

            cleaned_relation_pairs = list()
            for word1, word2 in relation_pairs:
                if (word1, word2) not in cleaned_relation_pairs and (word2, word1) not in cleaned_relation_pairs:
                    cleaned_relation_pairs.append((word1, word2))

        return words_set, cleaned_relation_pairs

    def get_synonyms(self, related_words_set):

        synonym_list = []
        synonym_id_set = set()
        words_set = related_words_set.copy()

        for word in related_words_set:

            synonym_tuples = self._get_syns(self._get_thesaurus_soup(word))

            if self.verbose:
                print("        ", word, "has", len(synonym_tuples), "synonyms")

            if len(synonym_tuples) > 0:
                for synonym, relevance in synonym_tuples:
                    words_set.add(synonym)
                    # Append the synonym link

                    if (word, synonym) not in synonym_id_set:
                        synonym_list.append((word, synonym, relevance))
                        synonym_id_set.add((word, synonym))

        return words_set, synonym_list

    @classmethod
    def setup(cls, word_set):
        cls.word_queue = set([word for word in word_set if len(word) > 2 and word is not None])
        cls.queue_length = len(cls.word_queue)
        cls.crawled_count = 0

    @classmethod
    def _get_first_word(cls):
        cls.word_list_lock.acquire()
        dummy = cls.word_queue.pop()
        cls.word_list_lock.release()
        return dummy

    @staticmethod
    def _get_dictionary_soup(word):
        dictionary_url = "http://dictionary.com/browse/"
        dictionary_html = requests.get(dictionary_url + word)
        if dictionary_html.status_code == 404:
            dictionary_soup = None
            # print("Dictionary.com has no page for word", word)
        else:
            dictionary_soup = bs(dictionary_html.content)
        return dictionary_soup

    @staticmethod
    def _get_thesaurus_soup(word):
        thesaurus_url = "http://thesaurus.com/browse/"
        thesaurus_html = requests.get(thesaurus_url + word)
        if thesaurus_html.status_code == 404:
            thesaurus_soup = None
            # print("Thesaurus.com has no page for word", word)
        else:
            thesaurus_soup = bs(thesaurus_html.content)
        return thesaurus_soup

    @staticmethod
    def _get_syns(soup):
        synonyms = get_syns(soup)
        return synonyms

    @staticmethod
    def _get_related_words(soup, word):
        related_words = get_related_words(soup, word)
        return related_words
