#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser
import os

gHeaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-Hans-CN,zh-CN;q=0.9,zh;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5,ja;q=0.4',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.53 Safari/537.36 Edg/80.0.361.33',
    'Connection' : 'keep-alive',
    'Cache-Control': 'no-cache',
    'Host': 'user.guancha.cn'
}

class GuanChaZhuanLanParser(WebParser):
    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            self.debug_print("$$$ No valid response " + entry['title'] + ' ' + entry['link'])
            return entry
        r.encoding = 'utf-8'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry

        h3s = html.find_all('h3')
        if len(h3s) == 1:
            entry['title'] = h3s[0].string

        div = html.find('div', attrs={'class': 'content all-txt'})
        if not div:
            return entry
        content = div.prettify()
        entry['description'] = content
        return entry

    def getEntryInfoFromLi(self, li):
        h4 = li.find('h4', attrs = {'class': 'module-title'})
        if h4 == None:
            self.debug_print("$$$ Fail to find <h4> in <li> [%s]" % li.prettify())
            return None
        a = h4.find('a')
        if a == None:
            self.debug_print("$$$ Fail to find <a> in <h4> [%s]" % h4.prettify())
            return None
        title = a['title'] if a.has_attr('title') else a.string
        entry = {
            'title': title,
            'link': a['href'],
            'published': timestamp_utils.adjustTimeByTimezon(1970, 1, 1, 0, 0, 0, 8),
            'description': title
        }
        div = li.find('div', attrs = {'class': 'module-interact'})
        if div == None:
            self.debug_print("INFO: no <div class='module-interact'> in <li> [%s]" % li.prettify())
            return entry
        span = div.find('span')
        if span == None:
            self.debug_print("INFO: no <span> in <div> [%s]" % div.prettify())
            return entry
        matchedObj = re.search('^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})$', span.string.strip())
        if matchedObj == None:
            self.debug_print("INFO: no time string in <span> [%s]" % span.prettify())
        timeIntList = list(map(lambda x: int(x) ,list(matchedObj.groups())))
        timeIntList.append(8)
        entry['published'] = timestamp_utils.adjustTimeByTimezon(*timeIntList)
        return entry

    def processArticleLink(self, link):
        targetLink = link if link.find(self.url) == 0 else self.url[:-1] + link
        strsByDot = targetLink.split('.')
        return '.'.join(strsByDot[:-1]) + '_s.' + strsByDot[-1]


    def get_abstract_feed(self):
        feed = {
            'title': 'GuanCha ZhuanLan Articles',
            'link': self.url,
            'description': 'GuanCha ZhuanLan Articles',
            'entries': []
        }
        for userId in self.subPages:
            url = self.url + userId
            r = self.httpClient.get(url)
            r.encoding = 'utf-8'
            if r.status_code != 200:
                self.debug_print("$$$ Fail to get web content from [%s]" % url)
                continue
            html = BeautifulSoup(r.text, 'html5lib')
            lis = html.find_all('li', attrs = {'class': 'borderNo'})
            for li in lis:
                entry = self.getEntryInfoFromLi(li)
                if entry != None:
                    entry['link'] = self.processArticleLink(entry['link'])
                    feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    self_dir = os.path.dirname(os.path.abspath(__file__))
    feed_info = {}
    feed_info['url'] = 'https://www.guancha.cn/'
    feed_info['name'] = 'GuanChaZhuanLanArticles'
    feed_info['subPages'] = ['XiJinPing', 'WenTieJun', 'ZhengYongNian', 'PaulKrugman', 'FuLangXiSi-FuShan']
    feed_info['keywords'] = []
    feed_info['update'] = '20220101000000'
    feed_info['conf_file'] = self_dir + '/../config/config.xml'
    feed_info['log_file'] = self_dir + '/../log/log.log'
    parser = GuanChaZhuanLanParser(feed_info)
    feed_data = parser.get_abstract_feed()
    for entry in feed_data['entries']:
        entry = parser.get_full_description(entry)
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        print(' '*3 + 'published: ' + '-'.join(list(map(lambda x:str(x), list(entry['published'])))))
        if entry['description'].find(chr(8))>=0:
            print("find \h")
