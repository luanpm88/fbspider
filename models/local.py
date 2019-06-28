from bs4 import BeautifulSoup

import config


class FacebookHTMLProcessor(object):

    def __init__(self):
        self.soup = BeautifulSoup

    def validate_login(self, data):
        """
        Function to validate response from POST login response.
        :param data: str - html page
        :return:
        """

        html = self.soup(data, config.html_parser)
        feed = html.find("div", id=config.id_feed)
        one_tap_login = html.find("h3")
        if feed or one_tap_login == "Log in with one tap":
            return True

        return False

    def get_login_hidden_data(self, data):
        html = self.soup(data, config.html_parser)
        hidden_fields = html.find_all("input", type="hidden")
        post_data = {tag["name"]: tag.get("value") for tag in hidden_fields}
        return post_data

    def validate_approve_page(self, data):
        """
        Function to validate response from POST login response. Facebook return
        page with 'Log in with one tap'
        :param data: str - html page
        :return: form: dict - hidden values found on this form
        """
        form = dict()

        html = self.soup(data, config.html_parser)
        submit_button = html.find_all("input")
        for field in submit_button:
            name = field.get("name", False)
            if name:
                form[name] = field.get("value", "")
        return form
