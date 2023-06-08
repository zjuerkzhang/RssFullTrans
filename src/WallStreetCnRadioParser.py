import re
from bs4 import BeautifulSoup
from WebParser import WebParser
import timestamp_utils

class WallStreetCnRadioParser(WebParser):
    def get_full_description(self, entry):
        contentUrlPatten = "https://api-one.wallstcn.com/apiv1/content/articles/%s?extract=0"
        articleId = entry['link'].split('/')[-1].split('?')[0]
        contentJsonUrl = contentUrlPatten % articleId
        r = self.httpClient.get(contentJsonUrl)
        if r.status_code != 200:
            return entry
        jsdata = r.json()
        if 'data' in jsdata.keys() and 'content' in jsdata['data'].keys():
            entry['description'] = jsdata['data']['content']
            if 'audio_uri' in jsdata['data'].keys():
                audioElem = '<audio controls><source src="%s" type="audio/mpeg"></audio>' % jsdata['data']['audio_uri']
                entry['description'] = audioElem + entry['description']
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': '华尔街见闻早餐FM-Radio',
            'link': self.url,
            'description': '华尔街见闻早餐FM-Radio',
            'entries': []
        }
        r = self.httpClient.get(self.url)
        if r.status_code != 200:
            return feed
        jsdata = r.json()
        if 'data' not in jsdata.keys() or 'items' not in jsdata['data']:
            self.debug_print("$$$ No valid data.items from json string via [%s]" % self.url)
            return feed
        for item in jsdata['data']['items']:
            entry = {
                'title': re.sub('<.+?>', '', item['title']) ,
                'link': item['uri'],
                'published': None,
                'description': item['title']
            }
            beijing_time = self.translate_timestamp(item['display_time'])
            beijing_time.append(8)
            entry['published'] = timestamp_utils.adjustTimeByTimezon(*beijing_time)
            feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://api-one.wallstcn.com/apiv1/search/article?query=华尔街见闻早餐FM-Radio&limit=3'
    feed_info['name'] = '华尔街见闻'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    feed_info['proxy'] = ''
    parser = eval("WallStreetCnRadioParser(feed_info)")
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_title: ' + entry['title'])
        #print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']
        print(entry['pubDate'])
