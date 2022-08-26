#-*- coding: UTF-8 -*-
import datetime
import timestamp_utils
import re
from bs4 import BeautifulSoup
from WebParser import WebParser
import feedUtils

class PengpaiUserParser(WebParser):
    def translate_timestamp_str(self, timeStr):
        if re.match('\d{4}\-\d{2}\-\d{2}\s+\d{2}:\d{2}', timeStr) != None:
            [date_str, time_str] = timeStr.split(' ')
            date_array = date_str.split('-')
            year = int(date_array[0])
            month = int(date_array[1])
            day = int(date_array[2])
            time_array = time_str.split(':')
            hh = int(time_array[0])
            mm = int(time_array[1])
            ss = 0
            return [year, month, day, hh, mm, ss]
        return None


    def get_full_description(self, entry):
        if entry['published'] == None:
            entry['published'] = [1970, 1, 1, 0, 0, 0]
        r = self.httpClient.get(entry['link'])
        if r.status_code != 200:
            self.debug_print("$$$ No valid response " + entry['title'] + ' ' + entry['link'])
            return entry
        html = BeautifulSoup(r.text, 'html5lib')
        if html == None:
            self.debug_print("$$$ No valid html " + entry['title'] + ' ' + entry['link'])
            return entry
        time_div = html.find('div', attrs={'class': re.compile('^index_headerContent__')})
        if time_div == None:
            self.debug_print("$$$ No valid timestamp " + entry['title'] + ' ' + entry['link'])
            return entry
        spans = time_div.find_all('span')
        timestamp_str = ''
        for span in spans:
            if span.string != None and re.match('\d{4}\-\d{2}\-\d{2}\s+\d{2}:\d{2}', span.string.strip()) != None:
                timestamp_str = span.string.strip()
        if timestamp_str == '':
            self.debug_print("$$$ No valid time string " + entry['title'] + ' ' + entry['link'])
            return entry
        beijing_time = self.translate_timestamp_str(timestamp_str)
        beijing_time.append(8)
        entry['published'] = timestamp_utils.adjustTimeByTimezon(*beijing_time)
        txt_div = html.find('div', attrs={'class': re.compile('^index_cententWrap__')})
        nonDisplayElems = txt_div.find_all('audio', attrs = {'style': 'display: none;'})
        for elem in nonDisplayElems:
            elem.decompose()
        imgs = txt_div.find_all('img')
        for img in imgs:
            br = html.new_tag('br')
            img.insert_after(br)
        if txt_div != None:
            entry['description'] = txt_div.prettify()
        return entry


    def get_abstract_feed(self):
        feed = {
            'title': 'PengPai News',
            'link': self.url,
            'description': 'PengPai News',
            'entries': []
        }
        if self.subPage_flag:
            sub_pages = map(lambda x: {'path': x.replace('user_', ''), 'count': 2}, self.subPages)
        else:
            return feed
        apiUrl = 'https://api.thepaper.cn/contentapi/cont/pph/user'

        for page in sub_pages:
            titlesBySameAuthor = feedUtils.getArticleTitlesBySameAuthor(page["path"])
            postUserJson = {
                "pphId": page["path"],
                "pageNum": 1,
                "pageSize": page["count"]
            }
            r = self.httpClient.post(apiUrl, json=postUserJson)
            if r.status_code != 200:
                self.debug_print("$$$ Fail to get the json data of [%s]" % page["path"])
                continue
            jsdata = r.json()
            if "code" not in jsdata.keys() or jsdata["code"] != 200:
                self.debug_print("$$$ no valid 'code' in json data for [%s]" % (page["path"]))
                self.debug_print("$$$ json data: [%s]" % str(jsdata))
                continue
            if "data" not in jsdata.keys() or "list" not in jsdata["data"].keys():
                self.debug_print("$$$ no valid 'data.list' in json data for [%s]" % (page["path"]))
                self.debug_print("$$$ json data: [%s]" % str(jsdata))
            userName = ''
            for obj in jsdata["data"]["list"]:
                if "name" not in obj.keys() or "contId" not in obj.keys():
                    continue
                if "authorInfo" in obj.keys() and "sname" in obj["authorInfo"].keys() and userName == '':
                    userName = obj["authorInfo"]["sname"]
                if obj["name"] in titlesBySameAuthor:
                    self.debug_print("%s[PengpaiUser: %s] exist in other source, so skip it" % (obj["name"], page["path"]))
                    continue
                if userName == '':
                    title = obj["name"]
                else:
                    title = "%s | %s" % (userName, obj["name"])
                entry = {
                    'title': title,
                    'link': "%snewsDetail_forward_%s" % (self.url, obj["contId"]),
                    'published': None,
                    'description': title
                }
                feed['entries'].append(entry)
        return feed


if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'https://www.thepaper.cn/'
    feed_info['name'] = 'PengpaiUser'
    feed_info['keywords'] = []
    feed_info['subPages'] = ['user_5126969']
    feed_info['update'] = '20200106011400'
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = PengpaiUserParser(feed_info)
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_link: ' + entry['link'])
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']

