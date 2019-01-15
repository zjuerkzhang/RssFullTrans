#!/bin/bash
export LANG="zh_CN.UTF-8"

cd /root/RssFullTrans

if [ -d "/var/www/rss" ]
then
    rss_dir=/var/www/rss
elif [ -d "/usr/shared/nginx/html/rss" ]
then
    rss_dir=/usr/shared/nginx/html/rss
else
    rss_dir=/root/RssFullTrans
fi

cp $rss_dir/RSS_*.xml ./
python RssFullTrans.py

ls |grep RSS_ 
if [ $? -eq 0 ]
then
	mv RSS_*.xml $rss_dir/ 
fi
