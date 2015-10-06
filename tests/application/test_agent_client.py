import json
from urllib import parse
from tornado.testing import AsyncHTTPTestCase
from application.server import Application


class TestAgentRequest(AsyncHTTPTestCase):

    def get_app(self):
        app = Application()
        app.settings["xsrf_cookies"] = False  # invalidate xsrf to test
        return app

    def test_suggest(self):
        params = {
            "candidate_id": 0,
            "is_like": "true"
        }

        body = parse.urlencode(params)
        response = self.fetch("/agent/12345/train",
                          method="POST", body=body)

        result = json.loads(response.body.decode("utf-8"))
        self.assertTrue("candidates" in result)

        for c in result["candidates"]:
            self.assertTrue("city" in c)
            self.assertTrue("spots" in c)
            self.assertTrue("tours" in c)
            print("{0}: spots={1}, tours={2}".format(c["city"]["code"], len(c["spots"]), len(c["tours"])))
