import re
import requests
from bs4 import BeautifulSoup
from GeneralParser import GeneralParser

class ReutersParser(GeneralParser):
    def get_full_description(self, entry):
        r = requests.get(entry.link)
        if r.status_code != 200:
            return ''
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return ''
        article_div = html.find('div', attrs={'class': 'StandardArticleBody_body'})
        if not article_div:
            return ''
        figure = article_div.find('figure', attrs={'class': 'Image_zoom'})
        if figure != None:
            img_src = ''
            imgs = figure.find_all('img')
            if len(imgs) > 0:
                img_src = imgs[0]['src']
                pattern = re.compile('&w=\d+')
                img_src = pattern.sub('', img_src) + '&w=800'
            figure_sub_divs = figure.find_all('div')
            for div in figure_sub_divs:
                div.decompose()
            if len(img_src) > 0:
                figure.append(html.new_tag('img', src=img_src))
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
    feed_info['url'] = 'http://cn.reuters.com/rssFeed/CNAnalysesNews/'
    feed_info['name'] = 'CNAnalysesNews'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = 'config.xml'
    feed_info['log_file'] = 'log.log'
    parser = eval("ReutersParser(feed_info)")
    feed_data = parser.parse()
    print ' '*1 + 'feed_title: ' + feed_data['title']
    print ' '*1 + 'entries: '
    for entry in feed_data['entries']:
        print ' '*3 + 'entry_title: ' + entry['title']
        print ' '*3 + 'entry_des: ' + entry['description']
        #print ' '*3 + 'entry_content: ' + entry['content']
