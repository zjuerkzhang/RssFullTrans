import os
import xml.etree.ElementTree as ET

self_dir = os.path.dirname(os.path.abspath(__file__))
sample_config_file = self_dir + "/../config/config.xml"

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
                name = feed.find("name")
                if name == None:
                    one_feed['name'] = list(filter(lambda x: len(x) > 0, one_feed['url'].split('/')))[-1]
                else:
                    one_feed['name'] = name.text
                title = feed.find("title")
                if title == None:
                    one_feed['title'] = ''
                else:
                    one_feed['title'] = title.text
                enabling = feed.find("enableStatus")
                if enabling != None and enabling.text == "False":
                    one_feed['enableStatus'] = False
                else:
                    one_feed['enableStatus'] = True
                if 'update' in feed.attrib.keys():
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
                black_items = feed.iter("blackItem")
                blk_array = []
                for blk in black_items:
                    blk_array.append(blk.text)
                one_feed['blacklist'] = blk_array
                sub_page_items = feed.iter("subPage")
                sub_pages = []
                for sub_page in sub_page_items:
                    sub_pages.append(sub_page.text)
                one_feed['subPages'] = sub_pages
                proxy = feed.find('proxy')
                if proxy != None:
                    one_feed['proxy'] = proxy.text
                else:
                    one_feed['proxy'] = ''
            ret_feeds.append(one_feed)
        return ret_feeds
    else:
        return []

def update_feed_timestamp(feed_name, feed_url, timestamp, config_file = sample_config_file):
    if os.path.isfile(config_file):
        tree = ET.parse(config_file)
        root = tree.getroot()
        feeds = root.findall("feed")
        ret_feed = list(filter(lambda x:x.find('url').text == feed_url and x.find('name').text == feed_name, feeds))
        if len(ret_feed) > 0:
            ret_feed[0].set('update', timestamp)
            tree.write(config_file, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    feeds = get_feeds_from_xml(sample_config_file)
    if len(feeds) > 0:
        print("%d feeds are fetched from the file <" + sample_config_file + ">", len(feeds))
        for feed in feeds:
            print(feed)

    #update_feed_timestamp("http://cn.reuters.com/rssFeed/CNTopGenNews/", "20180909120000")
