#!/bin/bash
export LANG="zh_CN.UTF-8"

proxyIpAddr="10.158.100.2"
outStr=`ping -c 1 -W 2 $proxyIpAddr`
pingStatus=$?
if [ $pingStatus -eq 0 ]
then
    export http_proxy="http://$proxyIpAddr:8080"
    export https_proxy="http://$proxyIpAddr:8080"
fi

filePath=$0
fileDir=`dirname $filePath`
cd $fileDir

mkdir -p log
mkdir -p output

html_dir=$fileDir/../fullrss.github.io
rss_dir=$html_dir/rss

cp $rss_dir/RSS_*.xml ./output/
python3 src/RssFullTrans.py

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
    git reset --soft 9a4a6017883d78fd382ffc61c4164d73331ddd02
    git commit -m "`date`"
    git push --force
fi

if [ $pingStatus -eq 0 ]
then
    unset http_proxy
    unset https_proxy
fi

