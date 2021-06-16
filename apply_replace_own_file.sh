#!/usr/bin/env bash

echo "cp -f /jd/own/imwcc_jd_imwcc/jd_factory.js /jd/own/hapecoder_JD-SCRIPT"

cp -f /jd/own/imwcc_jd_imwcc/jd_factory.js /jd/own/hapecoder_JD-SCRIPT

cp -f /jd/own/imwcc_jd_imwcc/jshare.sh  /jd

echo "force update scripts"
cp -f  /jd/own/imwcc_jd_imwcc/jd_syj.js  /jd/scripts
# cp -f /jd/own/imwcc_jd_imwcc/jd_city.js  /jd/scripts
cp -f /jd/own/imwcc_jd_imwcc/jd_try.js   /jd/scripts
#cp -f  /jd/own/imwcc_jd_imwcc/jd_bean_change.js /jd/scripts
cp -f /jd/own/imwcc_jd_imwcc/jd_pk.js /jd/scripts

