#-*- coding: UTF-8 -*-
import datetime
from os import times
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class WxnmhParser(WebParser):
    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            self.debug_print("$$$ No valid response " + entry['title'] + ' ' + entry['link'])
            return entry
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry

        div = html.find('div', attrs={'class': 'rich_media_content'})
        if not div:
            return entry

        title_str = ''
        title = html.find('title')
        if title != None:
            title_str = title.string
        entry['description'] = title_str + '<br>' + div.prettify().replace("data-src", "src")
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': 'Wechat User Articles',
            'link': self.url,
            'description': 'Wechat User Articles',
            'entries': []
        }
        if self.subPage_flag:
            sub_pages = map(lambda x: {'path': x + '.htm', 'count': 2}, self.subPages)
        else:
            return feed

        for page in sub_pages:
            url = self.url + page['path']
            r = self.httpClient.get(url)
            if r.status_code != 200:
                continue
            html = BeautifulSoup(r.text, 'html5lib')
            if html == None:
                continue
            tds = html.find_all('td', attrs = {'class': 'td-subject p-l-0'})
            if len(tds) > page['count']:
                tds = tds[:page['count']]
            for td in tds:
                subjectDiv = td.find('div', attrs = {'class': 'subject'})
                if not subjectDiv:
                    continue
                a = subjectDiv.find('a')
                if not a:
                    continue
                self.debug_print("$$$ entry found [%s]" % a.string)
                dt = td.find('dt')
                if dt.prettify().find('小时前') < 0:
                    continue
                publishTime = timestamp_utils.adjustTimeByTimezon(1970, 1, 1, 0, 0, 0, 8)
                for child in list(dt.children):
                    if isinstance(child, str) and child.strip() != '':
                        timeStr = child.strip()
                        if timeStr.find('小时前') > 0:
                            try:
                                hours = int(timeStr.replace('小时前', ''))
                                pbBjT = datetime.datetime.today() + datetime.timedelta(hours = (0-hours))
                                publishTime = timestamp_utils.adjustTimeByTimezon(pbBjT.year, pbBjT.month, pbBjT.day, pbBjT.hour, 0, 0, 8)
                                break
                            except:
                                self.debug_print("$$$ Invalid publish date time [%s]" % timeStr)
                                continue
                entry = {
                    'title': a.string,
                    'link': self.url + a['href'],
                    'published': publishTime,
                    'description': a.string
                }
                feed['entries'].append(entry)
        return feed


if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://www.wxnmh.com/'
    feed_info['name'] = 'WechatUserArticles'
    feed_info['keywords'] = []
    feed_info['subPages'] = ['user-115792', 'user-28079']
    feed_info['update'] = '20200106011400'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = WxnmhParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']

