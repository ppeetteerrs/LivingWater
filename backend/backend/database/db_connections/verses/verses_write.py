import string

from backend.database.db_connections.bible.bible_connection_rethink import BibleQueryConnection
from backend.database.db_connections.translation.british_to_american import BritishAmericanConnection
from backend.database.db_connections.verses.verses_connection import VerseConnection as Conn, Verse, VerseKeywordLink, \
    Keyword
from backend.database.db_connections.verses.verses_read import VerseRead
from backend.tools import DebugException, DebugTools


class VerseWrite(object):

    @staticmethod
    # Add a keyword record
    def add_keyword(word: str):
        Conn.session.add(Conn.keyword_table(VerseWrite._clean(word, convert_to_american=True)))
        Conn.commit()

    @staticmethod
    # Add a verse record [Need verification]
    def add_verse(location: str, lvl1: [str] = [], lvl2: [str] = [], lvl3: [str] = []):
        # Check if verse already exists
        verse_record: Verse = VerseRead.get_verse_record(location)
        if verse_record is None:
            # Add the verse record if the verse does not exist yet and retrieve added record
            Conn.session.add(Conn.verse_table(location))
            Conn.commit()
            verse_record = VerseRead.get_verse_record(location)
        else:
            # If verse already exists, raise an error
            raise DebugException(502)

        # Combine keywords into one list
        keyword_list = [(word, 3) for word in VerseWrite._clean_list(lvl3, convert_to_american=True)]
        keyword_list.extend([(word, 2) for word in VerseWrite._clean_list(lvl2, convert_to_american=True)])
        keyword_list.extend([(word, 1) for word in VerseWrite._clean_list(lvl1, convert_to_american=True)])

        # Update keyword links
        for keyword, level in keyword_list:
            # Check if keyword already exists in DB
            keyword_record = VerseRead.get_keyword_record(keyword)
            # Add keyword if it doesn't exist
            if keyword_record is None:
                VerseWrite.add_keyword(keyword)
                keyword_record = VerseRead.get_keyword_record(keyword)

            # Check if link already exists in DB
            link_record = VerseRead.get_link_record(verse_record, keyword_record)

            if link_record is None:
                # Add link if it doesn't exist
                Conn.session.add(Conn.link_table(verse_record, keyword_record, level))
                Conn.commit()
            else:
                # Update link if it exists
                link_record.level = level
                Conn.commit()
        return VerseRead.get_verse_record(location, jsonify=True)

    @classmethod
    def remove_verse(cls, location: str):
        verse_record: Verse = VerseRead.get_verse_record(location)
        if verse_record is None:
            raise DebugException(503)
        else:
            # Remove all links and the verse
            link_records = VerseRead.get_link_record(verse_record, jsonify=False)
            for link_record in link_records:
                Conn.session.delete(link_record)
            Conn.commit()
            Conn.session.delete(verse_record)
            Conn.commit()
            return VerseRead.jsonify_verse_record(verse_record)

    @staticmethod
    # Update verse location
    def update_verse_location(location: str, new_location: str):
        # Check if verse exists
        verse_record: Verse = VerseRead.get_verse_record(location)
        # Check if new verse already exists
        new_verse_record: Verse = VerseRead.get_verse_record(new_location)
        # Check if location of the verse is updated
        if verse_record is not None and new_verse_record is None:
            # Update verse location if a new location is provided
            verse_record.location = new_location
            Conn.commit()
        elif new_verse_record is not None:
            raise DebugException(502)
        else:
            raise DebugException(503)
        return VerseRead.get_verse_record(new_location, jsonify=True)

    @staticmethod
    # Add, Update or Delete verse keyword link
    def edit_link(location: str, word: str, level: int, delete: bool = False, jsonify=False):
        # Clean words only if it is not deleting
        if not delete:
            word = VerseWrite._clean(word, convert_to_american=True)

        # Verify weight level
        if (not isinstance(level, int)) or level > 3 or level < 1:
            print(isinstance(level, int))
            raise DebugException(504)

        # Check if link already exists
        verse_record: Verse = VerseRead.get_verse_record(location)
        keyword_record: Keyword = VerseRead.get_keyword_record(word)
        if keyword_record is None:
            # If keyword does not exist, add it to db
            VerseWrite.add_keyword(word)
            keyword_record = VerseRead.get_keyword_record(word)
        link_record: VerseKeywordLink = VerseRead.get_link_record(verse_record, keyword_record)

        if link_record is not None:
            if delete:
                # Update link if it already exists
                link_record.keyword.appearance -= 1
                link_record.keyword.total_votes -= link_record.votes
                link_record.verse.update_max_vote()
                Conn.session.delete(link_record)
                Conn.commit()
                return VerseRead.jsonify_link_record(link_record)
            else:
                # Update link if it already exists
                link_record.level = level
                Conn.commit()
        else:
            if delete:
                # Trying to delete non-existent link
                raise DebugException(503)
            else:
                # Add link if it doesnt exist
                verse_record.keyword_links.append(Conn.link_table(verse_record, keyword_record, level))
                Conn.commit()

        return VerseRead.get_link_record(verse_record, keyword_record, jsonify)

    @staticmethod
    def update_frequency_info():
        all_verses = VerseRead.get_verse_record()
        all_keywords = VerseRead.get_keyword_record()
        all_keywords_dict = dict(
            [(keyword_record.word, {"number_of_appearance": 0, "total_votes": 0}) for keyword_record in all_keywords])
        for verse_index, verse_record in enumerate(all_verses):
            DebugTools.logging.print_debug("Frequency Update Progress:", (verse_index + 1), "/", len(all_verses))
            verse_record.update_max_vote()
            for keyword_link in verse_record.keyword_links:
                all_keywords_dict[keyword_link.keyword.word]["number_of_appearance"] += 1
                all_keywords_dict[keyword_link.keyword.word]["total_votes"] += keyword_link.votes
        for keyword_record in all_keywords:
            keyword_record.appearance = all_keywords_dict[keyword_record.word]["number_of_appearance"]
            keyword_record.total_votes = all_keywords_dict[keyword_record.word]["total_votes"]
        Conn.commit()

    @staticmethod
    def _clean(word, convert_to_american):

        if word is None:
            return None

        word = word.strip()

        # Remove all punctuations
        no_punc = word.translate(str.maketrans('', '', string.punctuation))

        # Remove all whitespaces
        no_white = no_punc.strip()  # Lowercase
        lowercase = no_white.lower()

        # Convert to American English
        if convert_to_american:
            lowercase_american = BritishAmericanConnection.british_to_american(lowercase)
            return lowercase_american
        else:
            return lowercase

    @staticmethod
    def _clean_list(words, convert_to_american):
        split1 = list()
        for word in words:
            split1.extend(word.split(" "))
        split2 = list()
        for split1word in split1:
            split2.extend(split1word.split("."))
        cleaned_word_list = [VerseWrite._clean(word, convert_to_american) for word in split2]
        cleaned_word_list = [word for word in cleaned_word_list if word != "" and word is not None]
        return cleaned_word_list

    @staticmethod
    def british_to_american():
        keyword_records = VerseRead.get_keyword_record()
        all_keywords = [keyword_record.word for keyword_record in keyword_records]
        for keyword_record in keyword_records:
            if BritishAmericanConnection.british_to_american(keyword_record.word) in all_keywords:
                print(keyword_record.word, BritishAmericanConnection.british_to_american(keyword_record.word))
        print("done")

    @staticmethod
    # Update the text of all verses to NIV version format
    def update_all_verses_text(version: str = "niv"):
        all_verses = VerseRead.get_verse_record()
        for verse in all_verses:
            try:
                verse.text = BibleQueryConnection.get_text_dict_with_parsing(version, verse.location)
            except Exception as e:
                print(e)
                print(verse.location)
                break
        Conn.commit()
