#!/usr/bin/env bash

echo "check jd_crazy_joy_coin"
count=`ps -ef |grep /jd/scripts/jd_crazy_joy_coin.js |grep -v "grep" |wc -l`
#echo $count
if [ 0 == $count ];then
    echo "run jd_crazy_joy_coin"
    otask /jd/own/hapecoder_JD-SCRIPT/jd_crazy_joy_coin.js &
fi
