#!/usr/bin/env bash

function check_hang_task(){
  count=`ps -ef |grep $1 |grep -v "grep" |wc -l`
  #echo $count
  if [ 0 == $count ];then
    jtask $1 &
  fi
}

check_hang_task /jd/scripts/jd_crazy_joy_coin.js

