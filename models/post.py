import datetime
import re
from urllib.parse import urlparse
from urllib.parse import parse_qs

from uuid import uuid4

import bs4.element

import config
from models import html_processor


class PostFacebook(object):

    def __init__(self, tag):
        self.post = tag
        # self.post = html_processor.HTMLScanner(tag)

    def __str__(self):
        return str(self.post)

    @property
    def footer(self):
        return self._get_footer()

    def _get_footer(self):
        info_div = list(list(self.post.children)[-1].children)
        info = [i for i in info_div[-1].find_all("a")]
        return info

    def _get_post_content(self):
        full_content = [p.get_text() for p in self.post.find_all("p")]
        if not full_content:
            try:
                full_content = self.post.find_all("a")[2]["href"]
            except IndexError:
                full_content = self.post.find("table").get_text()
                return full_content

        str_full_content = " ".join(full_content)
        return str_full_content

    def _likes(self):
        try:
            likes_pointer = self.footer[0].get_text()
        except IndexError:
            print(f"LIKES IndexError {self.footer}")
            return 0
        try:
            likes = int(likes_pointer)
        except ValueError:
            print(f"LIKES ValueError {likes_pointer}")

            likes_pointer = likes_pointer.split(",")
            try:
                likes = likes_pointer[0] * 1000 + likes_pointer[1]
            except IndexError:
                likes = 0
        return likes

    def _link(self):
        try:
            if self.footer[-1].get_text() != "Full Story":
                post_link = self.footer[-2]["href"]
            else:
                post_link = self.footer[-1]["href"]

            if not post_link:
                raise ValueError("NO LINK")
        except IndexError:
            # post_link = ""
            with open("test_link.html", "w", encoding="utf-8") as f:
                f.write(str(self.post))
                # raise error to search for new tag and add to config
            raise ValueError("PostFacebook _link Check html")

        if "/reaction/" in post_link:
            return ""

        return post_link

    @staticmethod
    def get_iso_date(post_date):
        HOURS = 24
        MINUTES = 60

        date_other_year = re.match(r"\d{1,2} ([A-Za-z])+ \d{4}\sat\s\d{2}:\d{2}", post_date)
        date_this_year_1 = re.match(r"(\d{1,2} [A-Za-z]+\sat\s\d{2}:\d{2})", post_date)
        date_short = re.match(r"(\d{1,2} [A-Za-z]+ \d{4})", post_date)

        # Default values
        seconds = 0
        minutes = 0
        hours = 0
        day = datetime.datetime.now().day
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year

        if date_this_year_1:
            date_time_set = date_this_year_1.group().split(" at ")
            date_set = date_time_set[0].split(" ")
            time_set = date_time_set[1].split(":")

            minutes = int(time_set[1])
            hours = int(time_set[0])
            day = int(date_set[0])
            month = int(config.months.get(date_set[1]))

        elif "hr" in post_date:
            # Pattern "1 hr"

            post_hours= int(post_date.split(" ")[0])
            hours = (datetime.datetime.now().hour - post_hours) % HOURS

        elif "min" in post_date:
            # Pattern "18 mins"

            post_minutes = int(post_date.split(" ")[0])
            minutes = (datetime.datetime.now().minute - post_minutes) % MINUTES
            hours = datetime.datetime.now().hour

        elif "Yesterday" in post_date:
            post_date = post_date.replace("PM", "")
            post_date = post_date.replace("AM", "")
            # Yesterday at 04:42

            date_time_set = post_date.split(" at ")
            time_set = date_time_set[1].split(":")
            minutes = int(time_set[1])
            hours = int(time_set[0])
            if day != 1:
                day -= 1

        elif date_other_year:
            date_time_set = date_other_year.group().split(" at ")
            date_set = date_time_set[0].split(" ")
            time_set = date_time_set[1].split(":")

            seconds = 0
            minutes = int(time_set[1])
            hours = int(time_set[0])
            day = int(date_set[0])
            month = int(config.months.get(date_set[1]))
            year = int(date_set[2])

        elif date_short:
            date_time_set = date_short.group().split(" ")

            day = int(date_time_set[0])
            month = int(config.months.get(date_time_set[1]))
            year = int(date_time_set[2])

        else:
            print(f"Wrong date format: {post_date}")

        date = datetime.datetime(year, month, day, hours, minutes, seconds)

        return date

    def _date(self):
        # Take date
        date = self.post.find("abbr")
        if date:
            # Some posts doesn't have date
            date_iso = self.get_iso_date(date.get_text())
        else:
            date_iso = ""
        return date_iso

    def _comments(self):
        info_div = list(list(self.post.children)[-1].children)[-1]
        comments_area = info_div.find_all(
            config.A,
            class_=[re.compile(r"^[a-zA-Z]{2}(?![\w\s])$")]
        )
        comments = [a.contents for a in comments_area if len(a.get("class")) == 1]

        if not comments:
            return 0
        elif not comments[0]:
            return 0
        elif not comments[0][0]:
            return 0

        comments_search = re.search(r"\d+", comments[0][0])

        if not comments_search:
            return 0

        return int(comments_search.group())

    def _location(self):
        date = self.post.find("abbr")
        try:
            tag = date.next_sibling.next_sibling
            if tag.name == "a":
                return tag["href"]
        except (AttributeError, KeyError):
            return ""

    def _author_info(self):
        author = self.post.find("table", class_=re.compile("^\w{1,2}$")).find("strong").find("a")
        # TODO AUTHOR NAME RETURN TAG
        author_name = author.contents[0]
        if isinstance(author_name, bs4.element.Tag):
            author_name = author_name.get_text()
        return author["href"], author_name, ""

    def info(self, timedelta=None):
        date_iso = self._date()

        # TODO Add full text for long post
        content = self._get_post_content()
        if content:
            likes = self._likes()
            link = self._link()
            comments = self._comments()
            loc_href = self._location()

            author_id, author_name, author_img_src = self._author_info()

            # In case of "shared link"

            post_data = {
                "id": str(uuid4()),
                "post_data": content,
                "title": " ".join(content.split(" ")[:5]),
                "published_date": date_iso,
                "like_count": likes,
                "link": link,
                "comment_count": comments,
                "author_id": author_id,
                "author_name": author_name,
                "author_image_url": author_img_src,
                "iso_code": "",
                "iso_area": "",
                "post_type": "post",

                "platform": "facebook",
                "following": 0,
                "dislike_count": 0,
                "view_count": 0,
                "language": "",
                "sentiment": "",
            }

            if timedelta and date_iso:
                date_validation = self.validate_date(date_iso, timedelta)
                print(f"DATE: {date_iso} {timedelta} {date_validation}")
                if date_validation == "break":
                    print("date_validation is BREAK")
                    return {"break": True}

            return post_data
        return dict()

    @staticmethod
    def validate_date(post_date, timedelta):
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


