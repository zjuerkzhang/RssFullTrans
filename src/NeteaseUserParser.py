#-*- coding: UTF-8 -*-
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class NeteaseUserParser(WebParser):
    def translate_timestamp(self, timeStr):
        if re.match('\d{4}\-\d{2}\-\d{2}\s+\d{2}:\d{2}:\d{2}', timeStr) != None:
            [date_str, time_str] = timeStr.split(' ')
            date_array = date_str.split('-')
            year = int(date_array[0])
            month = int(date_array[1])
            day = int(date_array[2])
            time_array = time_str.split(':')
            hh = int(time_array[0])
            mm = int(time_array[1])
            ss = int(time_array[2])
            return [year, month, day, hh, mm, ss]
        return None


    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            self.debug_print("$$$ No valid response " + entry['title'] + ' ' + entry['link'])
            return entry
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry
        div = html.find('div', attrs={'class': 'post_body'})
        if div == None:
            self.debug_print("$$$ No valid content " + entry['title'] + ' ' + entry['link'])
            return entry
        entry['description'] = div.prettify()
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': 'PengPai News',
            'link': self.url,
            'description': 'PengPai News',
            'entries': []
        }

        for page in self.subPages:
            url = self.url + page
            r = self.httpClient.get(url)
            if r.status_code != 200:
                continue
            html = BeautifulSoup(r.text, 'html5lib')
            if html == None:
                continue
            divs = html.find_all('div', attrs={'class', 'media_article_content'})
            if len(divs) < 1:
                self.debug_print("No <div> of class 'media_article_content' found from [%s]" % url)
                continue
            div = divs[0]
            a = div.find('a')
            if a == None:
                self.debug_print("No <a> under div of 'media_article_content' in [%s]" % url)
                continue
            entry = {
                'title': a.string,
                'link': a['href'],
                'published': timestamp_utils.adjustTimeByTimezon(1970, 1, 1, 0, 0, 0, 8),
                'description': a.string
            }
            p = div.find('p', attrs = {'class': 'media_article_date'})
            if p != None:
                bjTime = self.translate_timestamp(p.string)
                bjTime.append(8)
                entry['published'] = timestamp_utils.adjustTimeByTimezon(*bjTime)
            feed['entries'].append(entry)
        print(feed)
        return feed


if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://www.163.com/dy/media/'
    feed_info['name'] = 'NeteaseUser'
    feed_info['keywords'] = []
    feed_info['subPages'] = ['T1604148115540.html']
    feed_info['update'] = '20200106011400'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = NeteaseUserParser(feed_info)
    feed_data = parser.get_abstract_feed()
    for entry in feed_data['entries']:
        entry = parser.get_full_description(entry)
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']

