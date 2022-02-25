#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class YiqingParser(WebParser):
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
            self.debug_print("$$$ No valid response " + entry['title'] + ' ' + entry['link'])
            return entry
        r.encoding = 'utf-8'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry
        mainDiv = html.find('div', attrs={'class': 'article oneColumn pub_border'})
        time_div = mainDiv.find('div', attrs={'class': 'pages-date'})
        if time_div == None or len(time_div.contents) == 0:
            self.debug_print("$$$ No valid timestamp " + entry['title'] + ' ' + entry['link'])
            return entry
        timeStr = time_div.contents[0].strip()
        #self.debug_print("DEBUG: [%s] at %s" % (entry['title'], timeStr))
        beijing_time = self.translate_timestamp(timeStr)
        beijing_time.append(8)
        entry['published'] = timestamp_utils.adjustTimeByTimezon(*beijing_time)
        txt_div = mainDiv.find('div', attrs={'class': 'pages_content'})
        if txt_div != None:
            entry['description'] = txt_div.prettify()
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': 'Yiqing News',
            'link': self.url,
            'description': 'Yiqing News',
            'entries': []
        }
        r = self.httpClient.get(self.url)
        if r.status_code != 200:
            return feed
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html5lib')
        div = soup.find('div', attrs={'class': 'news_box'})
        if div == None:
            return feed
        lis = div.find_all('li')
        for li in lis:
            a = li.find('a', attrs = {'target': '_blank'})
            if a == None:
                continue
            entry = {
                'title': a.string,
                'link': self.host + a['href'],
                'published': None,
                'description': a.string
            }
            feed['entries'].append(entry)
        return feed


if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'http://www.gov.cn/fuwu/fwtj.htm'
    feed_info['name'] = 'YiqingNews'
    feed_info['keywords'] = ['新型冠状病毒肺炎疫情最新情况', '疫情防控最新消息']
    feed_info['subPages'] = []
    feed_info['update'] = '20220112011400'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = YiqingParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']

