import re

import config
from . import html_processor


class SearchObject(object):
    def __init__(self, html):
        self.page = html_processor.HTMLScanner(html)


class AccountPageFacebook(SearchObject):

    def __init__(self, html):
        super().__init__(html)

    def get_posts(self):
        """
        Get user page. Return all available posts from this range of month.
        Return info

        :param userpage: str - html page
        :param timedelta: - tuple of datetime.date
        :return:
            posts - list of dicts
            link - link for next page of posts in requirede

        """

        # if "Page Not Found" in html.head.title.get_text():
        #     return list(), ""
        with open("html/current_page_acc.html", "w") as f:
            f.write(str(self.page))

        posts_root = self.page.find(config.DIV, id=config.div_id_root)
        try:
            posts_area = posts_root.find(config.DIV, id=config.div_id_recent)
        except AttributeError:
            with open("jbjjln.html", "w", encoding="utf-8") as f:
                f.write(str(self.page))
            raise Exception

        if not posts_area:
            return list(), ""

        post_divs = posts_area.find_all(
            config.DIV,
            id=re.compile(r"^\w{1}_[\w\d]{1}_[\w\d]{1}$"),
            class_=re.compile(r"^(\w{2}\s){2}\w{2}$"),
            role="article"
        )

        try:
            link_tag = posts_area.next_sibling.find("a")
            if link_tag:
                link = link_tag["href"]
            else:
                link = ""
        except AttributeError:
            link = ""

        return post_divs, link


class GraphPageFacebook(SearchObject):

    def __init__(self, html):
        super().__init__(html)

    def get_posts(self):
        """
        Get user page. Return all available posts from this range of month.
        Return info

        :param userpage: str - html page
        :param timedelta: - tuple of datetime.date
        :return:
            posts - list of dicts
            link - link for next page of posts in requirede

        """

        # if "Page Not Found" in html.head.title.get_text():
        #     return list(), ""
        with open("html/current_page_kwd.html", "w") as f:
            f.write(str(self.page))

        posts_root = self.page.find(config.DIV, id=config.div_id_root)
        try:
            posts_area = posts_root.find(config.DIV, id=config.div_id_posts)
        except AttributeError:
            with open("html/response_login.html", "w", encoding="utf-8") as f:
                f.write(str(self.page))
            raise Exception

        if not posts_area:
            return list(), ""

        post_divs = posts_area.find_all(
            config.DIV,
            id=re.compile(r"^\w{1}_[\w\d]{1}_[\w\d]{1}$"),
            class_=re.compile(r"^(\w{2}\s){2}\w{2}$"),
            role="article"
        )

        link_div = self.page.find(config.DIV, id=config.div_id_link)
        if link_div:
            link = link_div.find(config.A).get(config.HREF)
        else:
            link = ""
        print(f"LINK: {link}")

        return post_divs, link


class PagesFacebook(SearchObject):

    def __init__(self, html):
        super().__init__(html)

    def get_posts(self):
        """
        Get user page. Return all available posts from this range of month.
        Return info

        :param userpage: str - html page
        :param timedelta: - tuple of datetime.date
        :return:
            posts - list of dicts
            link - link for next page of posts in requirede

        """

        posts_root = self.page.find(config.DIV, id="BrowseResultsContainer")
        # try:
        #     posts_area = posts_root.find(config.DIV, id=config.div_id_recent)
        posts_area = posts_root
        # except AttributeError:
        #     with open("jbjjln.html", "w", encoding="utf-8") as f:
        #         f.write(str(self.page))
        #     raise Exception

        if not posts_area:
            return list(), ""

        post_divs = posts_area.find_all(
            "table",
            role="presentation"
        )

        try:
            link_tag = posts_area.find("div", id="see_more_pager")
            if link_tag:
                link = link_tag.find("a")["href"]
            else:
                link = ""
        except AttributeError:
            link = ""

        return post_divs, link