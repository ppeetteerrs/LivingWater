#!flask/bin/python

from backend.tools.logging import Logging
from dotenv import load_dotenv
load_dotenv(verbose=True)
from backend.server.app import app
from os import getenv

# warnings.filterwarnings("ignore")
Logging.unmute()
app.run(host=getenv("HOST"), port=int(getenv("PORT")), debug=True)
# app.run(debug=True)

# from scripts.bible_crawler.crawler import Master
# Master("niv")
