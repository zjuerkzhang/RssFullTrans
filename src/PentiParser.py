#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser
import os

class PentiParser(WebParser):
    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            return entry
        r.encoding = 'gb2312'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            #print "fail to bs"
            return entry
        div = html.find('table', attrs={'class': 'ke-zeroborder', 'style': 'table-layout:fixed;word-break:break-all;'})
        if div == None:
            return entry
        scripts = div.find_all('script')
        for s in scripts:
            s.decompose()
        inses = div.find_all('ins')
        for ins in inses:
            ins.decompose()
        entry['description'] = div.prettify()
        #print entry['title']
        #print ' '.join(map(lambda x:'%d' % x, entry['published']))
        return entry

    def __fetch_entry_from_node_a(self, a):
        if a == None:
            return None
        if a['href'] != None and a.string != None:
            re_found = re.search('\d{8}', a.string)
            if re_found == None:
                return None
            ts_str = a.string[re_found.start():re_found.end()]
            if len(ts_str) == 8:
                published = [int(ts_str[:4]), int(ts_str[4:6]), int(ts_str[6:]), 0, 0, 0]
            else:
                published = None
            return {
            'title': a.string,
            'link': '/'.join(self.url.split('/')[:-1]) + '/' + a['href'],
            'published': published,
            'description': a.string
            }
        else:
            return None

    def get_abstract_feed(self):
        feed = {
            'title': 'Penti News',
            'link': self.url,
            'description': 'Penti News',
            'entries': []
        }
        r = self.httpClient.get(self.url)
        if r.status_code != 200:
            return feed
        r.encoding = 'gb2312'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return feed
        lis = html.find_all('li')
        for li in lis:
            a = li.find('a')
            entry = self.__fetch_entry_from_node_a(a)
            if entry != None:
                feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    self_dir = os.path.dirname(os.path.abspath(__file__))
    feed_info = {}
    feed_info['url'] = 'http://www.dapenti.com/blog/blog.asp?subjectid=70&name=xilei'
    feed_info['name'] = 'PentiNews'
    feed_info['keywords'] = []
    feed_info['update'] = '20190300000000'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = self_dir + '/../log/log.log'
    feed_info['subPages'] = []
    parser = PentiParser(feed_info)
    feed_data = parser.parse()
    print ' '*1 + 'feed_title: ' + feed_data['title']
    print ' '*1 + 'entries: '
    for entry in feed_data['entries']:
        print ' '*3 + 'entry_link: ' + entry['link']
        print ' '*3 + 'entry_title: ' + entry['title']
        print ' '*3 + 'entry_des: ' + entry['description']
        print ' '*3 + 'published: ' + datetime.date.isoformat(entry['pubDate'])

