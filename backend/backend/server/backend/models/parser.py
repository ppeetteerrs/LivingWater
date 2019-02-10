from backend.database.db_connections.dict.dict_connection_rethink import DictConnection
from backend.database.db_connections.verses.verses_read import VerseRead
from backend.tools.nlp import NLP
from ..models.models import *

TF_a_zero = 1
TF_a_inf = 0.3  # Curvature Parameter
TF_a_n = 0.5  # Maximum Penalty for low Rarity among Verses
TF_n = 1

# Useless ATM
RPIV_a_zero = 0.95  # Maximum Penalty for low Relative Popularity In Verse
RPIV_a_inf = 1.2  # Curvature Parameter
RPIV_a_n = 1
RPIV_n = 1

RPAV_a_zero = 0.95  # Maximum Penalty for low Relative Popularity Across Verses
RPAV_a_inf = 1.1  # Curvature Parameter
RPAV_a_n = 1
RPAV_n = 1


class Parser:
    timer = DebugTools.timer()

    @classmethod
    def parse_sentence(cls, sentence: str) -> Sentence:
        sentence_object = Sentence(sentence)
        cleaned_sentence: [str] = NLP.clean(sentence)
        base_word_object_list = cls.parse_base_words(cleaned_sentence)
        sentence_object.add_base_words(base_word_object_list)
        return sentence_object

    @classmethod
    def parse_base_words(cls, base_words: []) -> [BaseWord]:
        cls.timer.reset()
        base_word_weight_dict_list = DictConnection.get_word_list_syns_and_related(base_words, add_base_word=True)
        cls.timer.print_duration("Get Synonyms and Related Words", indentation=2)
        base_word_object_array = []
        for index, base_word in enumerate(base_words):
            if base_word in base_word_weight_dict_list:
                sorted_dict = base_word_weight_dict_list[base_word].copy()
                base_word_object_array.append(BaseWord(index, base_word, sorted_dict))
        return base_word_object_array

    @classmethod
    def parse_verse(cls, verse: object, total_verses: int) -> Verse:
        return Verse(verse, total_verses)

    @classmethod
    def parse_verses(cls, verse_records_list=None) -> [Verse]:
        parsed_verses_list = list()
        all_verses = VerseRead.get_verse_record()
        verse_num = len(all_verses)
        if verse_records_list is None:
            verse_records_list = all_verses
        for verse in verse_records_list:
            parsed_verses_list.append(cls.parse_verse(verse, verse_num))
        return parsed_verses_list
