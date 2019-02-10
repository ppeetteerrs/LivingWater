from sqlalchemy import *
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *

from .. import SETTINGS
from ..bible.bible_connection_rethink import BibleQueryConnection

# Setup
Base = declarative_base()


class Verse(Base):
    __tablename__ = 'verses'
    id = Column(Integer, primary_key=True)
    location = Column(String, unique=True)
    book = Column(String)
    start_chapter = Column(Integer)
    start_verse = Column(Integer)
    end_chapter = Column(Integer)
    end_verse = Column(Integer)
    keywords = association_proxy('keyword_links', 'keyword')
    max_vote = Column(Integer)

    def __init__(self, location):
        self.location = location
        parsed_location = BibleQueryConnection.parse_location(location)
        self.book = parsed_location["book"]
        self.start_chapter = parsed_location["start_chapter"]
        self.start_verse = parsed_location["start_verse"]
        self.end_chapter = parsed_location["end_chapter"]
        self.end_verse = parsed_location["end_verse"]
        self.max_vote = 1

    def update_max_vote(self):
        self.max_vote = VerseConnection.calc_max_vote(self)


# Keywords Table Model
class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True)
    appearance = Column(Integer)
    total_votes = Column(Integer)

    def __init__(self, word):
        self.word = word
        self.appearance = 0
        self.total_votes = 1


# VerseKeywordLinks Table Model
class VerseKeywordLink(Base):
    __tablename__ = 'verse_keyword_links'
    level = Column(Integer)
    votes = Column(Integer)  # Not in use
    verse_id = Column(Integer, ForeignKey('verses.id'), primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), primary_key=True)
    keyword = relationship("Keyword", primaryjoin=keyword_id == Keyword.id, backref="verse_links")
    verse = relationship("Verse", primaryjoin=verse_id == Verse.id, backref="keyword_links")

    def __init__(self, verse: Verse, keyword: Keyword, level: int):
        self.level = level
        self.verse = verse
        self.keyword = keyword
        self.votes = 1
        # add an appearance to the keyword
        self.keyword.appearance += 1
        self.keyword.total_votes += 1


class VerseConnection(object):
    engine = None
    Session = None
    session = None
    keyword_table = None
    verse_table = None
    link_table = None

    @classmethod
    def setup(cls):
        cls.engine = create_engine("sqlite:///" + SETTINGS["VERSES_DB_PATH"],
                                   connect_args={'check_same_thread': False})
        cls.Session = sessionmaker(bind=cls.engine, autocommit=False, autoflush=False)
        cls.session = cls.Session()
        cls.keyword_table = Keyword
        cls.verse_table = Verse
        cls.link_table = VerseKeywordLink
        # Create Tables
        Base.metadata.create_all(cls.engine)

    @classmethod
    def commit(cls):
        cls.session.commit()

    @classmethod
    def calc_max_vote(cls, verse_record: Verse):
        for keyword_links in verse_record.keyword_links:
            if keyword_links.votes < 1:
                keyword_links.votes = 1
        votes = [keyword_links.votes for keyword_links in verse_record.keyword_links]
        cls.commit()
        if len(votes) > 0:
            return max(votes)
        else:
            return 1


VerseConnection.setup()
