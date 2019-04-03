import re
import requests
from bs4 import BeautifulSoup
from GeneralParser import GeneralParser
import config_utils
import operator as op

class NYTParser(GeneralParser):
    def get_full_description(self, entry):
        r = requests.get(entry.link)
        if r.status_code != 200:
            return ''
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return ''
        partial_divs = html.find_all('div', attrs={'class': 'article-partial'})
        content = ''
        for partial in partial_divs:
            paragraph_divs = partial.find_all('div', attrs={'class': 'article-paragraph'})
            for para in paragraph_divs:
                content = content + para.prettify()
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
    feed_infos = config_utils.get_feeds_from_xml("config.xml")
    feed_info = list(filter(lambda x:op.eq(x['name'], "NytIntNews"), feed_infos))[0]
    '''
    feed_info = {}
    feed_info['url'] = 'https://cn.nytimes.com/rss.html'
    feed_info['name'] = 'NytIntNews'
    feed_info['keywords'] = []
    '''
    feed_info['update'] = ''
    feed_info['conf_file'] = 'config.xml'
    feed_info['log_file'] = 'log.log'
    parser = eval("NYTParser(feed_info)")
    feed_data = parser.parse()
    
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_title: ' + entry['title'])
        #print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']
    
