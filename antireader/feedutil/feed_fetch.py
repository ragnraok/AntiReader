from utils import get_feed_link
from exception import CannotGetFeedSite

import feedparser
import locale
import datetime

class FeedData(object):
    def __init__(self, site, if_feed_link=False):
        self.site = site
        self.feed_url = None
        self.parser = None
        self.has_parser = False
        self.if_feed_link = if_feed_link

    def init_data(self):
        locale.setlocale(locale.LC_TIME, "en_US.UTF8")
        if not self.if_feed_link:
            feed_url = get_feed_link(self.site)
            if feed_url is None:
                raise CannotGetFeedSite(self.site)
            self.feed_url = feed_url
        else:
            self.feed_url = self.site
        self.parser = feedparser.parse(self.feed_url)

    @property
    def site_title(self):
        if 'title' in self.parser['channel']:
            return self.parser['channel']['title']
        elif 'subtitle' in self.parser['channel']:
            return self.parser['channel']['subtitle']

    @property
    def site_updated(self):
        """
        the latest update date, may be None, because some blog
        doesn't have updated key (Fuck!)
        """
        if 'updated' in self.parser['channel']:
            timestr = self.parser['channel']['updated']
            version = self.parser.version
            #print "timestr = %s" % timestr
            return self.__parse_timestr(version, timestr, self.site)
        elif 'published' in self.parser['channel']:
            timestr = self.parser['channel']['published']
            version = self.parser.version
            #print "timestr = %s" % timestr
            return self.__parse_timestr(version, timestr, self.site)
        else:
            #print "timestr is None"
            return None

    def __parse_timestr(self, version, timestr, url):
        if 'rss' in version:
            try:
                """
                for general situation
                timestr[:25] in this format:
                %a, %d %b %Y %H:%M:%S
                """
                return datetime.datetime.strptime(timestr[:25], "%a, %d %b %Y %H:%M:%S")
            except:
                # sucks situations
                if 'csdn.net' in url:
                    return datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
                elif '163.com' in url:
                    return datetime.datetime.strptime(timestr[:19], "%Y-%m-%dT%H:%M:%S")
                else:
                    """
                    in this format:
                        %Y-%m-%d %H:%M:%S
                    """
                    return datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        elif 'atom' in version:
            """
            for general situation
            timestr[:19] in this format:
            %Y-%m-%dT%H:%M:%S
            """
            return datetime.datetime.strptime(timestr[:19], "%Y-%m-%dT%H:%M:%S")


    @property
    def site_articles(self):
        """
        return an articles list in this format:
        [{'title': title,
            'link': link,
            'content': content in html format,
            'date': a datetime.datetime object}
        ,...]
        """
        if 'atom' in self.parser.version:
            item_list = self.parser['items']
            result = []
            for item in item_list:
                article = {}
                article['link'] = item['link']
                article['title'] = item['title']
                article['date'] = self.__parse_timestr(self.parser.version,
                        item['updated'], self.site)
                article['content'] = item['description']
                result.append(article)
            return result
        elif 'rss' in self.parser.version:
            item_list = self.parser['items']
            result = []
            for item in item_list:
                article = {}
                article['link'] = item['link']
                article['title'] = item['title']
                article['date'] = self.__parse_timestr(self.parser.version,
                        item['updated'], self.site)
                if 'content' in item:
                    article['content'] = item['content'][0]['value']
                elif 'summary' in item:
                    article['content'] = item['summary']
                elif 'description' in item:
                    article['content'] = item['description']
                result.append(article)
            return result


if __name__ == '__main__':
    # get a test
    site = raw_input("Please input a site: ")
    feed_data = FeedData(site)
    feed_data.init_data()
    print feed_data.feed_url
    print feed_data.site_title
    print feed_data.site_updated
    print feed_data.parser['channel']
    #for article in feed_data.site_articles:
    #    print article['title']
    #    print article['date']
    #    print article['link']
    #    #print article['content']
