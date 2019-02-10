import warnings

from scripts.database.database import Connection

warnings.filterwarnings('ignore')
Connection.setup()
print(Connection.get_all_words())
i = 0
while (i < 10):
    word = input()
    related_words = Connection.get_related_words(word)
    synonyms, bases = Connection.get_synonyms(word, show_bases=True)
    print(word, ":")
    print("\nRelated Words:")
    print("    ", related_words)
    print("\nSynonyms:")
    print("    ", synonyms)
    print("\nBases:")
    print("    ", bases)
# Crawler.setup([])
# crawler = Crawler(0)
# word = input()
# root_words = {word} | crawler._get_related_words(crawler._get_dictionary_soup(word), word)
# words_set, relation_pairs = crawler.get_relation_pairs(root_words)
# words_set, synonym_list = crawler.get_synonyms(words_set)
#
# print(synonym_list)
