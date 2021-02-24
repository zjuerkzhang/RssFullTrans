#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class GuanchaParser(WebParser):
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
        if entry['published'] == None:
            entry['published'] = [1970, 1, 1, 0, 0, 0]
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            return entry
        r.encoding = 'utf-8'
        pattern = re.compile('!wap\.jpg\"') # fix the img node
        new_text = pattern.sub('">', r.text)
        html = BeautifulSoup(new_text, 'html5lib')
        if html == None:
            return entry
        textPage = html.find('section', attrs={'class': 'textPageContInner'})
        if textPage == None:
            return entry
        h1s = textPage.find_all('h1')
        for h1 in h1s:
            h1.decompose()
        entry['description'] = textPage.prettify()
        time_span = textPage.find('span', attrs={'class': 'time'})
        timestamp_str = ''
        if time_span != None:
            if re.match('\d{4}\-\d{2}\-\d{2}\s+\d{2}:\d{2}', time_span.string.strip()) != None:
                timestamp_str = time_span.string.strip()
        if timestamp_str != '':
            beijing_time = self.translate_timestamp(timestamp_str)
            beijing_time.append(8)
            entry['published'] = timestamp_utils.adjustTimeByTimezon(*beijing_time)
        #print entry['title']
        #print ' '.join(map(lambda x:'%d' % x, entry['published']))
        return entry

    def __fetch_entry_from_node_a(self, a):
        if a == None:
            return None
        h3 = a.find('h3')
        if a['href'] != None and h3 != None:
            #print(h3.string)
            return {
            'title': h3.string,
            'link': self.url + a['href'],
            'published': None,
            'description': h3.string
            }
        else:
            return None

    def get_abstract_feed(self):
        feed = {
            'title': 'Guancha News',
            'link': self.url,
            'description': 'Guancha News',
            'entries': []
        }
        r = self.httpClient.get(self.url)
        if r.status_code != 200:
            return feed
        r.encoding = 'utf-8'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return feed
        headline = html.find('li', attrs={'class': 'headline'})
        if headline != None:
            a = headline.find('a')
            entry = self.__fetch_entry_from_node_a(a)
            if entry != None:
                feed['entries'].append(entry)
        box_rights = html.find_all('div', attrs={'class': 'box-right'})
        for br in box_rights:
            a_s = br.find_all('a')
            for a in a_s:
                entry = self.__fetch_entry_from_node_a(a)
                if entry != None:
                    feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://m.guancha.cn/'
    feed_info['name'] = 'GuanchaNews'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = GuanchaParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        #print ' '*3 + 'entry_des: ' + entry['description']
        #print ' '*3 + 'published: ' + entry['pubDate']

