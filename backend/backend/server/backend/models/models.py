from backend.tools import DebugTools
from .. import SETTINGS

PARAMS = SETTINGS["PARAMS"]


class BaseWord:
    def __init__(self, index: int, base_word: str, weight_dict):
        self.index = index
        self.base_word = base_word
        self.weight_dict = weight_dict

    def __str__(self):
        print("Base Word", self.index, ":", self.base_word)
        return ""


class Sentence:
    def __init__(self, sentence: str):
        self.sentence = sentence
        self.base_words: [BaseWord] = []

    def __str__(self):
        print("Sentence:", self.sentence)
        for base_word in self.base_words:
            print(base_word)
        return ""

    def add_base_words(self, base_word_list: [BaseWord]):
        self.base_words.extend(base_word_list)


class Keyword:
    def __init__(self, verse, keyword_record, level, votes, total_verses):
        self.verse = verse
        self.word = keyword_record.word
        self.term_frequency = DebugTools.tools.calc_exp(keyword_record.appearance / total_verses, PARAMS["TF_a_zero"],
                                                        PARAMS["TF_a_inf"],
                                                        PARAMS["TF_a_n"], PARAMS["TF_n"])
        self.relative_popularity_in_verse = DebugTools.tools.calc_exp(
            votes / verse.max_vote,
            PARAMS["RPIV_a_zero"], PARAMS["RPIV_a_inf"], PARAMS["RPIV_a_n"],
            PARAMS["RPIV_n"])
        self.relative_popularity_across_verses = DebugTools.tools.calc_exp(
            votes / keyword_record.total_votes,
            PARAMS["RPAV_a_zero"], PARAMS["RPAV_a_inf"], PARAMS["RPAV_a_n"],
            PARAMS["RPAV_n"])
        self.weight = SETTINGS["ADMIN_WEIGHTS_RATIO"][level - 1]
        self.prelim_score = self.relative_popularity_across_verses * self.relative_popularity_in_verse * self.weight
        self.votes = float(votes + 1)

    def __str__(self):
        print(
            "Keyword: " + self.word + "\nTerm Frequency: %.2f \nPopularity in Verse: %.2f \nPopularity across Verses: %.2f \nWeight: %.2f \nVotes: %.2f" % (
                self.term_frequency, self.relative_popularity_in_verse, self.relative_popularity_across_verses,
                self.weight,
                self.votes))
        return ""


class Verse:
    def __init__(self, verse_object, total_verses: int):
        self.verse_object = verse_object
        self.location = self.verse_object.location
        self.book = self.verse_object.book
        self.start_chapter = self.verse_object.start_chapter
        self.start_verse = self.verse_object.start_verse
        self.end_chapter = self.verse_object.end_chapter
        self.end_verse = self.verse_object.end_verse
        self.keywords = [keyword_link.keyword.word for keyword_link in self.verse_object.keyword_links]
        self.score = 0
        self.score_breakdown = None
        self.sorted_score_breakdown = None
        self.max_vote = verse_object.max_vote
        self.keyword_objects = [
            Keyword(self, keyword_link.keyword, keyword_link.level, keyword_link.votes, total_verses) for keyword_link
            in
            self.verse_object.keyword_links]


class ScoreBreakdown:
    def __init__(self, verse: Verse, sentence: Sentence):
        self.verse = verse
        self.sentence = sentence
        self.scores_list = []


class BaseWordScore:
    def __init__(self, base_word: BaseWord, verse: Verse):
        self.verse = verse
        self.base_word = base_word
        self.index = base_word.index
        self.scores = []
        self.max_score = 0
        self.max_score_word = None


class WordScore:
    def __init__(self, word: str, decay: float, verse: Verse, base_word: BaseWord):
        self.base_word = base_word
        self.verse = verse
        self.word = word
        self.synonym_decay = decay
        self.matched_keyword = None
        self.score = 0
        self.breakdown = None
