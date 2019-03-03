'''
Created on 2013-7-10

@author: kzhang
'''
import os
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
from PengpaiParser import PengpaiParser
from GuanchaParser import GuanchaParser
from PentiParser import PentiParser

max_entry_count_in_feed = 20
debug_switch_on   = 2
log_file_name = 'log.log'

def debug_print(str):
    if debug_switch_on == 1:
        print str
    if debug_switch_on == 2:
        file_utils.write_to_log_file(log_file_name, str)

def parse_and_sort_existing_feed_items(rss_xml_file):
    feed = feedparser.parse(rss_xml_file)
    items = []
    for entry in feed.entries:
        (yy, mm, dd, hh, MM, ss) = timestamp_utils.getTimeDecFromPubdate(entry['published'])
        items.append(PyRSS2Gen.RSSItem(
            title = entry.title,
            link = entry.link,
            description = entry.description,
            pubDate = datetime.datetime(yy, mm, dd, hh, MM, ss)))
    items = sorted(items, key=lambda x:x.pubDate, reverse=True)
    return items

def transfer_full_article(feed_conf):
    '''
    feed = {
        'url': 'http://cn.reuters.com/rssFeed/CNAnalysesNews/',
        'keywords': [
            u'\u8def\u900f\u65e9\u62a5',
            u'\u8def\u900f\u665a\u62a5'],
        'parser': 'ReuterParser',
        'name': 'CNAnalysesNews',
        'title': ''
        'update': ''}
    '''
    file_utils.write_to_log_file(log_file_name, '-'*50)
    parser_instance_str = feed_conf['parser'] + "(feed_conf)"
    parser = eval(parser_instance_str)
    feed_data = parser.parse()
    if len(feed_data['entries']) > 0:
        new_feed = PyRSS2Gen.RSS2(
               title = feed_conf['title'] if len(feed_conf['title']) > 0 else feed_data['title'],
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
        rss_xml_file = 'RSS_' + feed_conf['name'] + ".xml"
        if (len(new_feed.items) < max_entry_count_in_feed) and os.path.isfile(rss_xml_file):
            old_entry_to_merge_count = max_entry_count_in_feed - len(new_feed.items)
            file_utils.write_to_log_file(log_file_name, "--> Merge existing feed items")
            old_entries = parse_and_sort_existing_feed_items(rss_xml_file)
            if len(old_entries) < old_entry_to_merge_count:
                old_entry_to_merge_count = len(old_entries)
            i = 0
            while i < old_entry_to_merge_count:
                new_feed.items.append(old_entries[i])
                i = i + 1
        new_feed.write_xml(open(rss_xml_file, "w"), 'utf-8')
        file_utils.write_to_log_file(log_file_name, "<<<*****>>> new feed generated for " + feed_conf['name'] + '(' + feed_data['title'] + ')')
    else:
        file_utils.write_to_log_file(log_file_name, ">>>*****<<< no feed generated for " + feed_conf['name'])

if __name__ == '__main__':
    file_utils.write_to_log_file(log_file_name, "="*50)

    config_file = 'config.xml'
    feeds = config_utils.get_feeds_from_xml(config_file)
    for feed in feeds:
        feed['conf_file'] = config_file
        feed['log_file'] = log_file_name
        transfer_full_article(feed)
    '''
    entries = parse_and_sort_existing_feed_items('RSS_CNAnalysesNews.xml')
    for entry in entries:
        print entry.title
        print entry.link
        print entry.pubDate
    '''
