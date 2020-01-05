#!/bin/bash
export LANG="zh_CN.UTF-8"
export http_proxy="http://10.144.1.10:8080"
export https_proxy="http://10.144.1.10:8080"

cd /home/kzhang/github/RssFullTrans
mkdir -p log
mkdir -p output

html_dir=/home/kzhang/github/fullrss.github.io
rss_dir=$html_dir/rss

cp $rss_dir/RSS_*.xml ./output/
python src/RssFullTrans.py

ls ./output/|grep RSS_
if [ $? -eq 0 ]
then
    mv output/RSS_*.xml $rss_dir/
    cp html/index.html $html_dir
    cp html/index.html $rss_dir
    cd $rss_dir
    git add --all
    msg=`date`
    git commit -m "$msg"
    git push
fi

unset http_proxy
unset https_proxy
