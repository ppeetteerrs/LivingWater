import rethinkdb as r

from backend.tools import DebugTools, DebugException


class BibleQueryConnection(object):
    connection = r.connect("localhost", 28015)
    DB = r.db("bible")
    bible_dict = {}

    @classmethod
    def setup_cache(cls):
        for version in cls.DB.table_list().run(cls.connection):
            version_book_array = cls.DB.table(version).coerce_to("array").run(cls.connection)
            cls.bible_dict[version] = {}
            for item in version_book_array:
                cls.bible_dict[version][item["title"]] = item

    # Convert text location into formatted location
    @classmethod
    def parse_location(cls, full_location: str):
        try:
            full_location_split = full_location.split(" ")
            book_title = ""
            for part in full_location_split[:-1]:
                book_title += part + " "
            book_title = book_title.strip()
            full_verse_location_array = full_location_split[-1].split("-")
            if len(full_verse_location_array) == 2:
                # Has start and end
                start_chapter_text, start_verse_text = full_verse_location_array[0].split(":")
                end_chapter_text, end_verse_text = full_verse_location_array[1].split(":")
                start_chapter = cls.text_to_int(start_chapter_text)
                start_verse = cls.text_to_int(start_verse_text)
                end_chapter = cls.text_to_int(end_chapter_text)
                end_verse = cls.text_to_int(end_verse_text)
                return {"book": book_title, "start_chapter": start_chapter, "start_verse": start_verse,
                        "end_chapter": end_chapter, "end_verse": end_verse}
            elif len(full_verse_location_array) == 1:
                # Only start verse
                chapter, verse = full_verse_location_array[0].split(":")
                return {"book": book_title, "start_chapter": chapter, "start_verse": verse,
                        "end_chapter": None, "end_verse": None}
            else:
                DebugTools.logging.print_debug("Unable to Parse Verse Location")
        except Exception:
            raise DebugException(507)

    @classmethod
    def get_text_dict_with_parsing(cls, version: str, full_location: str):
        parsed_locations = cls.parse_location(full_location)
        text_dict = cls.get_text_with_version(version, parsed_locations["book"], str(parsed_locations["start_chapter"]),
                                              str(parsed_locations["start_verse"]),
                                              str(parsed_locations["end_chapter"]),
                                              str(parsed_locations["end_verse"]))
        return text_dict

    @classmethod
    def get_book_titles(cls, book: str):
        book_titles = {}
        for version, book_item in cls.bible_dict.items():
            book_titles[version] = book_item[book]["displayed_title"]
        return book_titles

    @classmethod
    def get_text_with_version(cls, version: str, book: str, start_chapter_text, start_verse_text,
                              end_chapter_text=None, end_verse_text=None):
        try:
            if version not in cls.bible_dict:
                raise DebugException(506)
        except Exception:
            raise DebugException(506)

        try:

            start_chapter = cls.text_to_int(start_chapter_text)
            start_verse = cls.text_to_int(start_verse_text)
            end_chapter = cls.text_to_int(end_chapter_text)
            end_verse = cls.text_to_int(end_verse_text)

            # Get dictionary object for the whole book
            book_text = cls.bible_dict[version][book]["content"]

            if end_chapter_text is not None:

                relevant_book_text = {}

                # Iterate over dictionary object to filter unused chapters
                for key, val in book_text.items():

                    if start_chapter < int(key) < end_chapter:
                        # If it is between start and end chapters, add it in
                        relevant_book_text[key] = val
                    if int(key) == start_chapter:
                        # If it is starting chapter, filter away unrelated verses
                        relevant_verses = {}
                        for verse, verse_content in val.items():
                            if int(verse) >= start_verse:
                                relevant_verses[verse] = verse_content
                        relevant_book_text[key] = relevant_verses
                    if int(key) == end_chapter:
                        # If it is ending chapter, filter away unrelated verses
                        relevant_verses = {}
                        for verse, verse_content in val.items():
                            if int(verse) <= end_verse:
                                relevant_verses[verse] = verse_content
                        relevant_book_text[key] = relevant_verses
            else:
                relevant_book_text = {
                    start_chapter_text: {start_verse_text: book_text[str(start_chapter)][str(start_verse)]}}
            return relevant_book_text

        except Exception as e:
            DebugTools.logging.print_debug(version, book, start_chapter_text, start_verse_text, end_chapter_text,
                                           end_verse_text)
            raise DebugException(505)

    @classmethod
    def get_text_all_versions(cls, book: str, start_chapter_text, start_verse_text,
                              end_chapter_text=None, end_verse_text=None):
        all_versions = cls.DB.table_list().run(cls.connection)

        text_response = {}

        for version in all_versions:
            version_text = cls.get_text_with_version(version, book, start_chapter_text, start_verse_text,
                                                     end_chapter_text, end_verse_text)
            text_response[version] = version_text

        return text_response

    @staticmethod
    def text_to_int(text: str):
        if text is None:
            return None
        if isinstance(text, int):
            return text
        end_text = ""
        for char in text:
            if char.isdigit():
                end_text += char
        return int(end_text)


BibleQueryConnection.setup_cache()
