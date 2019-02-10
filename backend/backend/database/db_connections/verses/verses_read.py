from backend.database.db_connections.verses.verses_connection import VerseConnection as Conn, Verse, VerseKeywordLink, \
    Keyword, BibleQueryConnection
from backend.tools import DebugException


class VerseRead(object):

    @staticmethod
    # Get one or all keywords, in query form or json form
    def get_keyword_record(word: str = None, jsonify: bool = False):
        if word is None:
            all_keyword_records = Conn.session.query(Conn.keyword_table).all()
            if jsonify:
                all_keyword_json = []
                for keyword_record in all_keyword_records:
                    all_keyword_json.append(VerseRead.jsonify_keyword_record(keyword_record))
                return all_keyword_json
            else:
                return all_keyword_records
        else:
            keyword_record = Conn.session.query(Conn.keyword_table).filter(Conn.keyword_table.word == word).first()
            if jsonify:
                return VerseRead.jsonify_keyword_record(keyword_record)
            else:
                return keyword_record

    @staticmethod
    # Jsonify a keyword query
    def jsonify_keyword_record(keyword_record: Keyword):
        keyword_json = {}
        keyword_json["id"] = keyword_record.id
        keyword_json["word"] = keyword_record.word
        keyword_json["appearance"] = keyword_record.appearance
        keyword_json["total_votes"] = keyword_record.total_votes

    @staticmethod
    # Get one or all verses, in query form or json form
    def get_verse_record(location: str = None, jsonify: bool = False):
        if location is None:
            all_verse_records = Conn.session.query(Conn.verse_table).all()
            if jsonify:
                all_verse_json = []
                for verse_record in all_verse_records:
                    all_verse_json.append(VerseRead.jsonify_verse_record(verse_record))
                return all_verse_json
            else:
                return all_verse_records
        else:
            verse_record = Conn.session.query(Conn.verse_table).filter(Conn.verse_table.location == location).first()
            if jsonify:
                return VerseRead.jsonify_verse_record(verse_record)
            else:
                return verse_record

    @staticmethod
    # Search for the verse by location or starting with the location passed as argument
    def search_verse(query_string: str, jsonify: bool = False):
        # Try and match the exact location
        matched_verse = VerseRead.get_verse_record(location=query_string)
        if matched_verse is None:
            # Try and match location that starts with query string
            matched_verse = Conn.session.query(Conn.verse_table).filter(
                Conn.verse_table.location.startswith(query_string)).first()
            if matched_verse is None:
                # Raise Exception if nothing is found
                raise DebugException(501)
        if jsonify:
            return VerseRead.jsonify_verse_record(matched_verse)
        else:
            return matched_verse

    @staticmethod
    # Jsonify a verse query
    def jsonify_verse_record(verse_record: Verse):
        verse_json = {}
        verse_json["location"] = verse_record.location
        verse_json["new_location"] = None
        verse_json["book"] = verse_record.book
        verse_json["start_chapter"] = verse_record.start_chapter
        verse_json["start_verse"] = verse_record.start_verse
        verse_json["end_chapter"] = verse_record.end_chapter
        verse_json["end_verse"] = verse_record.end_verse
        verse_json["max_vote"] = verse_record.max_vote
        verse_json["text"] = BibleQueryConnection.get_text_all_versions(verse_record.book, verse_record.start_chapter,
                                                                        verse_record.start_verse,
                                                                        verse_record.end_chapter,
                                                                        verse_record.end_verse)
        verse_json["id"] = verse_record.id
        verse_json["keywords"] = [{"word": keyword_link.keyword.word, "level": keyword_link.level} for keyword_link in
                                  verse_record.keyword_links]
        return verse_json

    @staticmethod
    # Get one or all links, in query form or json form
    def get_link_record(verse_record: Verse, word_record: Keyword = None, jsonify=False):
        if verse_record is None:
            raise DebugException(503)
        # Check if a keyword record is provided
        if word_record is None:
            # Return all keyword links for the verse
            all_link_records = Conn.session.query(Conn.link_table).filter(
                Conn.link_table.verse_id == verse_record.id).all()
            if jsonify:
                return [VerseRead.jsonify_link_record(link_record) for link_record in all_link_records]
            else:
                return all_link_records
        else:
            # Return only the link with the keyword
            link_record = Conn.session.query(Conn.link_table).filter(
                Conn.link_table.verse_id == verse_record.id).filter(
                Conn.link_table.keyword_id == word_record.id).first()
            if jsonify:
                return VerseRead.jsonify_link_record(link_record)
            else:
                return link_record

    @staticmethod
    # Jsonify a link query
    def jsonify_link_record(link_record: VerseKeywordLink):
        link_json = {}
        link_json["verse_location"] = link_record.verse.location
        link_json["keyword"] = link_record.keyword.word
        link_json["level"] = link_record.level
        link_json["vote"] = link_record.votes
        return link_json