class FullPagePostM(PostFacebook):

    def __init__(self, html):
        super().__init__(html)
        try:
            self.post = html_processor.HTMLScanner(html)
        except RecursionError:
            self.post = html_processor.HTMLScanner("")

    def _user_id(self, related_link):
        # TODO change to RegEx
        url_parsed = urlparse(f"https://www.facebook.com{related_link}")
        if url_parsed.path.startswith("/profile.php"):
            uid = parse_qs(url_parsed.query).get("id")[0]
        else:
            uid = url_parsed.path.replace("/", "")
        return uid

    def get_text(self):
        post_area = self.post.find("div", id="MPhotoContent")
        try:
            content = post_area.find("div", {"data-ft": False}).get_text()
        except AttributeError:
            content = self.post.find_all("p")
            content = " ".join([c.get_text() for c in content])

        # for tag in hashtags:
        #     search_res = re.search(re.escape(tag), re.escape(content), re.IGNORECASE)
        #     # print("search_res: ", search_res)
        #     if search_res:
        #         return content
        return content

    def get_comments(self):
        comments = []
        next_page_link_fields = ["/story.php?story_fbid", "id", "p"]

        comment_divs = self.post.find_all(
            "div",
            id=re.compile("^\d*$"),
            class_=re.compile("^\w{2}$")
        )

        next_page_link_div = self.post.find(
            "div",
            id=re.compile("^see_next_\d*$"),
            class_=re.compile("^\w{2}$")
        )

        if next_page_link_div:
            next_page_link = next_page_link_div.find("a")["href"]

        else:
            next_page_link = ""

        for c in comment_divs:
            if len(c.get("class")) > 1:
                continue

            like_count_tag = c.find(
                "a",
                attrs={
                    "class": re.compile("^\w{2} \w{2}$"),
                    "aria-label": re.compile("^\d? reaction[\w,]*")
                }
            )
            if like_count_tag:
                like_count = int(like_count_tag.get_text())
            else:
                like_count = 0

            comments.append(
                {
                    "title": c.find("h3").next_sibling.get_text(),
                    "author_name": c.find("h3").find("a").get_text(),
                    "author_id": self._user_id(c.find("h3").find("a")["href"]),
                    "post_type": "comment",
                    "post_data": c.find("h3").next_sibling.get_text().lower(),
                    "published_date": str(self.get_iso_date(c.find("abbr").get_text())),
                    "like_count": like_count,
                    "comment_count": 0,
                    "id": "",

                    "platform": "facebook",
                    "following": 0,
                    "dislike_count": 0,
                    "view_count": 0,
                    "language": "",
                    "sentiment": "",
                }
            )

        return comments, next_page_link


class LocationPage(object):

    def __init__(self, html):
        self.location_page = html_processor.HTMLScanner(html)

    def get_location(self):
        try:
            loc_str = self.location_page.find("h1").get_text()
        except AttributeError:
            loc_str = ""
        return loc_str


class PostFacebookDesktopPage(object):
    def __init__(self, html):
        self.post = html_processor.HTMLScanner(html)

    def get_shares(self):
        with open("full_post.html", "w", encoding="utf-8") as f:
            f.write(str(self.post))

        shares_a = self.post.find(
            "a",
            href=re.compile("^\/shares\/view[\?\w=&]*$")
        )
        shares_number = shares_a.get_text().split(" ")[0]
        if shares_number.isnumeric():
            return int(shares_number)
        return 0
