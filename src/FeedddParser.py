#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
import feedparser
from bs4 import BeautifulSoup
from WebParser import WebParser

class FeedddParser(WebParser):
    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            self.debug_print("$$$ No valid response %s [%s]" % (entry['title'], entry['link']))
            return entry
        soup = BeautifulSoup(r.text, 'html5lib')
        if soup == None:
            self.debug_print("$$$ No valid html %s [%s]" % (entry['title'], entry['link']))
            return entry
        div = soup.find('div', attrs = {'class': 'rich_media_content'})
        if div == None:
            self.debug_print("$$$: Fail to get content from %s [%s]" % (entry['title'], entry['link']))
            return entry
        tagsToRemoveStyle = ['span', 'p', 'em', 'section']
        for tag in tagsToRemoveStyle:
            elems = div.find_all(tag)
            for elem in elems:
                if elem.has_attr('style'):
                    del elem['style']
                #if elem.has_attr('style') and re.search('font-size:\s*\d+px;?', elem['style']) != None:
                #    elem['style'] = re.sub('font-size:\s*\d+px;?', '', elem['style'])
        content = div.prettify()
        content = content.replace("data-src", "src")
        content = re.sub('<p>\s*<br\s*/>\s*</p>', '', content)
        #print("%s|%s\n%s" % (wechatAuthor, title, content))
        entry['description'] = content
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': '微信公众号合集',
            'link': self.url,
            'description': '微信公众号合集',
            'entries': []
        }

        for page in self.subPages:
            url = self.url + page
            oneFeed = feedparser.parse(url)
            feedAuthor = "No Author"
            if oneFeed.has_key('feed') and oneFeed.feed.has_key('title'):
                feedAuthor = oneFeed.feed.title
            for oneEntry in oneFeed.entries:
                entry = {
                    'title': "%s | %s" % (feedAuthor, oneEntry.title),
                    'link': oneEntry.link,
                    'published': timestamp_utils.getTimeDecFromPubdate(oneEntry['published']),
                    'description': oneEntry.description
                }
                feed['entries'].append(entry)
        return feed


if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://api.feeddd.org/feeds/'
    feed_info['name'] = 'WechatUserArticles'
    feed_info['keywords'] = []
    feed_info['subPages'] = [
        '6131b5301269c358aa0dec42',
        '6131e1421269c358aa0e1cad',
        '62014453dca58a380c59c4be',
        '61285e90221f954f5e11175f',
        '6131e1421269c358aa0e1b6b'
    ]
    feed_info['update'] = '20220710011400'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = FeedddParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print(' '*3 + 'entry_content: ' + entry['content'])
        if entry['description'].find(chr(8))>=0:
            print("find \h")

