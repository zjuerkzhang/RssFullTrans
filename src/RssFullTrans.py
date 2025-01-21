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
import threading
import datetime
from ReutersParser import ReutersParser
from FTParser import FTParser
from NYTParser import NYTParser
from PengpaiParser import PengpaiParser
from PengpaiUserParser import PengpaiUserParser
from GuanchaParser import GuanchaParser
from PentiParser import PentiParser
from IfanrParser import IfanrParser
from DskbParser import DskbParser
from BbcParser import BbcParser
from MicroHistoryParser import MicroHistoryParser
from CctvNewsParser import CctvNewsParser
from ClTechParser import ClTechParser
from GeneralParser import GeneralParser
from YiqingParser import YiqingParser
from WxnmhParser import WxnmhParser
from GuanChaUserParser import GuanChaUserParser
from NeteaseUserParser import NeteaseUserParser
from WallStreetCnRadioParser import WallStreetCnRadioParser
from GuanChaZhuanLanParser import GuanChaZhuanLanParser
from HaozaobaoParser import HaozaobaoParser
from FeedddParser import FeedddParser
from ZhuNewsParser import ZhuNewsParser

max_entry_count_in_feed = 20
debug_switch_on   = 2

self_dir = os.path.dirname(os.path.abspath(__file__))
log_file_dir = self_dir + "/../log/"
config_file_dir = self_dir + "/../config/"
xml_file_dir = self_dir + "/../output/"
lockConfigFile = threading.Lock()

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
    file_utils.write_to_log_file(feed_conf['log_file'], '-'*50)
    parser_instance_str = feed_conf['parser'] + "(feed_conf)"
    parser = eval(parser_instance_str)
    feed_data = parser.parse()
    if len(feed_data['entries']) > 0:
        rss_xml_file = xml_file_dir + 'RSS_' + feed_conf['name'] + ".xml"
        old_entries = []
        if os.path.isfile(rss_xml_file):
            old_entries = parse_and_sort_existing_feed_items(rss_xml_file)
            file_utils.write_to_log_file(feed_conf['log_file'], "--> old entries count from [%s]: %d" % (rss_xml_file, len(old_entries)))
        old_links = list(map(lambda x:x.link, old_entries))

        new_feed = PyRSS2Gen.RSS2(
               title = feed_conf['title'] if len(feed_conf['title']) > 0 else feed_data['title'],
               link = feed_data['link'],
               description = feed_data['description'],
               #image = feed.feed.image,
               lastBuildDate = datetime.datetime.now())
        for entry in feed_data['entries']:
            if entry['link'] in old_links:
                file_utils.write_to_log_file(feed_conf['log_file'], "--> entry [%s] exists in old entries" % entry['title'])
                continue
            new_feed.items.append(PyRSS2Gen.RSSItem(
                title = entry['title'],
                link = entry['link'],
                description = entry['description'],
                pubDate = entry['pubDate']))

        if (len(new_feed.items) < max_entry_count_in_feed) and len(old_entries) > 0:
            old_entry_to_merge_count = max_entry_count_in_feed - len(new_feed.items)
            file_utils.write_to_log_file(feed_conf['log_file'], "--> Merge existing feed items")
            if len(old_entries) < old_entry_to_merge_count:
                old_entry_to_merge_count = len(old_entries)
            i = 0
            while i < old_entry_to_merge_count:
                new_feed.items.append(old_entries[i])
                i = i + 1
        new_feed.write_xml(open(rss_xml_file, "w"), 'utf-8')
        file_utils.write_to_log_file(feed_conf['log_file'], "<<<*****>>> new feed generated for " + feed_conf['name'] + '(' + feed_data['title'] + ')')
    else:
        file_utils.write_to_log_file(feed_conf['log_file'], ">>>*****<<< no feed generated for " + feed_conf['name'])

if __name__ == '__main__':
    thread_array = []
    config_file = config_file_dir + 'config.xml'
    feeds = config_utils.get_feeds_from_xml(config_file)
    for feed in feeds:
        if feed['enableStatus'] == False:
            continue
        feed['conf_file'] = config_file
        feed['log_file'] = log_file_dir + feed['name'] + ".log"
        feed['lock'] = lockConfigFile
        thread_entry = threading.Thread(target=transfer_full_article, args=(feed,), name="thread-" + feed['name'])
        thread_entry.daemon = True
        thread_array.append(thread_entry)
        thread_entry.start()
        file_utils.write_to_log_file(log_file_dir + "main.log", "start %s" % thread_entry.name)
        #print("start %s" % thread_entry.name)
    for thr in thread_array:
        thr.join(5*60)
        file_utils.write_to_log_file(log_file_dir + "main.log", "finished %s" % thr.name)
        #print("%s finished" % thr.name)
    '''
    entries = parse_and_sort_existing_feed_items('RSS_CNAnalysesNews.xml')
    for entry in entries:
        print entry.title
        print entry.link
        print entry.pubDate
    '''
