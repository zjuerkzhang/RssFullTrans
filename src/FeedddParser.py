#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
import feedparser
from bs4 import BeautifulSoup
from WebParser import WebParser
import requests

gUserId2RssFeedMap = [
    {
        "userId": '62014453dca58a380c59c4be',
        "rssUrls": [
            'http://192.168.119.47/rss/RSS_GuanChaUserArticles.xml',
            'https://bloghz.ddns.net/ppf/wechatRss.xml'
        ]
    },
    {
        "userId": '616102e99b888e41f5cb64fb',
        "rssUrls": ['http://192.168.119.47/rss/RSS_PengpaiUserArticlesForKindle.xml']
    }
]

def notifyWechatArticleFetchResult(msgText):
    jsonMsg = {
        'subject': '微信公众号转RSS',
        'channel': 'telegram|bark',
        'content': msgText
    }
    requests.post("https://bloghz.ddns.net/cmd/notify/", json = jsonMsg)

def getArticleTitlesFromAnotherRssSource(userId):
    titles = []
    userId2RssFeedPairs = list(filter(lambda x: x["userId"] == userId, gUserId2RssFeedMap))
    if len(userId2RssFeedPairs) == 0:
        return titles
    rssUrls = userId2RssFeedPairs[0]["rssUrls"]
    for url in rssUrls:
        anotherFeed = feedparser.parse(url)
        titlesInOneFeed = list(map(lambda x: x.title, anotherFeed.entries))
        titles.extend(titlesInOneFeed)
    return titles

class FeedddParser(WebParser):
    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            msgText = "No valid response from %s [%s]" % (entry['title'], entry['link'])
            self.debug_print(msgText)
            notifyWechatArticleFetchResult(msgText)
            return None
        soup = BeautifulSoup(r.text, 'html5lib')
        if soup == None:
            msgText = "No valid html from %s [%s]" % (entry['title'], entry['link'])
            self.debug_print(msgText)
            notifyWechatArticleFetchResult(msgText)
            return None
        copyrightLogo = soup.find('span', attrs = {'id': 'copyright_logo'})
        if copyrightLogo == None:
            self.debug_print("%s[%s] is not an article, maybe AD, so drop it" % (entry['title'], entry['link']))
            return None
        div = soup.find('div', attrs = {'class': 'rich_media_content'})
        if div == None:
            msgText = "Fail to get content from %s [%s]" % (entry['title'], entry['link'])
            self.debug_print(msgText)
            notifyWechatArticleFetchResult(msgText)
            return None
        tagsToRemoveStyle = ['span', 'p', 'em', 'section']
        for tag in tagsToRemoveStyle:
            elems = div.find_all(tag)
            for elem in elems:
                if elem.has_attr('style'):
                    del elem['style']
        content = div.prettify()
        content = content.replace("data-src", "src")
        content = re.sub('<p>\s*<br\s*/>\s*</p>', '', content)
        #print("%s|%s\n%s" % (wechatAuthor, title, content))
        entry['description'] = content
        notifyWechatArticleFetchResult("[%s] is added" % entry['title'])
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': '微信公众号合集',
            'link': self.url,
            'description': '微信公众号合集',
            'entries': []
        }

        for page in self.subPages:
            titlesFromOtherSource = getArticleTitlesFromAnotherRssSource(page)
            url = self.url + page
            oneFeed = feedparser.parse(url)
            feedAuthor = "No Author"
            if oneFeed.has_key('feed') and oneFeed.feed.has_key('title'):
                feedAuthor = oneFeed.feed.title
            for oneEntry in oneFeed.entries:
                if oneEntry.title in titlesFromOtherSource:
                    self.debug_print("%s[%s] exist in other source, so skip it" % (oneEntry.title, oneEntry.link))
                    continue
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
        '6131e1421269c358aa0e1b6b',
        '6131e1401269c358aa0e186f'
    ]
    feed_info['update'] = '20220811003432'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = FeedddParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        #print(' '*3 + 'entry_des: ' + entry['description'])
        #print(' '*3 + 'entry_content: ' + entry['content'])
        if entry['description'].find(chr(8))>=0:
            print("find \h")

