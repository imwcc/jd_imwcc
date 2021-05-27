#!/bin/bash

CURRENT_DIR=`pwd`
## 导入通用变量与函数
# . $dir_shell/jshare.sh

function remove_help_pool() {
    check_dir=$1
    cd $check_dir
    if [ $? -ne 0 ]
    then
        echo "目录无法访问: " $check_dir
        return -1
    fi

    temp_file=/tmp/arvin_tempd
    grep -i "readShareCodeRes && readShareCodeRes.code === 200" *.js > $temp_file;
    pwd
    cat temp_file
    awk -v FS=':' '{print  $1}'  $temp_file | xargs   sed -i 's/if\ (readShareCodeRes\ \&\&\ readShareCodeRes.code\ ===\ 200)/if\ (false)/g'
}

#去掉助力
echo "disable help poll"
array=(/jd/own/hapecoder_JD-SCRIPT /jd/own/zero205_JD_tencent_scf /jd/own/imwcc_jd_imwcc /jd/scripts)
for(( i=0;i<${#array[@]};i++)) do
    #${#array[@]}获取数组长度用于循环
    echo "close help pool for:" ${array[i]};
    remove_help_pool ${array[i]}
done;

echo "disable autho tips" #看着烦
if [ -f /jd/scripts/sendNotify.js ]; then
    sed -i 's/desp += author/\/\/desp += author/g'  /jd/scripts/sendNotify.js
else
    echo "warning don't find /jd/scripts/sendNotify.js"
fi

cd $CURRENT_DIR
