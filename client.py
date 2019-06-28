import time
import re
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import unquote

import pycountry
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium.common.exceptions
from selenium.webdriver.firefox.options import Options

import caching
import config
import models
import web
from models import local
from models import post
from models import search


options = Options()
options.headless = True


def make_driver():
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.facebook.com/apps/site_scraping_tos_terms.php")
    cookies = [

    ]

    for c in cookies:
        driver.add_cookie(
            {'name': c.get("name"), 'value': c.get("value"), 'domain': "www.facebook.com"})
    return driver


class Session(requests.Session):
    def __init__(self):
        super().__init__()

    def close(self):
        self.close()


class Parser(object):

    def __init__(self, timedelta=None):
        self.timedelta = timedelta

        self.session = Session()
        self.html_scanner = local.FacebookHTMLProcessor()
        self.web = web.Web(self.session)
        self.location = post.LocationPage
        self.post_handler = models.post.PostFacebook
        self.driver = make_driver()

    def login(self):
        # TODO add credentials rotation
        url = config.fb_login
        credentials = config.login_data_fb
        login_page = self.web.get(url)
        post_data = self.html_scanner.get_login_hidden_data(login_page)
        credentials.update(post_data)
        response_login = self.web.post(url, credentials)
        with open("html/current_login.html", "w") as f:
            f.write(response_login)
        return

    @staticmethod
    def validate_date(post_date, timedelta):
        print(f"post_date: {post_date}")
        if not post_date:
            # if no date provided. Empty string
            return "add"
        elif timedelta[0] > timedelta[1]:
            return "break"
        elif timedelta[0] <= post_date <= timedelta[1]:
            return "add"
        elif timedelta[0] > post_date:
            return "break"
        elif post_date > timedelta[1]:
            return "skip"
        else:
            raise ValueError(f"Wrong date comparison {post_date}: {timedelta}")

    def _user_id(self, related_link):
        url_parsed = urlparse(f"https://www.facebook.com{related_link}")

        if url_parsed.path.startswith("/profile.php"):
            uid = parse_qs(url_parsed.query).get("id")[0]
        else:
            uid = url_parsed.path.replace("/", "")

        if uid.startswith("/"):
            endposition = uid.find("?")
            uid = uid[1:endposition]
        return uid

    def _get_location(self, href):
        if not href:
            return "", ""
        html = self.web.get(href[1:])
        location_str = self.location(html).get_location()
        if not location_str:
            return "", ""

        location_list = location_str.split(", ")
        for l in location_list:
            if l == "Vietnam":
                l = "Viet Nam"

            loc_search = pycountry.countries.get(name=l)

            if loc_search:
                return loc_search.alpha_2, loc_search.numeric
        return "", ""

    def _language_filter(self, posts, languages):
        post_filtered = []
        for p in posts:
            post_body = p["post_data"]
            res = re.findall(r'[\u4e00-\u9fff]+', post_body)
            if res:
                post_filtered.append(p)
        return post_filtered

    def _post_info(self, crawled_posts, keywords, excluded):
        posts_filtered = list()
        continue_search = True
        if keywords:
            search_keywords = [
                *keywords,
                *[s.replace(" ", "") for s in keywords]
            ]
        else:
            search_keywords = []

        if excluded and "" in excluded:
            del excluded[excluded.index("")]

        if "" in search_keywords:
            search_keywords = list(set(search_keywords))
            del search_keywords[search_keywords.index("")]

        for p in crawled_posts:
            post_object = self.post_handler(p)
            post_info = post_object.info(self.timedelta)
            # For Account no reason to continue (posts sorted)
            if isinstance(self, AccountParser) \
                    and post_info.get("break", False):

                continue_search = False
                return posts_filtered, continue_search
            if not post_info.get("link", False):
                continue

            full_post_html = self.web.get(post_info.get("link")[1:])

            content_full = post.FullPagePostM(full_post_html)
            post_text = content_full.get_text()

            if post_text:
                post_info["post_data"] = content_full.get_text()

            # Validate data doesn't contain excluded
            if excluded:
                excluded_found = False
                for k in excluded:
                    search_res = re.search(
                        re.escape(k),
                        re.escape(post_info.get("post_data", "")),
                        re.IGNORECASE
                    )
                    if search_res:
                        excluded_found = True
                        break
                if excluded_found:
                    continue

            # Validate data contain keywords
            if search_keywords:
                keyword_found = False
                for k in search_keywords:

                    search_res = re.search(
                        re.escape(k),
                        re.escape(post_info.get("post_data", "")),
                        re.IGNORECASE
                    )
                    if search_res:
                        keyword_found = True
                        break
                if not keyword_found:
                    continue

            posts_filtered.append(post_info)

        return posts_filtered, continue_search

    def _post_postprocessing(self, posts):
        posts_processed = []

        for p in posts:
            if "/story.php?story_fbid" in p["link"]:
                fields_url = ["id", "/story.php?story_fbid"]
                post_link_parsed = parse_qs(p['link'].replace(
                    "&__tn__=%2AW#footer_action_list", ""))
                post_link_filtered = unquote(
                    urlencode({q: post_link_parsed[q] for q in post_link_parsed if q in fields_url}))
                post_link_filtered = post_link_filtered.replace("['", "")
                post_link_filtered = post_link_filtered.replace("']", "")
                p["link"] = f"https://www.facebook.com{post_link_filtered}"
            elif "photos.php" in p["link"]:
                post_link_filtered = "https://www.facebook.com".format(
                    p["link"][:p["link"].find("?type")])
                endposition = post_link_filtered.find("&set")
                post_link_filtered = post_link_filtered[:endposition]
            elif f"/photos/" in p["link"]:
                post_link_filtered = urlparse(p["link"]).path
                p["link"] = post_link_filtered
            else:
                post_link_filtered = p["link"]

            p["post_data"] = re.sub(" +", " ", p["post_data"])
            p["post_data"] = p["post_data"].strip()
            p["published_date"] = str(p["published_date"])
            p["link"] = f"https://www.facebook.com{post_link_filtered}"
            p["author_id"] = self._user_id(p["author_id"])
            p["iso_code"], p["iso_area"] = self._get_location(p.get("iso_href", ""))
            # p["followers"] = self.get_follower(p["author_id"])
            # p["share_count"] = self.get_share(p["link"])
            p["followers"] = ""
            p["share_count"] = ""

            posts_processed.append(p)

        return posts_processed

    def _posts(self, searchfunc, queryies, keywords=None, excluded=None, iteration_depth=-1):
        posts = []

        for query in queryies:
            print(f"query {query}")

            posts_list, next_page_link = searchfunc(query)
            posts_filtered, continue_search = self._post_info(posts_list, keywords, excluded)
            posts.extend(posts_filtered)
            iterator = 0

            while next_page_link:
                if isinstance(self, AccountParser):
                    next_page_link = next_page_link[1:]
                else:
                    next_page_link = next_page_link[39:]
                posts_list, next_page_link = searchfunc(next_page_link, api=False)
                posts_filtered, continue_search = self._post_info(
                    posts_list,
                    keywords,
                    excluded
                )

                posts.extend(posts_filtered)

                if not continue_search:
                    next_page_link = ""

                iterator += 1
                if iterator == iteration_depth:
                    break

        posts_postprocessend = self._post_postprocessing(posts)
        return posts_postprocessend

    def posts_collect(
            self,
            searchfunc,
            query,
            keywords=None,
            excluded=None,
            comments=True,
            languages=None,
            iter_depth_posts=-1,
            iter_depth_comments=-1
    ):
        posts = self._posts(searchfunc, query, keywords, excluded, iter_depth_posts)

        if languages:
            posts = self._language_filter(posts, languages)

        return posts


class AccountParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SearchHtml = models.search.AccountPageFacebook

    def search(self, *args, **kwargs):
        posts = self.posts_collect(self._account_search, *args, **kwargs)
        return posts

    def _account_search(self, search_query, api=False):
        search_data = search_query
        if api:
            search_data = search_query
        search_result = self.SearchHtml(self.web.get(search_data))
        posts, next_page_link = search_result.get_posts()
        return posts, next_page_link


class PagesFacebook(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SearchHtml = models.search.PagesFacebook

    def search(self, *args, **kwargs):
        posts = self.posts_collect(self._account_search, *args, **kwargs)
        return posts

    def _account_search(self, search_query, api=False):
        search_data = search_query
        if api:
            search_data = search_query
        search_result = self.SearchHtml(self.web.get(search_data))
        posts, next_page_link = search_result.get_posts()
        return posts, next_page_link


class GraphParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SearchHtml = models.search.GraphPageFacebook

    def search(self, *args, **kwargs):
        posts = self.posts_collect(self._graph_search, *args, **kwargs)
        return posts

    def _graph_search(self, search_query, api=False):
        search_data = "{prefix}{data}{suffix}".format(
            prefix=config.fb_graph_search_prefix,
            data="+".join(search_query.split(" ")),
            suffix=config.fb_graph_search_suffix
        )
        if api:
            search_data = search_query
        search_result = self.SearchHtml(self.web.get(search_data))
        posts, next_page_link = search_result.get_posts()
        return posts, next_page_link
