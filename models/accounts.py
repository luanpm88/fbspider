import re
from models import post
import config
from bs4 import BeautifulSoup
import bs4.element


class Account(post.PostFacebook):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.soup = BeautifulSoup

    def user_posts(self, userpage, timedelta):
        """
        Get user page. Return all available posts from this range of month.
        Return info

        :param userpage: str - html page
        :param timedelta: - tuple of datetime.date
        :return:
            posts - list of dicts
            link - link for next page of posts in requirede

        """
        posts = list()

        html = self.soup(userpage, config.html_parser)
        if "Page Not Found" in html.head.title.get_text():
            return list(), ""

        try:

            link_tag = html.find("div", id="recent").next_sibling.find("a")
            if link_tag:
                link = link_tag["href"]
            else:
                link = ""
        except AttributeError:
            link = ""


        # Find area with list of user posts
        post_area = html.find("div", id="recent")
        if not post_area:
            return posts, ""
        post_area = list(post_area.children)[0]

        # Iterate over every post
        post_divs = list(post_area.children)[0].find_all("div", recursive=False)
        for post in post_divs:
            # Take date
            date = post.find("abbr")
            if date:
                # Some posts doesn't have date
                date_iso = self.get_iso_date(date.get_text())
            else:
                date_iso = ""

            date_validation = self.validate_date(date_iso, timedelta)
            if date_validation is "break":
                link = ""
                break
            elif date_validation is "skip":
                continue

            # Take post body
            # TODO Add full text for long post
            content = self._get_post_content(post)

            # Get amount of likes and link to comments
            info_div = list(list(post.children)[-1].children)
            info = [i for i in info_div[-1].find_all("a")]

            likes = info[0].get_text()
            try:
                post_link = info[-2]["href"]
            except IndexError:
                with open("test.html", "w", encoding="utf-8") as f:
                    f.write(str(info))
                    # raise error to search for new tag and add to config
                raise ValueError("Check html")

            # In case of "shared link"
            if not content:
                content = post.find_all("a")[2]["href"]

            comments = self._comments(post)
            loc_href = self._location()

            author_id, author_name, author_img_src = self._author_info(post)

            # In case of "shared link"

            posts.append({
                "Author Id": author_id,
                "Author Name": author_name,
                "Author Image Url": author_img_src,
                "ISO Code": "",
                "ISO Area": "",
                "ISO HREF": loc_href,

                "Comment Count": comments,
                "Post Data": content,
                "Publication Date": str(date_iso),
                "Like Count": likes,
                "Link": f"https://www.facebook.com{post_link}",
            })
            print("POST: ", {
                "Post Data": content,
                "Publication Date": str(date_iso),
                "Like Count": likes,
                "Link": post_link
            })

        return posts, link

    def _comments(self, fpost):
        info_div = list(list(fpost.children)[-1].children)[-1]
        comments_area = info_div.find_all(
            config.A,
            class_=[re.compile(r"^[a-zA-Z]{2}(?![\w\s])$")]
        )
        comments = [a.contents for a in comments_area if len(a.get("class")) == 1]

        if not comments:
            return 0
        elif not comments[0]:
            return 0
        print("COMMENTS: ", comments)
        comments_search = re.search(r"\d+", comments[0][0])
        if not comments_search:
            return 0

        return int(comments_search.group())

    def _author_info(self, p):
        # print("POST: ", str(self.post))
        # print("TABLE: ", str(self.post.find("table", class_=re.compile(r"^\w{1,2}$"))))
        # print("STRONG: ", str(self.post.find("table", class_=re.compile(r"^\w{1,2}$")).find("strong")))
        # print("STRONG: ", str(self.post.find("table", class_=re.compile(r"^\w{1, 2}$")).find("strong")))

        author = p.find("table", class_=re.compile("^\w{1,2}$")).find("strong").find("a")
        # TODO AUTHOR NAME RETURN TAG
        author_name = author.contents[0]
        if isinstance(author_name, bs4.element.Tag):
            author_name = author_name.get_text()
        return author["href"], author_name, ""

    def _get_post_content(self, post):
        full_content = [p.get_text() for p in post.find_all("p")]
        return " ".join(full_content)
