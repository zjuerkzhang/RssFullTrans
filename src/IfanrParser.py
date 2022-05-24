#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class IfanrParser(WebParser):
    def get_abstract_feed(self):
        feed = {
            'title': 'PengPai News',
            'link': self.url,
            'description': 'PengPai News',
            'entries': []
        }
        r = self.httpClient.get(self.url)
        if r.status_code != 200:
            return feed
        jsdata = r.json()
        for ob in jsdata['objects']:
            entry = {
                'title': ob['post_title'],
                'link': ob['post_url'],
                'published': None,
                'description': ob['post_content'].replace(chr(8), "")
            }
            beijing_time = self.translate_timestamp(ob['created_at'])
            beijing_time.append(8)
            entry['published'] = timestamp_utils.adjustTimeByTimezon(*beijing_time)
            feed['entries'].append(entry)
        return feed


if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://sso.ifanr.com/api/v5/wp/article/?post_category=%E6%97%A9%E6%8A%A5'
    feed_info['name'] = 'IfanrNews'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = IfanrParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print(' '*3 + 'entry_content: ' + entry['content'])
        if entry['description'].find(chr(8))>=0:
            print("find \h")
