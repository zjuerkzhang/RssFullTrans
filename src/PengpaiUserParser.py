#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class PengpaiUserParser(WebParser):
    def translate_timestamp_str(self, timeStr):
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
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry
        time_div = html.find('div', attrs={'class': 'news_about'})
        if time_div == None:
            self.debug_print("$$$ No valid timestamp " + entry['title'] + ' ' + entry['link'])
            return entry
        ps = time_div.find_all('p')
        timestamp_str = ''
        for p in ps:
            if len(p.contents) > 0 and re.match('\d{4}\-\d{2}\-\d{2}\s+\d{2}:\d{2}', p.contents[0].strip()) != None:
                timestamp_str = p.contents[0].strip()
        if timestamp_str == '':
            self.debug_print("$$$ No valid time string " + entry['title'] + ' ' + entry['link'])
            return entry
        beijing_time = self.translate_timestamp_str(timestamp_str)
        beijing_time.append(8)
        entry['published'] = timestamp_utils.adjustTimeByTimezon(*beijing_time)
        news_path = ''
        path_div = html.find('div', attrs={'class': 'news_path'})
        if path_div != None:
            a_s = path_div.find_all('a')
            if len(a_s) > 0:
                news_path = path_div.prettify()
        txt_div = html.find('div', attrs={'class': 'news_txt'})
        nonDisplayElems = txt_div.find_all('audio', attrs = {'style': 'display: none;'})
        for elem in nonDisplayElems:
            elem.decompose()
        imgs = txt_div.find_all('img')
        for img in imgs:
            br = html.new_tag('br')
            img.insert_after(br)
        if txt_div != None:
            entry['description'] = news_path + '<br>' + txt_div.prettify()
        return entry

    def get_news_li_by_retry(self, url, retryLimit):
        retryCount = 0
        news_lis = []
        while retryCount < retryLimit:
            retryCount = retryCount + 1
            r = self.httpClient.get(url)
            if r.status_code != 200:
                continue
            html = BeautifulSoup(r.text, 'html5lib')
            if html == None:
                continue
            news_lis = html.find_all('div', attrs={'class', 'news_li'})
            if len(news_lis) == 0:
                self.debug_print("$$$ No <div class='news_li'> found in [%s], retry" % url)
                continue
            return news_lis
        return news_lis

    def get_abstract_feed(self):
        feed = {
            'title': 'PengPai News',
            'link': self.url,
            'description': 'PengPai News',
            'entries': []
        }
        if self.subPage_flag:
            sub_pages = map(lambda x: {'path': x, 'count': 2}, self.subPages)
        else:
            return feed

        for page in sub_pages:
            url = self.url + page['path']
            #print(url)
            '''
            r = self.httpClient.get(url)
            if r.status_code != 200:
                continue
            html = BeautifulSoup(r.text, 'html5lib')
            if html == None:
                continue
            news_lis = html.find_all('div', attrs={'class', 'news_li'})
            if len(news_lis) == 0:
                self.debug_print("$$$ No <div class='news_li'> found in [%s]" % url)
            if len(news_lis) > page['count']:
                news_lis = news_lis[:page['count']]
            '''
            news_lis = self.get_news_li_by_retry(url, 2)
            for li in news_lis:
                a = li.find('a', attrs = {'target': '_blank'})
                if a == None:
                    continue
                div = a.find('div', attrs = {'class': 'title'})
                if div == None:
                    continue
                entry = {
                    'title': div.string,
                    'link': self.url + a['href'],
                    'published': None,
                    'description': div.string
                }
                feed['entries'].append(entry)
        return feed


if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://www.thepaper.cn/'
    feed_info['name'] = 'PengpaiUser'
    feed_info['keywords'] = []
    feed_info['subPages'] = ['user_5126969']
    feed_info['update'] = '20200106011400'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = PengpaiUserParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']

