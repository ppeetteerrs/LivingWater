from backend.database.db_connections.dict.dict_connection_rethink import DictConnection
from backend.database.db_connections.verses.verses_connection import VerseConnection
from backend.database.db_connections.verses.verses_read import VerseRead
from backend.database.db_connections.verses.verses_write import VerseWrite
from backend.tools import DebugTools
from backend.tools.nlp import NLP


class Restful(object):
    @classmethod
    def modify_synonym(cls, base_word: str, synonym: str, level=0, add_syn: bool = True):

        # Check if both base_word and synonym are valid
        cleaned_sentence = NLP.clean(base_word)
        if len(cleaned_sentence) == 0 or cleaned_sentence[0] == "":
            raise DebugTools.exceptions(304, base_word)
        else:
            base_word = cleaned_sentence[0]
        # Only clean synonym if we are adding it
        if add_syn:
            cleaned_sentence = NLP.clean(synonym)
            if len(cleaned_sentence) == 0 or cleaned_sentence[0] == "":
                raise DebugTools.exceptions(309, synonym)
            else:
                synonym = cleaned_sentence[0]
        # Check if synonym is same as base word
        if base_word == synonym:
            raise DebugTools.exceptions(310)
        if add_syn:
            response = DictConnection.change_syn_record(base_word, synonym, level)
            return response
        else:
            response = DictConnection.remove_syn_record(base_word, synonym)
            return response

    @classmethod
    def modify_related_words(cls, base_word: str, synonym: str, add_relation: bool = True):
        cleaned_sentence = NLP.clean(base_word)
        if len(cleaned_sentence) == 0 or cleaned_sentence[0] == "":
            raise DebugTools.exceptions(304, base_word)
        else:
            base_word = cleaned_sentence[0]
        if add_relation:
            cleaned_sentence = NLP.clean(synonym)
            if len(cleaned_sentence) == 0 or cleaned_sentence[0] == "":
                raise DebugTools.exceptions(309, synonym)
            else:
                synonym = cleaned_sentence[0]
        if base_word == synonym:
            raise DebugTools.exceptions(310)
        response = DictConnection.modify_related_words(base_word, synonym, add_relation=add_relation)
        return response

    @classmethod
    def get_synonyms_and_related(cls, base_word):
        cleaned_sentence = NLP.clean(base_word)
        if len(cleaned_sentence) == 0 or cleaned_sentence[0] == "":
            raise DebugTools.exceptions(304, base_word)
        else:
            cleaned_word = cleaned_sentence[0]
        # word_record = DictConnection.get_word_record(cleaned_word)
        syn_dict = DictConnection.get_word_list_syns_and_related([cleaned_word])[cleaned_word]

        response = []

        for k, v in syn_dict.items():
            if v["parent"] == cleaned_word:
                # Directly related
                response.append((k, v))
            elif v["parent"] is None and v["weight"] < 1:
                # Synonym
                v["weight"] = v["weight"] / DictConnection.syn_decay
                response.append((k, v))
        return response

    @classmethod
    def reset_votes(cls):
        verses = VerseRead.get_verse_record()
        for verse_record in verses:
            verse_record.max_vote = 1
            for keyword_link in verse_record.keyword_links:
                keyword_link.votes = 1
        VerseConnection.session.commit()

        return "Completed"

    @classmethod
    def vote(cls, response_item, positive: bool):

        # Get Relevant Verse
        verse_record = VerseRead.get_verse_record(response_item["location"])

        # Get Matched Words
        matched_words = [breakdown_item["matched_word"] for breakdown_item in response_item["breakdown"]]

        # Increase vote for matched keywords
        if positive:
            for keyword_link in verse_record.keyword_links:
                # Add a vote if the keyword is matched
                if keyword_link.keyword.word in matched_words:
                    keyword_link.votes += 1
                    keyword_link.keyword.total_votes += 1
                    print(keyword_link.keyword.word, "now has votes", keyword_link.votes)
        else:
            for keyword_link in verse_record.keyword_links:
                # Add a vote if the keyword is matched
                if keyword_link.keyword.word in matched_words and keyword_link.votes > 1:
                    keyword_link.votes -= 1
                    keyword_link.keyword.total_votes -= 1
                    print(keyword_link.keyword.word, "now has votes", keyword_link.votes)

        verse_record.update_max_vote()
        VerseConnection.session.commit()

        return "Done"

    @classmethod
    def search_verse(cls, query_string):
        verse_json = VerseRead.search_verse(query_string=query_string, jsonify=True)
        return verse_json

    @classmethod
    def edit_link(cls, location: str, word: str, level: int, delete: bool = False):
        return VerseWrite.edit_link(location, word, level, delete, jsonify=True)

    @classmethod
    def update_verse_location(cls, old_location: str, new_location: str):
        return VerseWrite.update_verse_location(old_location, new_location)

    @classmethod
    def add_verse(cls, location: str, lvl1: [str] = [], lvl2: [str] = [], lvl3: [str] = []):
        return VerseWrite.add_verse(location, lvl1, lvl2, lvl3)

    @classmethod
    def remove_verse(cls, location: str):
        return VerseWrite.remove_verse(location)

    @classmethod
    def add_word(cls, new_word: str, copy: str):
        return DictConnection.copy_word(new_word, copy)

    @classmethod
    def delete_word(cls, word: str):
        return DictConnection.delete_word(word)
