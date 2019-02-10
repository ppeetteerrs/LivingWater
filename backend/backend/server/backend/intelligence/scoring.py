import numpy as np

from backend.tools import DebugTools
from ..models.models import Verse, ScoreBreakdown, Sentence
from ...backend import SETTINGS


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# Score = word_decay * admin_score * normalized user vote * popularity score * connected bonus * (tfidf)

class Scoring:
    Max_Popularity_Bonus = 2
    Connection_Multiplier = 1.5
    Admin_Vote_Weight = 100
    Connection_Bonus = 0.3
    Repeated_Match_Penalty = 0.7

    @classmethod
    def get_score(cls, all_verses: [Verse], sentence_object: Sentence) -> [ScoreBreakdown]:
        # Create an empty dict to store score breakdown for all verses
        verses_scores = {}

        # Iterate over each verse
        for verse_object in all_verses:
            # Create a score breakdown for the verse
            base_word_breakdowns: {} = cls.get_verse_score_breakdown(verse_object, sentence_object)

            # Calculate total score for the verse
            total_score = cls.calc_total_score(base_word_breakdowns)
            verses_scores[verse_object.location] = {"verse_location": verse_object.location,
                                                    "verse_object": verse_object,
                                                    "score": total_score,
                                                    "base_word_breakdowns": base_word_breakdowns}

        sorted_verse_scores = DebugTools.tools.sort_by_secondary_key(verses_scores, secondary_key="score")

        return sorted_verse_scores

    @classmethod
    def get_verse_score_breakdown(cls, verse_object: Verse, sentence_object: Sentence):
        # Create an empty dict to store score breakdown for all base words
        base_word_scores = {}

        # To store a mapping between matched keywords and the highest scoring base_word match
        # key: verse_keyword, val: score, base_word, breakdown
        all_matched_keywords_pairing = {}

        # Iterate over each base word to populate all_matched_keywords_pairing
        for index, base_word_object in enumerate(sentence_object.base_words):

            # Create empty object in base_word_scores
            base_word_scores[base_word_object.base_word] = {"keyword": None, "breakdown": None, "score": 0,
                                                            "best_word": None}

            # [key (0): verse_keyword, item(1): score, breakdown]: sorted by score
            sorted_keyword_score_list = cls.get_base_word_score_breakdown(verse_object, base_word_object.weight_dict)

            if len(sorted_keyword_score_list) > 0:
                # Continue if the base_word matched any keywords

                for verse_keyword, keyword_score_item in sorted_keyword_score_list:

                    # Check if verse_keyword has already been matched by another base word
                    if verse_keyword in all_matched_keywords_pairing:
                        # If already matched, take the higher score
                        if keyword_score_item["score"] > all_matched_keywords_pairing[verse_keyword]["score"]:
                            all_matched_keywords_pairing[verse_keyword]["base_word"] = base_word_object.base_word
                            all_matched_keywords_pairing[verse_keyword]["breakdown"] = keyword_score_item["breakdown"]
                            all_matched_keywords_pairing[verse_keyword]["score"] = keyword_score_item["score"]
                        else:
                            pass

                    else:
                        # If not matched already, just add to the mapping
                        all_matched_keywords_pairing[verse_keyword] = {}
                        all_matched_keywords_pairing[verse_keyword]["base_word"] = base_word_object.base_word
                        all_matched_keywords_pairing[verse_keyword]["breakdown"] = keyword_score_item["breakdown"]
                        all_matched_keywords_pairing[verse_keyword]["score"] = keyword_score_item["score"]

        sorted_matched_keywords_pairing = DebugTools.tools.sort_by_secondary_key(all_matched_keywords_pairing,
                                                                                 secondary_key="score")

        # Extract highest scored match for each base word
        for matched_keywords_pairing_item in sorted_matched_keywords_pairing:
            item_verse_keyword = matched_keywords_pairing_item[0]
            item_score = matched_keywords_pairing_item[1]["score"]
            item_base_word = matched_keywords_pairing_item[1]["base_word"]
            item_breakdown = matched_keywords_pairing_item[1]["breakdown"]

            if item_base_word in base_word_scores and base_word_scores[item_base_word]["score"] <= 0:
                base_word_scores[item_base_word] = {"keyword": item_verse_keyword, "score": item_score,
                                                    "breakdown": item_breakdown, "best_word": item_verse_keyword}

        return base_word_scores

    @classmethod
    def get_base_word_score_breakdown(cls, verse_object: Verse, base_word_weight_dict):
        # Create an empty dict to store score breakdown for all keywords
        keyword_scores = {}

        # Iterate over each keyword
        for keyword_object in verse_object.keyword_objects:
            word = keyword_object.word
            if word in base_word_weight_dict:
                # If there is a match
                breakdown = cls.calc_word_score(base_word_weight_dict[word], keyword_object.term_frequency,
                                                keyword_object.relative_popularity_in_verse,
                                                keyword_object.relative_popularity_across_verses, keyword_object.weight)
                keyword_scores[word] = {"score": breakdown["score"], "breakdown": breakdown}
        return DebugTools.tools.sort_by_secondary_key(keyword_scores, secondary_key="score")

    @classmethod
    def calc_total_score(cls, base_word_score_dict):
        matched_count = 0
        total_count = 0

        for k, v in base_word_score_dict.items():
            if v["score"] > 0:
                matched_count += 1
            total_count += 1

        total_multiplier = 1
        total_base_score = 0

        for item_base_word, val in base_word_score_dict.items():
            best_score = val["score"]
            total_multiplier *= 1 + cls.Connection_Bonus * best_score
            total_base_score += best_score
        # Calculate matching penalty
        matched_fraction = 0
        if total_count > 0:
            matched_fraction = matched_count / total_count
        total_multiplier *= DebugTools.tools.calc_exp(matched_fraction,
                                                      SETTINGS["PARAMS"]["MB_a_zero"],
                                                      SETTINGS["PARAMS"]["MB_a_inf"], SETTINGS["PARAMS"]["MB_a_n"],
                                                      SETTINGS["PARAMS"]["MB_n"])
        return total_base_score * total_multiplier

    @staticmethod
    def calc_word_score(syn_word_info, tf, rpiv, rpav, weight):
        breakdown = {
            "score": syn_word_info["weight"] * tf * rpiv * rpav * weight,
            "decay": syn_word_info["weight"],
            "term frequency": tf,
            "relative popularity in verse": rpiv,
            "relative popularity across verse": rpav,
            "weight": weight,
            "db_id": syn_word_info["id"],
            "parent": syn_word_info["parent"]
        }
        return breakdown
