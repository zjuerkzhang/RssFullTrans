#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser
from requestsWrapper import requestsWrapper

class ClTechParser(WebParser):
    def translate_timestamp(self, timeStr):
        if re.match('\d{4}\-\d{2}\-\d{2}\s+\d{2}:\d{2}', timeStr) != None:
            [date_str, time_str] = timeStr.split(' ')
            date_array = date_str.split('-')
            year = int(date_array[0])
            month = int(date_array[1])
            day = int(date_array[2])
            time_array = time_str.split(':')
            hh = int(time_array[0])
            mm = int(time_array[1])
            ss = 0
            return [year, month, day, hh, mm, ss]
        return None


    def get_full_description(self, entry):
        r = self.clHttpClient.get(entry['link'])
        if r.status_code != 200:
            self.debug_print("$$$ No valid response " + entry['title'] + ' ' + entry['link'])
            return entry
        r.encoding = 'gbk'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry
        div = html.find('div', attrs = {'class': 'tpc_cont'})
        if div == None:
            self.debug_print("$$$ No valid div " + entry['title'] + ' ' + entry['link'])
            return entry
        divs = div.find_all('div')
        for d in divs:
            d.decompose()
        imgs = div.find_all('img')
        for i in imgs:
            if 'ess-data' in i.attrs.keys():
                i.attrs = {'src': i.attrs['ess-data']}
                continue
        entry['description'] = div.prettify()
        return entry

    def __convert_time_from_str_to_int_array(self, s):
        return [int(s[:4]), int(s[4:6]), int(s[6:8]), int(s[8:10]), int(s[10:12]), 0]

    def __fetch_entry_from_node_a(self, a):
        if a == None or a['href'] == None or a.string == None:
            return None
        strArray = a.string.split(' ')
        if len(strArray) < 2:
            return None
        return {
            'title': ' '.join(strArray[1:]),
            'link': a['href'],
            'description': a.string,
            'published': self.__convert_time_from_str_to_int_array(strArray[0])
        }

    def get_abstract_feed(self):
        self.clHttpClient = requestsWrapper('t66y.com', baseDelay = 4, randomDelay = True, retryCount = 3)
        feed = {
            'title': 'Global News',
            'link': self.url,
            'description': 'Global News',
            'entries': []
        }
        r = self.httpClient.get(self.url)
        if r.status_code != 200:
            return feed
        r.encoding = "utf-8"
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return feed
        a_s = html.find_all('a')
        for a in a_s:
            entry = self.__fetch_entry_from_node_a(a)
            if entry != None:
                feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://bloghz.ddns.net/j/static/caoliu/TechNews.html'
    feed_info['name'] = 'ClTechParser'
    feed_info['keywords'] = []
    feed_info['update'] = '20210519011400'
    feed_info['subPages'] = []
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = ClTechParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        #print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']

