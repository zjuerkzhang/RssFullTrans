from GeneralParser import GeneralParser

class ZhuNewsParser(GeneralParser):
    def abstract_title(self, entry):
        title = entry.title
        splitedStrs = title.split("。")
        return splitedStrs[0]

if __name__ == "__main__":
    feed_info = {}
    feed_info['url'] = 'http://192.168.119.47:1200/telegram/channel/tnews365'
    feed_info['name'] = '竹新社'
    feed_info['keywords'] = []
    feed_info['update'] = ''
    feed_info['proxy'] = ''
    feed_info['conf_file'] = '../config/config.xml'
    feed_info['log_file'] = '../log/log.log'
    parser = eval("ZhuNewsParser(feed_info)")
    feed_data = parser.parse()
    print(' '*1 + 'feed_title: ' + feed_data['title'])
    print(' '*1 + 'entries: ')
    for entry in feed_data['entries']:
        print(' '*3 + 'entry_title: ' + entry['title'])
        print(' '*3 + 'entry_des: ' + entry['description'])
        #print ' '*3 + 'entry_content: ' + entry['content']