# -*- coding: utf-8 -*-

class CannotGetFeedSite(BaseException):
    def __init__(self, url):
        self.msg = "can not get rss feed link from %s" % url 

    def __repr__(self):
        return self.msg
