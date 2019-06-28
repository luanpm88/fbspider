import os
import pymongo
from elasticsearch_dsl import connections

username = os.getenv("FB_EMAIL", None)
password = os.getenv("FB_PASS", None)

db = pymongo.MongoClient("mongodb://localhost:27017")
dbr = pymongo.MongoClient("mongodb://broot:Robin9Test!@167.99.79.165:27017")
db_crawler = "crawler_fb"
connections.create_connection(hosts=["localhost:9200"], timeout=20)

html_parser = "lxml"

path_output = "output/"
path_input = "output/"
sleep_time = 0.5

fb = "https://m.facebook.com/"
fb_desktop = "https://www.facebook.com"
fb_login = "login/"
fb_graph_search_prefix = "graphsearch/str/"
fb_graph_search_suffix = "/stories-keyword/stories-public"
# fb_about = "about/"
# fb_posts = "posts/"
fb_approve_login = "login/device-based/update-nonce/"

DIV = "div"
A = "a"
HREF = "href"
P = "p"
LI = "li"
IMG = "img"
SMALL = "small"
SPAN = "span"
# input_id_login = "m_login_email"
id_feed = "m_newsfeed_stream"
div_id_posts = "BrowseResultsContainer"
div_id_root = "root"
div_id_recent = "recent"
div_id_link = "see_more_pager"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux) Gecko/20100101 Firefox/63.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "text/html; charset=utf-8"
}

login_data_fb = {
    # "_fb_no_script": True,
    "email": username,  # IMPORTANT
    "li": "",  # IMPORTANT
    "login": "Log+In",
    "lsd":	"AVpdIsgA",  # IMPORTANT?
    "pass": password,  # IMPORTANT
    "m_ts": "",
    "try_number": "0",
    "unrecognized_tries": "0",
}

months = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
    "Dec": 12,
    "Nov": 11,
    "Oct": 10,
    "Sep": 9,
    "Aug": 8,
    "Jul": 7,
    "Jun": 6,
    "Apr": 4,
    "Mar": 3,
    "Feb": 2,
    "Jan": 1
}


fieldnames_OTA = [
    "Platform",
    "Brand",
    "Keyword",
    "Poster",
    "Poster ID",
    "Like",
    "Comment",
    "Share",
    "Followers",
    "Following",
    "Location",
    "DateOfPost",
    "Url",
    "Subject",
    "Content",
]
# I/O


fieldnames_input = [
    "category_id",
    "category_name",
    "query",
    "keywords"
]

fieldnames_output = [
    "account_id",
    "category_id",
    "category_name",
    "platform",
    "id",
    "title",
    "published_date",
    "author_name",
    "author_id",
    "author_image_url",
    "followers",
    "following",
    "post_type",
    "post_data",
    "link",
    "like_count",
    "dislike_count",
    "share_count",
    "comment_count",
    "view_count",
    "language",
    "sentiment",
    "iso_code",
    "iso_area",
    "parent_url",
    "parent_id",
    "delivered_date",
    "keywords",
]
