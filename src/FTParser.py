import re
from bs4 import BeautifulSoup
from GeneralParser import GeneralParser

class FTParser(GeneralParser):
    def get_full_description(self, entry):
        urls = [
            entry.link + '?full=y',
            entry.link + '?full=y&exclusive'
        ]
        for url in urls:
            r = self.httpClient.get(url)
            if r.status_code != 200:
                continue
            html = BeautifulSoup(r.text, "html5lib")
            if html == None:
                continue
            article_div = html.find('div', attrs={'id': 'story-body-container'})
            if not article_div:
                continue
            break
        if not article_div:
            r = self.httpClient.get(entry.link + '?full=y&exclusive' )

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
    feed_info['url'] = 'http://www.ftchinese.com/rss/news'
    feed_info['name'] = 'FtFocusNews'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = eval("FTParser(feed_info)")
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']
