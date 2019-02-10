from threading import Thread, Lock

import requests
from bs4 import BeautifulSoup as bs

from backend.database.db_connections.bible.bible_crawler_connection_rethink import BibleCrawlerConnection
from . import PARAMS, BOOK_TITLES


def get_soup(url: str):
    html = requests.get(url)
    if html.status_code == 404:
        soup = None
        print("ERROR: URL", url, "does not exist")
    else:
        soup = bs(html.content, "html5lib")
    return soup


class Slave(Thread):
    db_lock = Lock()
    log_lock = Lock()

    def __init__(self, book_title: str, url: str, master,
                 verbose: bool = True):
        self.book_title = book_title
        self.url = url
        self.master = master
        self.verbose = verbose
        self.chapters = {}
        Thread.__init__(self)

    def run(self):
        self.log_lock.acquire()
        print("Book", self.book_title, "started")
        self.log_lock.release()
        self.chapters = self.crawl_bible_book_page()
        for chapter_number, chapter_url in self.chapters.items():
            self.crawl_chapter_page(chapter_number, chapter_url)
            self.log_lock.acquire()
            print("Book", self.book_title, chapter_number, "/", len(self.chapters.keys()))
            self.log_lock.release()
        self.log_lock.acquire()
        print("Book", self.book_title, "done")
        self.log_lock.release()

    def crawl_bible_book_page(self):
        soup = get_soup(self.url)
        chapter_urls = {}
        chapter_titles = {}
        chapter_elements = soup.find_all("a", {"class": "btn btn-lg bst-button-white btn-block"})
        for chapter_element in chapter_elements:
            chapter_number = chapter_element.text.strip()
            chapter_urls[chapter_number] = chapter_element["href"]
            chapter_titles[chapter_number] = {}

        # Create chapters
        self.db_lock.acquire()
        self.master.db.create_chapters(self.book_title, chapter_titles)
        self.db_lock.release()
        return chapter_urls

    def crawl_chapter_page(self, chapter_number: str, chapter_url: str):
        soup = get_soup(chapter_url)
        verses = {}
        verse_container_elements = soup.find_all("div", {"class": "verse"})
        for verse_container_element in verse_container_elements:
            verse_number = verse_container_element.find("span", {"class": "verse-number"}).find("strong").text.strip()
            verse_content_element = verse_container_element.find("span", {"class": "verse-" + verse_number})
            for verse_content_element_child in verse_content_element.find_all():
                if verse_content_element_child.name != "span":
                    verse_content_element_child.decompose()
            verse_content = verse_content_element.text.strip()
            verses[verse_number] = verse_content
        self.db_lock.acquire()
        self.master.db.create_verses(book=self.book_title, chapter_number=chapter_number, verses=verses)
        self.db_lock.release()
        return verses


# The master belongs to a bible version and owns an army of slaves (each responsible for a book)
class Master(object):

    def __init__(self, version: str = PARAMS["bible_version"],
                 verbose: bool = True):

        # Setup version and prefix properties of the master
        self.version = version
        self.url = PARAMS["base_url"] + version + "/"
        self.verbose = verbose

        # Setup bible book list
        book_titles = self.crawl_bible_version_page()
        self.book_titles = self.parse_book_titles(book_titles)
        self.slaves = self.create_slaves()

    def crawl_bible_version_page(self):
        soup = get_soup(self.url)
        book_title_elements = soup.find_all("h4", {"class": "small-header"})
        return book_title_elements

    def parse_book_titles(self, book_title_elements):
        # Each book item in the DB
        # id, title, displayed_title, url, max_chapter_number, content
        # content: chapter: { verse_number: text... , max_verse_number: }

        formatted_titles = []

        # Use English title as db index
        for index, book_title_element in enumerate(book_title_elements):
            title = BOOK_TITLES[index]
            displayed_title = book_title_element.text
            url = book_title_element.parent["href"]
            formatted_titles.append(
                {"id": title, "title": title, "displayed_title": displayed_title, "url": url, "content": {}})

        self.db = BibleCrawlerConnection(version=self.version, url=self.url, books=formatted_titles)

        return formatted_titles

    def create_slaves(self):
        army = []

        for book_title_item in self.book_titles:
            if True:  # book_title_item["title"] is "Luke":
                slave = Slave(book_title=book_title_item["title"], url=book_title_item["url"], master=self)
                army.append(slave)
                slave.start()

        return army
