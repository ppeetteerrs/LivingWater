from backend.database.db_connections.bible.bible_connection_rethink import BibleQueryConnection
from backend.tools import DebugTools
from .scoring import Scoring
from .. import SETTINGS
from ..models.parser import Parser


class Calculations(object):
    Admin_Weights = SETTINGS["ADMIN_WEIGHTS_RATIO"]
    current_time = 0
    timer = DebugTools.timer()

    @classmethod
    def get_rankings(cls, sentence: str, no_of_verses: int = 30):

        cls.timer.reset()

        DebugTools.logging.print_debug("Received sentence", sentence, indentation=1)

        # Generate Sentence Object
        sentence_object = Parser.parse_sentence(sentence)

        DebugTools.logging.print_debug("Took", cls.timer.get_duration(), "seconds to parse sentence", indentation=1)

        # Generate Verse Objects
        verses_list = Parser.parse_verses()

        DebugTools.logging.print_debug("Took", cls.timer.get_duration(), "seconds to parse all verses", indentation=1)

        # Calculate Scores
        sorted_verses = Scoring.get_score(verses_list, sentence_object)

        DebugTools.logging.print_debug("Took", cls.timer.get_duration(), "seconds to calculate scores", indentation=1)

        response_array = list()

        for index, info in enumerate(sorted_verses[:no_of_verses]):
            verse_location = info[0]
            verse_item = info[1]
            verse_object = verse_item["verse_object"]
            total_verse_score = verse_item["score"]
            base_word_breakdowns = verse_item["base_word_breakdowns"]
            response_array_item = {
                "verse_location": verse_location,
                "verse_book": verse_object.book,
                "start_chapter": verse_object.start_chapter,
                "start_verse": verse_object.start_verse,
                "end_chapter": verse_object.end_chapter,
                "end_verse": verse_object.end_verse,
                "verse_text": BibleQueryConnection.get_text_all_versions(verse_object.book, verse_object.start_chapter,
                                                                         verse_object.start_verse,
                                                                         verse_object.end_chapter,
                                                                         verse_object.end_verse),
                "book_titles": BibleQueryConnection.get_book_titles(verse_object.book),
                "verse_score": total_verse_score,
                "base_word_breakdowns": []
            }
            if total_verse_score > 0:
                # DebugTools.logging.print_log("Rank", (index + 1))
                # DebugTools.logging.print_log(verse_location, "\nScore:", total_verse_score, "\nText:", response_array_item["verse_text"])
                for item_base_word, base_word_breakdown in base_word_breakdowns.items():
                    base_word = item_base_word
                    best_match_word = base_word_breakdown["best_word"]
                    best_match_score = base_word_breakdown["score"]
                    best_match_word_parent = None
                    if base_word_breakdown["breakdown"] is not None:
                        best_match_word_parent = base_word_breakdown["breakdown"]["parent"]
                    intermediate_word_string = ""
                    if best_match_word_parent is not None and best_match_word_parent != "":
                        intermediate_word_string = " " + best_match_word_parent + " => "
                    # DebugTools.logging.print_log("\n    ", base_word, "=>", intermediate_word_string, best_match_word)
                    # DebugTools.logging.print_log("    Score:", best_match_score)
                    # DebugTools.logging.print_log("    Breakdown:", base_word_breakdown["breakdown"])
                    # DebugTools.logging.print_log("\n")
                    response_array_item["base_word_breakdowns"].append({
                        "best_base_word": base_word,
                        "best_match_word": best_match_word,
                        "best_match_score": best_match_score,
                        "best_match_word_parent": best_match_word_parent,
                        "breakdown": base_word_breakdown["breakdown"]
                    })
                response_array.append(response_array_item)

        cls.timer.print_duration("format response")

        if len(response_array) == 0 or response_array[0]["verse_score"] == 0:
            raise DebugTools.exceptions(101)

        return response_array
