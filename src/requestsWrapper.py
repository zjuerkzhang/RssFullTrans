import requests
import random
import time

class requestsWrapper(object):
    """docstring for requestsWrapper"""
    def __init__(self, host, baseDelay = 0, randomDelay = False, retryCount = 0, timeout = 30):
        self.host = host
        self.baseDelay = baseDelay
        self.randomDelay = randomDelay
        self.retryCount = retryCount
        self.timeout = timeout
        self.cookies = None
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-Hans-CN,zh-CN;q=0.9,zh;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5,ja;q=0.4',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.53 Safari/537.36 Edg/80.0.361.33',
            'Connection' : 'keep-alive',
            'Cache-Control': 'no-cache',
            'Host': self.host
        }

    def getRandomDelay(self):
        delay = self.baseDelay
        if self.randomDelay:
            delay = delay + random.random()
        return delay

    def get(self, url):
        #print("try to get: " + url)
        #print(self.cookies)
        time.sleep(self.getRandomDelay())
        resp = requests.get(url, timeout = self.timeout, headers = self.headers, cookies = self.cookies)
        retryCount = self.retryCount
        while resp.status_code != 200 and retryCount > 0:
            retryCount = retryCount - 1
            time.sleep(self.getRandomDelay())
            resp = requests.get(url, timeout = self.timeout, headers = self.headers, cookies = self.cookies)
        if resp.status_code == 200:
            if self.cookies == None:
                self.cookies = resp.cookies
            return resp
        else:
            return None

    def post(self, url, json = None):
        #print("try to get: " + url)
        #print(self.cookies)
        time.sleep(self.getRandomDelay())
        resp = requests.post(url, timeout = self.timeout, headers = self.headers, json = json, cookies = self.cookies)
        retryCount = self.retryCount
        while resp.status_code != 200 and retryCount > 0:
            retryCount = retryCount - 1
            time.sleep(self.getRandomDelay())
            resp = requests.post(url, timeout = self.timeout, headers = self.headers, json = json, cookies = self.cookies)
        if resp.status_code == 200:
            if self.cookies == None:
                self.cookies = resp.cookies
            return resp
        else:
            return None

