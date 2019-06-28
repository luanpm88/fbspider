import time
import config


class Web(object):

    def __init__(self, session):
        self.session = session
        self.header = config.headers

    def get(self, api, params=None, full=False):
        if full:
            url = api
        else:
            url = "{path}{api}".format(
                path=config.fb,
                api=api)

        if not params:
            params = dict()

        if "video_redirect" in url:
            return ""
        time.sleep(2)
        resp = self.session.get(url, params=params, headers=self.header)

        return resp.text

    def post(self, api, data):
        url = "{path}{api}".format(
            path=config.fb,
            api=api)

        resp = self.session.post(url, data=data)
        return resp.text
