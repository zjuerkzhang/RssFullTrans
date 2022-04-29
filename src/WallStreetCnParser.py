import re
from bs4 import BeautifulSoup
from GeneralParser import GeneralParser

class WallStreetCnParser(GeneralParser):
    def get_full_description(self, entry):
        contentUrlPatten = "https://api-one.wallstcn.com/apiv1/content/articles/%s?extract=0"
        articleId = entry.link.split('/')[-1]
        contentJsonUrl = contentUrlPatten % articleId
        r = self.httpClient.get(contentJsonUrl)
        if r.status_code != 200:
            return entry.description
        jsdata = r.json()
        if 'data' in jsdata.keys() and 'content' in jsdata['data'].keys():
            return jsdata['data']['content']
        return entry.description

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://rsshub.app/wallstreetcn/news/global'
    feed_info['name'] = '华尔街见闻'
    feed_info['keywords'] = ["华尔街见闻早餐FM-Radio"]
    feed_info['update'] = ''
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    feed_info['proxy'] = 'http://127.0.0.1:8080'
    parser = eval("WallStreetCnParser(feed_info)")
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']
