#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class MicroHistoryParser(WebParser):
    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            return entry
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            #print "fail to bs"
            return entry
        div = html.find('div', attrs={'class': 'panel-pane pane-node-body'})
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

    def __fetch_entry_from_node_li(self, li):
        if li == None:
            return None
        a = li.find('a')
        if a == None:
            return None
        if a['href'] != None and a.string != None:
            span = li.find('span', attrs={'class', 'views-field views-field-created'})
            published = None
            if span != None:
                date_span = span.find('span', 'field-content')
                if date_span != None and date_span.string != None:
                    date_strs = date_span.string.split('/')
                    if len(date_strs) >= 3:
                        published = [2000+int(date_strs[0]), int(date_strs[1]), int(date_strs[2]), 0, 0, 0]
            return {
                'title': a.string,
                'link': '/'.join(self.url.split('/')[:3]) + a['href'],
                'published': published,
                'description': a.string
            }
        else:
            return None

    def get_abstract_feed(self):
        feed = {
            'title': 'Micro History News',
            'link': self.url,
            'description': 'Micro History News',
            'entries': []
        }
        r = self.httpClient.get(self.url)
        if r.status_code != 200:
            return feed
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return feed
        div = html.find('div', attrs={'class', 'content-middle'})
        if div == None:
            return feed
        view_div = div.find('div', attrs={'class', 'view-content'})
        if view_div == None:
            return feed
        lis = view_div.find_all('li')
        for li in lis:
            entry = self.__fetch_entry_from_node_li(li)
            if entry != None:
                feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://botanwang.com/taxonomy/term/11792'
    feed_info['name'] = 'MicroHistoryParser'
    feed_info['keywords'] = []
    feed_info['update'] = '20191000000000'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = MicroHistoryParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        print(' '*3 + 'published: ' + datetime.date.isoformat(entry['pubDate']))

