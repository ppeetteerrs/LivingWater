from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from backend.database.db_connections.dict.dict_connection_rethink import DictConnection
from backend.database.db_connections.translation.british_to_american import BritishAmericanConnection

stop_words = stopwords.words("english")
RELATED_WORDS_WEIGHT = 0.9
SYNONYMS_WEIGHT = 0.7


class NLP(object):

    def __init__(self):
        pass

    @staticmethod
    # Tokenize => Remove Stopwords => Remove Punctuations => Lowercase
    def clean(sentence: str or list) -> [str]:

        # Tokenize if the sentence is a whole string
        if type(sentence) is str:
            sentence = word_tokenize(sentence)

        # Data Cleaning
        if type(sentence) is list:

            # Change sentence to lowercase and remove stop words and symbols
            sentence = [w.lower() for w in sentence if w.lower()
                        not in stop_words and w.isalpha()]

            filtered_sentence = []

            # Translate to american english if possible
            for base_word in sentence:
                american_base_word = BritishAmericanConnection.british_to_american(base_word)
                # Check if american word is in db
                if DictConnection.word_exists_in_db(american_base_word):
                    filtered_sentence.append(american_base_word)
                # Check if original word is in db
                elif DictConnection.word_exists_in_db(base_word):
                    filtered_sentence.append(base_word)
                # Do not include the base word if both forms are not in db
                else:
                    pass

            return filtered_sentence

        # Type Check
        else:
            print("Cannot clean sentence of type", type(sentence))

    @staticmethod
    def british_to_american(word: str):
        return BritishAmericanConnection.british_to_american(word)
