#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser

class DskbParser(WebParser):
    def get_publish_time(self, file_path):
        strs = file_path.split('/')
        if len(strs) > 3:
            return [int(strs[0]), int(strs[1]), int(strs[2]), 8, 0, 0]
        else:
            dt = datetime.datetime.now()
            return [dt.year, dt.month, dt.day, 8, 0, 0]

    def __filter_wanted_pages(self, titles):
        condition = [
            u'都市快报',
            u'杭州新闻',
            u'西湖新闻',
            u'北高峰',
            u'快报房产',
            u'爱学习的狮子',
            u'杭州硅谷',
            u'城市早知道',
            u'教育新闻',
            u'民意直通车,
            u'浙江新闻',
            u'警戒线',
            u'重要消息']
        patten = re.compile('[A-Z]\d+')
        filter_titles = []
        for t in titles:
            if len(list(filter(lambda x:t.find(x)>=0, condition))) > 0:
                matches = patten.findall(t)
                if len(matches) > 0:
                    filter_titles.append(matches[0])
        return filter_titles

    def __is_link_in_wanted_page(self, link, page_symbels):
        return len(list(filter(lambda x:link.find(x) >= 0, page_symbels))) >0

    def get_full_description(self, entry):
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            return entry
        r.encoding = 'utf-8'
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            return entry
        div = html.find('div', attrs={'class': 'content'})
        if div != None:
            entry['description'] = div.prettify()
        return entry

    def get_abstract_feed(self):
        feed = {
            'title': 'Dskb News',
            'link': self.url,
            'description': 'Dskb News',
            'entries': []
        }
        site_url = '/'.join(self.url.split('/')[:-1])
        r = self.httpClient.get(self.url)
        if r.status_code != 200:
            return feed
        strs = r.text.split('"')
        if len(strs) != 3:
            return feed
        actual_url = site_url + '/' + strs[1].replace('page', 'article')
        beijing_time = self.get_publish_time(strs[1])
        beijing_time.append(8)
        published = timestamp_utils.adjustTimeByTimezon(*beijing_time)
        r = self.httpClient.get(actual_url)
        if r.status_code != 200:
            return feed
        r.encoding = 'utf-8'
        page_url = '/'.join(actual_url.split('/')[:-1])
        page = BeautifulSoup(r.text, 'html5lib')
        if page == None:
            return feed
        page_list_div = page.find("div", attrs={'class': 'page-list'})
        if page_list_div == None:
            return feed
        title_divs = page_list_div.find_all("div", attrs={'class': 'title'})
        titles = list(filter(lambda x:len(x)>0, map(lambda x:x.string if x.string!=None else '', title_divs)))
        title_symbs = self.__filter_wanted_pages(titles)
        print(title_symbs)
        a_s = page_list_div.find_all("a")
        for a in a_s:
            if a.string != None and len(a.string.replace(' ', '')) > 0 and self.__is_link_in_wanted_page(a['href'], title_symbs):
                entry = {
                    'title': a.string,
                    'link': page_url + '/' + a['href'],
                    'published': published,
                    'description': a.string
                }
                feed['entries'].append(entry)
        return feed

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'http://mdaily.hangzhou.com.cn/dskb/index.html'
    feed_info['name'] = 'DskbNews'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = DskbParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']

