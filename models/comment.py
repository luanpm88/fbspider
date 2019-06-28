

class CommentFacebook(object):

    def __init__(self):
        pass

    def _extract_comment_data(self, div):
        """

        :param div:
        :return:
        """
        childrens = list(div.children)[0]
        comment_conten = childrens.children
        # First 3 tags responsible for name, text content, attachment
        is_author = comment_conten.__next__()
        author = is_author.find("a")["href"]
        text = self._comment_text_processor(
            comment_conten.__next__()
        )

        attached = self._comment_attached_processor(
            comment_conten.__next__()
        )

        return author, text, attached

    def _comment_attached_processor(self, data):
        if not data:
            return "NOTHING"
        if data.find("table"):
            return "LINK"
        elif data.find("img", src=re.compile(r"post_page_comments[\w_\/]+\.png"), recursive=False):
            return "STICKER"
        elif data.find("a", href=re.compile(r"video_redirect/*")):
            return "VIDEO"
        elif data.find("a", href=re.compile(r"photo.php*")):
            return "PICTURE"
        elif data.find("img", class_=re.compile(r"^[a-z]{2} [a-z]{2} [a-z]$")):
            return "STICKER"
        else:
            print(f"data.children: {data}")
            return "OTHER"

    def _comment_text_processor(self, data):
        if data:
            return data.get_text()
        else:
            return ""
