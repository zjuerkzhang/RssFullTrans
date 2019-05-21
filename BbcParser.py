import re
import requests
from bs4 import BeautifulSoup
from GeneralParser import GeneralParser

class BbcParser(GeneralParser):
    def get_full_description(self, entry):
        r = requests.get(entry.link)
        if r.status_code != 200:
            return ''
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return ''
        article_div = html.find('div', attrs={'class': 'story-body__inner'})
        if not article_div:
            return ''
        content = article_div.prettify()
        #self.debug_print(content)
        #pattern = re.compile('<div class="StandardArticleBody_body">.*?</div>', re.S)
        #strs = pattern.findall(content)
        #content = strs[0]
        #pattern = re.compile('<div[^>]+>')
        #content = pattern.sub('', content)
        #pattern = re.compile('</div>')
        #content = pattern.sub('', content)
        return content

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'http://feeds.bbci.co.uk/news/world/asia/china/rss.xml'
    feed_info['name'] = 'BBC China News'
    feed_info['keywords'] = []
    feed_info['blacklist'] = ''
    feed_info['update'] = ''
    feed_info['conf_file'] = 'config.xml'
    feed_info['log_file'] = 'log.log'
    parser = eval("BbcParser(feed_info)")
    feed_data = parser.parse()
    print ' '*1 + 'feed_title: ' + feed_data['title']
    print ' '*1 + 'entries: '
    for entry in feed_data['entries']:
        print ' '*3 + 'entry_title: ' + entry['title']
        print ' '*3 + 'entry_des: ' + entry['description']
        #print ' '*3 + 'entry_content: ' + entry['content']
