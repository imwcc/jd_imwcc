#!/usr/bin/env bash

#target_file='jcode.sh'
#code_from_path='default_code.config'

target_file='/jd/jcode.sh'
code_from_path='/jd/own/imwcc_jd_imwcc/default_code.config'

#imwcc1是打桩标志
stake=`sed -n -e '/imwcc1/=' ${target_file}`
if [ ! -n "$stake" ]; then  
   let line_number=`sed -n -e '/$config_name_my$j='$tmp_my_code'/=' ${target_file}`
   let line_number-=1
   sed  "${line_number} r ${code_from_path}" $target_file > /tmp/temp_code
   cp -f /tmp/temp_code $target_file
   echo "jcode imwcc1 打入成功"
   #sed  '58 r default_code.config' $target_file
else  
  echo "jcode imwcc1 已经打入"
fi
