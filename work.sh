#!/bin/bash
export LANG="zh_CN.UTF-8"

cd /root/RssFullTrans

rss_dir=/root/fullrss.github.io/rss

cp $rss_dir/RSS_*.xml ./
python RssFullTrans.py

ls |grep RSS_ 
if [ $? -eq 0 ]
then
	mv RSS_*.xml $rss_dir/ 
    cd $rss_dir
    git add --all
    msg=`date`
    git commit -m "$msg"
    git push
fi

