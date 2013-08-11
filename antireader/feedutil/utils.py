#-*- coding: utf-8 -*-

from HTMLParser import HTMLParser
from urllib2 import urlopen, Request

import re
import os
import urlparse


class FeedHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.has_found = False
        self.feed_url = None

    def handle_starttag(self, tag, attrs):
        if tag == 'link' and self.has_found == False:
            names = [val[0] for val in attrs]
            values = [val[1] for val in attrs]
            if 'type' in names:
                type_index = names.index('type')
                val = values[type_index]
                if ('rss' in val) or ('atom' in val):
                    href_index = names.index('href')
                    self.feed_url = values[href_index]
                    self.has_found = True

    def handle_data(self, data):
        pass

def pretreate_html(html):
    # remove all suck tags in html'
    re_judge1 = re.compile('<!-*[^>]*>') # remove brower judgement
    tmp1 = re_judge1.sub('', html)
    tmp2 = tmp1.replace('<![endif]–>', '') 
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)
    result = re_script.sub('', tmp2)
    return result

def check_if_feed_link(url):
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686)' + 
            'Gecko/20071127 Firefox/2.0.0.11')
    try:
        response = urlopen(request)
        res_info = response.info()
        content_type = res_info.getheaders('content-type')
        if 'xml' in content_type or 'feed' in url or 'rss' in url or 'atom' in url:
            return True
        return False
    except:
        return False


def get_feed_link(url):
    if not url.startswith('http://'):
        url = 'http://' + url
    if check_if_feed_link(url):
        return url

    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686)' + 
            'Gecko/20071127 Firefox/2.0.0.11')
    try:
        connection = urlopen(request)
    except:
        return None
    html = connection.read()
    html = pretreate_html(html)
    parser = FeedHtmlParser()
    try:
        #print 'use utf8'
        parser.feed(html.decode('utf-8'))
    except:
        #print 'error in utf8'
        try:
            #print 'use gb2312'
            parser.feed(html.decode('gb2312'))
        except:
            try:
                #print 'use gbk'
                parser.feed(html.decode('gbk'))
            except:
                pass

    if parser.feed_url:
        feed_url = parser.feed_url
        if 'feedburner' in feed_url: # it use feed burner, change to raw xml
            feed_url = feed_url + '?fmt=xml'
            return feed_url
        elif feed_url.startswith('/'):
            p = urlparse.urlparse(url)
            url = 'http://' + p.hostname
            feed_url = os.path.join(url, feed_url[1:])
        return feed_url
    else:
        return None


if __name__ == '__main__':
    link = raw_input("Please input a link: ")
    url = get_feed_link(link)
    if url is not None:
        print url
    else:
        print 'can not find rss url'
