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

class GuanChaUserParser(WebParser):
    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'], headers = gHeaders)
        if r.status_code != 200:
            self.debug_print("$$$ No valid response " + entry['title'] + ' ' + entry['link'])
            return entry
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry

        div = html.find('div', attrs={'class': 'article-content'})
        if not div:
            return entry
        subsDivToRemove = div.find_all('div', attrs = {'class': 'user-box user-info-box article-bottom-user'})
        for d in subsDivToRemove:
            d.decompose()
        subsDivToRemove = div.find_all('div', attrs = {'author-article'})
        for d in subsDivToRemove:
            d.decompose()
        subsDivToRemove = div.find_all('div', attrs = {'share-box'})
        for d in subsDivToRemove:
            d.decompose()
        subsDivToRemove = div.find_all('div', attrs = {'article-expand-more'})
        for d in subsDivToRemove:
            d.decompose()
        subsDivToRemove = div.find_all('div', attrs = {'hot-topic-nav bottom-hot-topic-nav'})
        for d in subsDivToRemove:
            d.decompose()
        subsDivToRemove = div.find_all('div', attrs = {'open-app'})
        for d in subsDivToRemove:
            d.decompose()

        content = div.prettify()
        entry['description'] = content
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': 'GuanCha User Articles',
            'link': self.url,
            'description': 'GuanCha User Articles',
            'entries': []
        }

        for userId in self.subPages:
            url = self.url + userId
            r = self.httpClient.get(url, headers = gHeaders)
            if r.status_code != 200:
                continue
            jsdata = r.json()
            if "data" not in jsdata.keys() or "items" not in jsdata['data'].keys() or len(jsdata['data']['items']) <=0:
                continue
            publishTime = timestamp_utils.adjustTimeByTimezon(1970, 1, 1, 0, 0, 0, 8)
            timeStr = jsdata['data']['items'][0]['created_at']
            if timeStr.find('小时前') < 0 and timeStr.find('昨天') < 0:
                continue
            try:
                if timeStr.find('小时前') >=0:
                    hours = int(timeStr.strip().replace('小时前', ''))
                    pbBjT = datetime.datetime.today() + datetime.timedelta(hours = (0-hours))
                    publishTime = timestamp_utils.adjustTimeByTimezon(pbBjT.year, pbBjT.month, pbBjT.day, pbBjT.hour, 0, 0, 8)
                if timeStr.find('昨天') >= 0:
                    yesterdayTimeStr = timeStr.replace('昨天', '').strip()
                    hourMin = yesterdayTimeStr.split(':')
                    if len(hourMin) < 2:
                        continue
                    hour = int(hourMin[0])
                    minute = int(hourMin[0])
                    pbBjT = datetime.datetime.today() + datetime.timedelta(hours = -24)
                    publishTime = timestamp_utils.adjustTimeByTimezon(pbBjT.year, pbBjT.month, pbBjT.day, hour, minute, 0, 8)
            except:
                self.debug_print("$$$ Invalid publish date time [%s]" % timeStr)
                continue
            entry = {
                'title': jsdata['data']['items'][0]['title'],
                'link': jsdata['data']['items'][0]['post_url'],
                'published': publishTime,
                'description': jsdata['data']['items'][0]['summary']
            }
            feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    self_dir = os.path.dirname(os.path.abspath(__file__))
    feed_info = {}
    feed_info['url'] = 'https://user.guancha.cn/user/get-published-list?page_no=1&uid='
    feed_info['name'] = 'GuanChaUser'
    feed_info['subPages'] = ['794520']
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = self_dir + '/../config/config.xml'
    feed_info['log_file'] = self_dir + '/../log/log.log'
    parser = GuanChaUserParser(feed_info)
    feed_data = parser.get_abstract_feed()
    for entry in feed_data['entries']:
        entry = parser.get_full_description(entry)
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print(' '*3 + 'entry_content: ' + entry['content'])
        if entry['description'].find(chr(8))>=0:
            print("find \h")
