#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
import requests
from bs4 import BeautifulSoup
from WebParser import WebParser

class CctvNewsParser(WebParser):
    def get_full_description(self, entry):
        r = requests.get(entry['link'])
        if r.status_code != 200:
            return entry
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            #print "fail to bs"
            return entry
        div = html.find('div', attrs={'class': 'col-md-8 col-sm-12'})
        if div == None:
            return entry
        scripts = div.find_all('script')
        for s in scripts:
            s.decompose()
        inses = div.find_all('ins')
        for ins in inses:
            ins.decompose()
        entry['description'] = div.prettify()
        return entry

    def __fetch_entry_from_node_tr(self, tr):
        if tr == None:
            return None
        a = tr.find('a')
        if a != None and a['href'] != None:
            re_found = re.search('\d{8}', a['href'])
            ts_str = a['href'][re_found.start():re_found.end()]
            if len(ts_str) == 8:
                published = [int(ts_str[:4]), int(ts_str[4:6]), int(ts_str[6:]), 0, 0, 0]
            else:
                published = None
            return {
            'title': a.string,
            'link': '/'.join(self.url.split('/')[:-2]) + a['href'],
            'published': published,
            'description': a.string
            }
        else:
            return None

    def get_abstract_feed(self):
        feed = {
            'title': 'CCTV News',
            'link': self.url,
            'description': 'CCTV News',
            'entries': []
        }
        r = requests.get(self.url)
        if r.status_code != 200:
            return feed
        #r.encoding = 'gb2312'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return feed
        table = html.find("table", attrs={'class': 'table table-bordered'})
        if table == None:
            return feed
        trs = table.find_all('tr')
        for tr in trs:
            entry = self.__fetch_entry_from_node_tr(tr)
            if entry != None:
                feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://cn.govopendata.com/xinwenlianbo/'
    feed_info['name'] = 'CctvNews'
    feed_info['keywords'] = []
    feed_info['update'] = '20190300000000'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = CctvNewsParser(feed_info)
    feed_data = parser.parse()
    print ' '*1 + 'feed_title: ' + feed_data['title']
    print ' '*1 + 'entries: '
    for entry in feed_data['entries']:
        print ' '*3 + 'entry_link: ' + entry['link']
        print ' '*3 + 'entry_title: ' + entry['title']
        print ' '*3 + 'entry_des: ' + entry['description']
        print ' '*3 + 'published: ' + datetime.date.isoformat(entry['pubDate'])

