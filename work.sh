#!/bin/bash
export LANG="zh_CN.UTF-8"
cd /root/RssFullTrans
python RssFullTrans.py
ls |grep RSS_ 
if [ $? -eq 0 ]
then
	mv RSS_*.xml /usr/share/nginx/html/rss/
fi