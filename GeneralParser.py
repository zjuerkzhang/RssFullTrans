import feedparser
import file_utils
import config_utils
import datetime
import timestamp_utils

class GeneralParser(object):
    def __init__(self, feed_info):
        '''
        feed = {
            'url': 'http://cn.reuters.com/rssFeed/CNAnalysesNews/',
            'keywords': [
                u'\u8def\u900f\u65e9\u62a5',
                u'\u8def\u900f\u665a\u62a5'],
            'parser': 'ReuterParser',
            'name': 'CNAnalysesNews',
            'update': '',
            'conf_file': 'config.xml,
            'log_file': 'log.log'}
        '''
        self.url = feed_info['url']
        self.name = feed_info['name']
        self.update = feed_info['update']
        self.new_update = self.update
        self.conf_file = feed_info['conf_file']
        self.log_file = feed_info['log_file']
        self.debug_switch_on = 2
        if len(feed_info['keywords']) <= 0:
            self.key_flag = False
            self.keywords = []
        else:
            self.key_flag = True
            self.keywords = feed_info['keywords']

    def debug_print(self, str):
        if self.debug_switch_on == 1:
            print str
        if self.debug_switch_on == 2:
            file_utils.write_to_log_file(self.log_file, str)

    def get_full_description(self, entry):
        ret_str = entry.description
        return ret_str        

    def __is_entry_new(self, entry):
        entry_time = "%04d%02d%02d%02d%02d%02d" % entry.published_parsed[:6]
        self.debug_print("entry %s published at %s" % (entry.title, entry_time))
        if cmp(entry_time, self.update) > 0:
            self.debug_print("===> New item")
            if cmp(entry_time, self.new_update) > 0:
                self.new_update = entry_time
            return True
        else:
            self.debug_print("===> [old one]")
            return False

    def __is_entry_contain_key(self, entry_title):
        if not self.key_flag:
            #self.debug_print("---> contain keyword")
            return True
        for key in self.keywords:
            if entry_title.find(key) >= 0:
                #self.debug_print("---> contain keyword")
                return True
        return False

    def parse(self): 
        self.debug_print("last_time for %s %s" % (self.name, self.update))
        feed = feedparser.parse(self.url)
        feed_data = {
                        'title': feed.feed.title,
                        'link': feed.feed.link,
                        'description': "This is the full text parser for feed <" + feed.feed.title + ">",
                        'entries': [],
                    }
        for entry in feed.entries:
            if not self.__is_entry_contain_key(entry.title):
                continue
            if self.__is_entry_new(entry):
                (yy, mm, dd, hh, MM, ss) = timestamp_utils.getTimeDecFromPubdate(entry['published'])
                entry_data = {
                                 'title': entry.title,
                                 'description': self.get_full_description(entry),
                                 'link': entry.link,
                                 'pubDate': datetime.datetime(yy, mm, dd, hh, MM, ss)
                             }
                feed_data['entries'].append(entry_data)
        if len(feed_data['entries']) > 0:
            config_utils.update_feed_timestamp(self.url, self.new_update, self.conf_file)
        return feed_data

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'http://cn.reuters.com/rssFeed/CNAnalysesNews/'
    feed_info['name'] = 'CNAnalysesNews'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['conf_file'] = 'config.xml'
    feed_info['log_file'] = 'log.log'
    parser = GeneralParser(feed_info)
    feed_data = parser.parse()
    print ' '*1 + 'feed_title: ' + feed_data['title']
    print ' '*1 + 'entries: '
    for entry in feed_data['entries']:
        print ' '*3 + 'entry_title: ' + entry['title']
        #print ' '*3 + 'entry_des: ' + entry['description']
        #print ' '*3 + 'entry_content: ' + entry['content']

