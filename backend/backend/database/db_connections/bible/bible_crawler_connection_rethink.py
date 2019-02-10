import rethinkdb as r


class BibleCrawlerConnection(object):

    def __init__(self, version: str, url: str, books):
        self.connection = r.connect("localhost", 28015)
        self.DB = r.db("bible")
        self.table = self.setup_table(version)
        self.create_books(books)

    def setup_table(self, bible_version: str):
        if bible_version not in self.DB.table_list().run(self.connection):
            self.DB.table_create(bible_version).run(self.connection)
            self.DB.table(bible_version).index_create("title").run(self.connection)
        return self.DB.table(bible_version)

    def create_books(self, books):
        results = self.table.insert(books).run(self.connection)

    def create_chapters(self, book: str, chapters: {}):
        results = self.table.get(book).update({"content": chapters}).run(self.connection)

    def create_verses(self, book: str, chapter_number: str, verses: {}):
        results = self.table.get(book).update({"content": {chapter_number: verses}}).run(self.connection)
