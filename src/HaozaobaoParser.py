#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class HaozaobaoParser(WebParser):

    def get_full_description(self, entry):
        if entry['published'] == None:
            entry['published'] = [1970, 1, 1, 0, 0, 0]
        r = self.getHttpResponseViaProxy(entry['link'])
        if r.status_code != 200:
            self.debug_print("$$$ No valid response " + entry['title'] + ' ' + entry['link'])
            return entry
        r.encoding = 'gb2312'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry
        contentDiv = html.find('div', attrs = {'class': 'content'})
        if contentDiv != None:
            scriptElems = contentDiv.find('script')
            for e in scriptElems:
                e.decompose()
            inses = contentDiv.find('ins')
            for ins in inses:
                ins.decompose()
            entry['description'] = contentDiv.prettify()
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': 'Haozaobao News',
            'link': self.url,
            'description': 'Haozaobao News',
            'entries': []
        }
        if self.subPage_flag:
            sub_pages = map(lambda x: {'path': x, 'count': 10}, self.subPages)
        else:
            return feed

        for page in sub_pages:
            url = self.url + page['path']
            r = self.getHttpResponseViaProxy(url)
            if r.status_code != 200:
                continue
            #r.encoding = "gb2312"
            html = BeautifulSoup(r.text, 'html5lib')
            if html == None:
                continue
            ul = html.find('ul', attrs = {'class': 'e2'})
            if ul == None:
                self.debug_print("$$$ No valid <ul class='e2'> in [%s]" % url)
                continue
            lis = ul.find_all('li')
            for li in lis:
                titleA = li.find('a', attrs = {'class': 'title'})
                if titleA == None:
                    continue
                entry = {
                    'title': titleA.string,
                    'link': '/'.join(self.url.split('/')[:3]) + titleA['href'],
                    'published': [1970, 1, 1, 0, 0, 0],
                    'description': titleA.string
                }
                span = li.find('span', attrs = {'class': 'info'})
                if span != None:
                    for content in list(span.contents):
                        if not isinstance(content, str):
                            continue
                        matchedObj = re.search('^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})$', content.strip())
                        if not matchedObj:
                            continue
                        timeIntList = list(map(lambda x: int(x) ,list(matchedObj.groups())))
                        timeIntList.append(8)
                        entry['published'] = timestamp_utils.adjustTimeByTimezon(*timeIntList)
                feed['entries'].append(entry)
        return feed


if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://www.haozaobao.com/plus/list.php?tid='
    feed_info['name'] = 'HaozaobaoNews'
    feed_info['keywords'] = []
    feed_info['subPages'] = ['4', '17']
    feed_info['proxy'] = 'http://127.0.0.1:8080'
    feed_info['update'] = '20200106011400'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = HaozaobaoParser(feed_info)
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

