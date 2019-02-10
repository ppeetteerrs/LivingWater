import pickle
import warnings

from scripts.crawler.crawler import Crawler
from scripts.crawler.middleman import MiddleMan
from scripts.database.database import Connection

warnings.filterwarnings('ignore')

# Prepare word list
word_list_raw = pickle.load(open("assets/common_words.h5", "rb"))

Connection.setup()
Crawler.setup(word_list_raw)
MiddleMan.setup(Connection, verbose=False)

verbose = False

for index in range(0, 20):
    crawler = Crawler(index, verbose=verbose)
    crawler.start()
