import re
import requests
from bs4 import BeautifulSoup
from GeneralParser import GeneralParser

class FTParser(GeneralParser):
    def get_full_description(self, entry):
        r = requests.get(entry.link + '?full=y')
        if r.status_code != 200:
            return ''
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return ''
        article_div = html.find('div', attrs={'id': 'story-body-container'})
        if not article_div:
            return ''
        ad_divs = article_div.find_all('div', attrs={'class': 'o-ads'})
        for ad in ad_divs:
            ad.decompose()
        scripts = article_div.find_all('script', attrs={'type': 'text/javascript'})
        for s in scripts:
            s.decompose()
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
    feed_info['url'] = 'http://www.ftchinese.com/rss/hotstoryby7day'
    feed_info['name'] = 'hotstoryby7day'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = 'config.xml'
    feed_info['log_file'] = 'log.log'
    parser = eval("FTParser(feed_info)")
    feed_data = parser.parse()
    print ' '*1 + 'feed_title: ' + feed_data['title']
    print ' '*1 + 'entries: '
    for entry in feed_data['entries']:
        print ' '*3 + 'entry_title: ' + entry['title']
        print ' '*3 + 'entry_des: ' + entry['description']
        #print ' '*3 + 'entry_content: ' + entry['content']
