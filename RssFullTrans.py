'''
Created on 2013-7-10

@author: kzhang
'''

import time
import feedparser
import config_utils
import file_utils
import timestamp_utils
import PyRSS2Gen
import datetime
from ReutersParser import ReutersParser
from FTParser import FTParser
from NYTParser import NYTParser

debug_switch_on   = 2
log_file_name = 'log.log'

def debug_print(str):
    if debug_switch_on == 1:
        print str
    if debug_switch_on == 2:
        file_utils.write_to_log_file(log_file_name, str)

def transfer_full_article(feed_conf):
    '''
    feed = {
        'url': 'http://cn.reuters.com/rssFeed/CNAnalysesNews/',
        'keywords': [
            u'\u8def\u900f\u65e9\u62a5',
            u'\u8def\u900f\u665a\u62a5'],
        'parser': 'ReuterParser',
        'name': 'CNAnalysesNews',
        'update': ''}
    '''
    file_utils.write_to_log_file(log_file_name, '-'*20)
    parser_instance_str = feed_conf['parser'] + "(feed_conf)"
    parser = eval(parser_instance_str)
    feed_data = parser.parse()
    if len(feed_data['entries']) > 0:
        new_feed = PyRSS2Gen.RSS2(
               title = feed_data['title'],
               link = feed_data['link'],
               description = feed_data['description'],
               #image = feed.feed.image,
               lastBuildDate = datetime.datetime.now())
        for entry in feed_data['entries']:
            new_feed.items.append(PyRSS2Gen.RSSItem(
                title = entry['title'],
                link = entry['link'],
                description = entry['description'],
                pubDate = entry['pubDate']))
        new_feed.write_xml(open('RSS_' + feed_conf['name'] + ".xml", "w"), 'utf-8')
        file_utils.write_to_log_file(log_file_name, "<<<*****>>> new feed generated for " + feed_conf['name'] + '(' + feed_data['title'] + ')')
    else:
        file_utils.write_to_log_file(log_file_name, ">>>*****<<< no feed generated for " + feed_conf['name'])

if __name__ == '__main__':
    config_file = 'config.xml'
    feeds = config_utils.get_feeds_from_xml(config_file)
    for feed in feeds:
        feed['conf_file'] = config_file
        feed['log_file'] = log_file_name
        transfer_full_article(feed)
