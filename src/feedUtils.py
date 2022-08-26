import feedparser

gRedundantRssFeedForOneAuthor = [
    {
        "userName": '西西弗评论',
        "userIdRssUrlMap": [
            {
                "userId": '62014453dca58a380c59c4be',
                "rssUrl": 'http://192.168.119.47/rss/RSS_WechatUserArticles.xml'
            },
            {
                "userId": '794520',
                "rssUrl": 'http://192.168.119.47/rss/RSS_GuanChaUserArticles.xml'
            },
            {
                "userId": '',
                "rssUrl": 'https://bloghz.ddns.net/ppf/wechatRss.xml'
            }
        ]
    },
    {
        "userName": '远川研究所',
        "userIdRssUrlMap": [
            {
                "userId": '616102e99b888e41f5cb64fb',
                "rssUrl": 'http://192.168.119.47/rss/RSS_WechatUserArticles.xml'
            },
            {
                "userId": '61d2cfe4dca58a380c3a9a8f',
                "rssUrl": 'http://192.168.119.47/rss/RSS_WechatUserArticles.xml'
            },
            {
                "userId": '5126969',
                "rssUrl": 'http://192.168.119.47/rss/RSS_PengpaiUserArticlesForKindle.xml'
            },
            {
                "userId": '',
                "rssUrl": 'https://bloghz.ddns.net/ppf/wechatRss.xml'
            }
        ]
    }
]

def getRedundantRssFeedInfoByUserId(userId):
    for info in gRedundantRssFeedForOneAuthor:
        for pair in info["userIdRssUrlMap"]:
            if userId in pair["userId"]:
                return info
    return None


def getCleanArticleTitle(title):
    splittedStrs = title.split('|')
    if len(splittedStrs) <= 1:
        return title.strip()
    else:
        return '|'.join(splittedStrs[1:]).strip()


def getOtherRssUrlsByUserId(userId, info):
    myPairs = list(filter(lambda x: x["userId"] == userId, info["userIdRssUrlMap"]))
    myUrl = myPairs[0]["rssUrl"] if len(myPairs) == 1 else ''
    rssUrls = []
    for pair in info["userIdRssUrlMap"]:
        if pair["rssUrl"] != myUrl:
            rssUrls.append(pair["rssUrl"])
    return rssUrls


def getArticleTitlesBySameAuthor(userId):
    titles = []
    authorInfo = getRedundantRssFeedInfoByUserId(userId)
    if authorInfo == None:
        return titles
    rssUrls = getOtherRssUrlsByUserId(userId, authorInfo)
    #print("[feedUtils]: %s" % userId)
    #print(rssUrls)
    for url in rssUrls:
        anotherFeed = feedparser.parse(url)
        titlesInOneFeed = list(map(lambda x: getCleanArticleTitle(x.title), anotherFeed.entries))
        titles.extend(titlesInOneFeed)
    return titles


if __name__ == '__main__':
    titles = getArticleTitlesBySameAuthor('794520')
    print('-' * 30)
    for t in titles:
        print(t)

    titles = getArticleTitlesBySameAuthor('616102e99b888e41f5cb64fb')
    print('-' * 30)
    for t in titles:
        print(t)

    titles = getArticleTitlesBySameAuthor('x')
    print('-' * 30)
    for t in titles:
        print(t)

