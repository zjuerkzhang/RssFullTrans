import os
import xml.etree.ElementTree as ET

sample_config_file = "config.xml"

def get_feeds_from_xml(config_file = sample_config_file):
    if os.path.isfile(config_file):
        ret_feeds = []
        tree = ET.parse(config_file)
        root = tree.getroot()
        feeds = root.findall("feed")
        for feed in feeds:
            one_feed = {}
            url = feed.find("url")
            if url == None:
                continue
            else:
                one_feed['url'] = url.text
                one_feed['name'] = filter(lambda x: len(x) > 0, one_feed['url'].split('/'))[-1]
                if feed.attrib.has_key('update'):
                    one_feed['update'] = feed.attrib['update']
                else:
                    one_feed['update'] = ''
                parser = feed.find('parser')
                if parser != None:
                    one_feed['parser'] = parser.text
                else:
                    one_feed['parser'] = ''
                keywords = feed.iter("keyword")
                kw_array = []
                for kw in keywords:
                    kw_array.append(kw.text)
                one_feed['keywords'] = kw_array
            ret_feeds.append(one_feed)
        return ret_feeds
    else:
        return []

def update_feed_timestamp(feed_url, timestamp, config_file = sample_config_file):
    if os.path.isfile(config_file):
        tree = ET.parse(config_file)
        root = tree.getroot()
        feeds = root.findall("feed")
        ret_feed = filter(lambda x:x.find('url').text == feed_url, feeds)
        if len(ret_feed) > 0:
            ret_feed[0].set('update', timestamp)
            tree.write(config_file, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    feeds = get_feeds_from_xml(sample_config_file)
    if len(feeds) > 0:
        print len(feeds), "feeds are fetched from the file <" + sample_config_file + ">"
        for feed in feeds:
            print feed

    #update_feed_timestamp("http://cn.reuters.com/rssFeed/CNTopGenNews/", "20180909120000")
