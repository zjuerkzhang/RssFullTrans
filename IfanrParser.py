#-*- coding: UTF-8 -*-
import file_utils
import config_utils
import datetime
import timestamp_utils
import re
import requests
from bs4 import BeautifulSoup
from WebParser import WebParser
import operator as op

class IfanrParser(WebParser):
    def translate_timestamp(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        return [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second]

    def get_abstract_feed(self):
        feed = {
            'title': 'PengPai News',
            'link': self.url,
            'description': 'PengPai News',
            'entries': []
        }
        r = requests.get(self.url)
        if r.status_code != 200:
            return feed
        jsdata = r.json()
        for ob in jsdata['objects']:
            entry = {
                'title': ob['post_title'],
                'link': ob['post_url'],
                'published': None,
                'description': ob['post_content']
            }
            beijing_time = self.translate_timestamp(ob['created_at'])
            beijing_time.append(8)
            entry['published'] = timestamp_utils.adjustTimeByTimezon(*beijing_time)
            feed['entries'].append(entry)
        return feed


if __name__ == "__main__":
    feed_infos = config_utils.get_feeds_from_xml("config.xml")
    feed_info = list(filter(lambda x:op.eq(x['name'], "IfanrNews"), feed_infos))[0]
    '''
    feed_info = {}
    feed_info['url'] = 'https://sso.ifanr.com/api/v5/wp/article/?post_category=%E6%97%A9%E6%8A%A5'
    feed_info['name'] = 'IfanrNews'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    '''
    feed_info['conf_file'] = 'config.xml'
    feed_info['log_file'] = 'log.log'
    parser = IfanrParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']

