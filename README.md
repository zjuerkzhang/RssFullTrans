# RssFullTrans

## Demo
[https://fullrss.ddns.net/rss/](https://fullrss.ddns.net/rss/)

## config.xml
```
<feed update="20181207015233">
    <url>http://cn.reuters.com/rssFeed/CNAnalysesNews/</url>
    <parser>ReutersParser</parser>
    <keywords>
        <keyword>路透早报</keyword>
        <keyword>路透晚报</keyword>
    </keywords>
    <blacklist>
        <blackItem>过滤词</blackItem>
    </blacklist>
</feed>
```
- `url`: The url of source RSS feed;
- `parser`: The parser which parse the article page and fetch the content;
- `keyword`: The keyword which is used to filter the entries whose title contains the keyword.
- `blackItem`: The item which is used to filter out the entries whose title contains the blackItem.
