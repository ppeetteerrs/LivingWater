import json

from backend.tools import DebugTools
from .calculations import Calculations
from ..restful.restful import Restful

DebugTools.logging.unmute()

class API:
    @classmethod
    def get_rankings(cls, sentence: str, no_of_verses=30):
        print("new version")
        timer = DebugTools.timer()
        timer.reset()
        response = {
            "results": Calculations.get_rankings(sentence, no_of_verses),
            "time_taken": timer.get_duration()
        }

        DebugTools.logging.print_debug("Total time taken:", response["time_taken"], "seconds")
        return response

    @classmethod
    def modify_synonym(cls, request):
        request_dict = json.loads(request)
        return Restful.modify_synonym(request_dict["base_word"], request_dict["synonym"], request_dict["level"],
                                      bool(request_dict["add_syn"]))

    @classmethod
    def modify_related_words(cls, request):
        request_dict = json.loads(request)
        return Restful.modify_related_words(request_dict["base_word"], request_dict["related_word"],
                                            bool(request_dict["add_link"]))

    @classmethod
    def get_synonyms(cls, json_string):
        return Restful.get_synonyms_and_related(json.loads(json_string))

    @classmethod
    def reset_votes(cls):
        return Restful.reset_votes()

    @classmethod
    def vote(cls, request_item, positive):
        return Restful.vote(json.loads(request_item), bool(json.loads(positive)))

    @classmethod
    def search_verse(cls, query_string):
        return Restful.search_verse(query_string)

    @classmethod
    def edit_link(cls, json_string):
        json_string = json.loads(json_string)
        print(json_string["delete"])
        return Restful.edit_link(json_string["location"], json_string["word"], int(json_string["level"]),
                                 bool(json_string["delete"]))

    @classmethod
    def update_verse_location(cls, old_location: str, new_location: str):
        return Restful.update_verse_location(old_location, new_location)

    @classmethod
    def add_verse(cls, json_string):
        json_string = json.loads(json_string)
        return Restful.add_verse(json_string["location"], json_string["lvl1"], json_string["lvl2"], json_string["lvl3"])

    @classmethod
    def remove_verse(cls, location: str):
        return Restful.remove_verse(location)

    @classmethod
    def add_word(cls, new_word, copy):
        return Restful.add_word(new_word, copy)

    @classmethod
    def delete_word(cls, word):
        return Restful.delete_word(word)
