# -*- coding: utf-8 -*-
import uuid
from datetime import datetime, timedelta
import urllib.parse as parse
import tornado.web


class GroupHandler(tornado.web.RequestHandler):
    """
    create the group to make the plan.
    Specifically, make unique url for group.
    """

    def post(self):
        """
        Create group url
        :return:
        """
        # create unique id
        group_id = uuid.uuid4().int & (1<<16)-1

        # selection filter to make plan (ex. budget)
        budget = int(self.get_argument("budget", "0"))

        _query = {
            "budget": budget,
        }
        query = parse.urlencode(_query)

        # create url
        url = '//{0}/agent/{1}?{2}'.format(self.request.host, group_id, query)
        response = {"url": url}
        return self.write(response)
