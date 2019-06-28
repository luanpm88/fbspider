from bs4 import BeautifulSoup

import config


class HTMLScanner(BeautifulSoup):

    def __init__(self, html):
        super().__init__(html, config.html_parser)
