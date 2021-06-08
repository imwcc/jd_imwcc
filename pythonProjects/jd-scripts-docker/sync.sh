#!/bin/bash
trap 'cp /jd-scripts-docker/sync.sh /sync' Exit
(
  exec 2<>/dev/null
  set -e
  cd /jd-scripts-docker
  git pull
) || {
  git clone --branch=main https://github.com/hbstarjason2021/jd-scripts-docker.git /jd-scripts-docker_tmp
  ####git clone --branch=main https://${{ secrets.PAT }}@github.com/hbstarjason2021/jd-scripts-docker.git /jd-scripts-docker_tmp
  
  [ -d /jd-scripts-docker_tmp ] && {
    rm -rf /jd-scripts-docker
    mv /jd-scripts-docker_tmp /jd-scripts-docker
  }
}

#######
(
  exec 2<>/dev/null
  set -e
  cd /scripts
  git pull
) || {
  #git clone --branch=master https://gitee.com/lxk0301/jd_scripts.git /scripts_tmp
  #git clone --branch=main https://github.com/hbstarjason/jd-scripts.git /scripts_tmp
  #git clone --branch=master https://github.com/hbstarjason/jd_scripts.git /scripts_tmp
  #git clone --branch=master https://github.com/hbstarjason/a.git /scripts_tmp
  git clone --branch=jd_scripts-new https://github.com/hbstarjason2021/jd_scripts.git /scripts_tmp
  
  [ -d /scripts_tmp ] && {
    rm -rf /scripts
    mv /scripts_tmp /scripts
  }
}

#######
(
  exec 2<>/dev/null
  set -e
  cd /qx
  git pull
) || {
  #git clone --branch=main https://github.com/i-chenzhe/qx.git /qx_tmp
  git clone --branch=qx https://github.com/hbstarjason2021/jd_scripts.git /qx_tmp  
  [ -d /qx_tmp ] && {
    rm -rf /qx
    mv /qx_tmp /qx
  }
}

########
#(
#  exec 2<>/dev/null
#  set -e
#  cd /Loon
#  git pull
#) || {
  #git clone --branch=main https://github.com/shylocks/Loon.git /Loon_tmp
#  git clone --branch=main https://github.com/chinnkarahoi/Loon.git /Loon_tmp
#  [ -d /Loon_tmp ] && {
#    rm -rf /Loon
#    mv /Loon_tmp /Loon
#  }
#}

#######
(
  exec 2<>/dev/null
  set -e
  cd /ljqailym
  git pull
) || {
  git clone --branch=ljqailym https://github.com/hbstarjason2021/jd_scripts.git /ljqailym_tmp
  [ -d /ljqailym_tmp ] && {
    rm -rf /ljqailym
    mv /ljqailym_tmp /ljqailym
  }
}

#######
(
  exec 2<>/dev/null
  set -e
  cd /jddj
  git pull
) || {
  git clone --branch=jddj-new https://github.com/hbstarjason2021/jd_scripts.git /jddj_tmp
  [ -d /jddj_tmp ] && {
    rm -rf /jddj
    mv /jddj_tmp /jddj
  }
}

#######
(
  exec 2<>/dev/null
  set -e
  cd /scripts-bak
  git pull
) || {
  #git clone --branch=master https://gitlab.com/MrRight/Scripts.git /scripts-bak_tmp
  git clone --branch=dust-new https://github.com/hbstarjason2021/jd_scripts.git /scripts-bak_tmp
  [ -d /scripts-bak_tmp ] && {
    rm -rf /scripts-bak
    mv /scripts-bak_tmp /scripts-bak
  }
}

cd /scripts || exit 1
npm install || npm install --registry=https://registry.npm.taobao.org || exit 1

[ -f /crontab.list ] && {
  cp /crontab.list /crontab.list.old
}
cat /etc/os-release | grep -q ubuntu && {
  cp /jd-scripts-docker/crontab.list /crontab.list
  crontab -r
} || {
  cat /scripts/docker/crontab_list.sh | grep 'node' | sed 's/>>.*$//' | awk '
  BEGIN{
    print("55 */3 * * *  bash /jd-scripts-docker/cron_wrapper bash /sync")
  }
  {
    for(i=1;i<=5;i++)printf("%s ",$i);
    printf("bash /jd-scripts-docker/cron_wrapper \"");
    for(i=6;i<=NF;i++)printf(" %s", $i);
    print "\"";
  }
  ' > /crontab.list
}

cp /crontab.list /crontab.list.old
cp /jd-scripts-docker/crontab.list /crontab.list
cp /jd-scripts-docker/from/jx_cfd.js /scripts/jx_cfd.js
cp /jd-scripts-docker/from/jx_cfd_exchange.js /scripts/jx_cfd_exchange.js
cp /jd-scripts-docker/from/jx_cfdtx.js /scripts/jx_cfdtx.js
cp /jd-scripts-docker/from/jdJxncTokens.js /scripts/jdJxncTokens.js

cp /jd-scripts-docker/from/jd_daydlt.js /scripts/jd_daydlt.js
cp /jd-scripts-docker/from/jdautogan.js /scripts/jdautogan.js

cp /jd-scripts-docker/from/jd_blueCoin_1000.js        /scripts/jd_blueCoin_1000.js
cp /jd-scripts-docker/from/jd_blueCoin_20.js          /scripts/jd_blueCoin_20.js
cp /jd-scripts-docker/from/jd_blueCoin_chunzhen.js    /scripts/jd_blueCoin_chunzhen.js
cp /jd-scripts-docker/from/jd_blueCoin_chunzhenxmy.js /scripts/jd_blueCoin_chunzhenxmy.js

cp /jd-scripts-docker/from/jd_super_redrain.js     /scripts/jd_super_redrain.js
cp /jd-scripts-docker/from/jd_half_redrain.js     /scripts/jd_half_redrain.js
cp /jd-scripts-docker/from/jd_hour_redrain.js     /scripts/jd_hour_redrain.js

cp /jd-scripts-docker/from/jd_mlyjy.js /scripts/jd_mlyjy.js
cp /jd-scripts-docker/from/jd_xmf.js /scripts/jd_xmf.js

cp /jd-scripts-docker/from/jd_jxcfd.js /scripts/jd_jxcfd.js

cp /jd-scripts-docker/from/jd_ShopSign-new.js /scripts/jd_ShopSign-new.js
cp /jd-scripts-docker/from/jd_jintie_wx.js /scripts/jd_jintie_wx.js

cp /jd-scripts-docker/from/jx_cash_sign.js /scripts/jx_cash_sign.js
cp /jd-scripts-docker/from/jd_zoo-new.js /scripts/jd_zoo-new.js

cp /jd-scripts-docker/from/jd_starStore.js /scripts/jd_starStore.js

cp /jd-scripts-docker/from/jd_618redpacket.js /scripts/jd_618redpacket.js
cp /jd-scripts-docker/from/zy_618jc.js /scripts/zy_618jc.js
cp /jd-scripts-docker/from/ddo_pk.js /scripts/ddo_pk.js
cp /jd-scripts-docker/from/jd_gcip.js /scripts/jd_gcip.js
cp /jd-scripts-docker/from/jd_mcxhd_brandcity.js /scripts/jd_mcxhd_brandcity.js

##cp /jd-scripts-docker/from/jd_entertainment.js /scripts/jd_entertainment.js
#cp /qx/jd_entertainment.js /scripts/jd_entertainment.js && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/jd_entertainment.js
##cp /jd-scripts-docker/from/jd_fanslove.js /scripts/jd_fanslove.js
#cp /jd-scripts-docker/from/z_tcl_lining.js /scripts/z_tcl_lining.js

cp /qx/jd_fanslove.js /scripts/jd_fanslove.js && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/jd_fanslove.js
##cp /jd-scripts-docker/from/z_wish.js  /scripts/z_wish.js 
#cp /qx/z_wish.js  /scripts/z_wish.js && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/z_wish.js

#cp /qx/z_lenovo.js     /scripts/z_lenovo.js    && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/z_lenovo.js
#cp /qx/z_mgold.js      /scripts/z_mgold.js     && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/z_mgold.js
#cp /qx/z_super5g.js    /scripts/z_super5g.js   && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/z_super5g.js
#cp /qx/z_city_cash.js  /scripts/z_city_cash.js && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/z_city_cash.js

cp /ljqailym/jd_live_redrain_half.js /scripts/jd_live_redrain_half.js
cp /ljqailym/redman_rain_hr.js       /scripts/redman_rain_hr.js 
cp /ljqailym/redman_rain_hy.js       /scripts/redman_rain_hy.js 
cp /ljqailym/redman_rain_mz.js       /scripts/redman_rain_mz.js 

cp /scripts-bak/normal/adolf_martin.js  /scripts/adolf_martin.js
cp /scripts-bak/normal/adolf_mi.js      /scripts/adolf_mi.js
cp /scripts-bak/normal/adolf_pk.js      /scripts/adolf_pk.js

cp /scripts-bak/normal/adolf_newInteraction.js  /scripts/adolf_newInteraction.js
cp /scripts-bak/normal/adolf_superbox.js        /scripts/adolf_superbox.js
cp /scripts-bak/normal/adolf_urge.js            /scripts/adolf_urge.js

cp /scripts-bak/normal/adolf_jxhb.js            /scripts/adolf_jxhb.js
cp /scripts-bak/normal/adolf_star.js            /scripts/adolf_star.js


cp /scripts-bak/normal/monk_inter_shop_sign.js  /scripts/monk_inter_shop_sign.js  && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/monk_inter_shop_sign.js
cp /scripts-bak/normal/monk_shop_follow_sku.js  /scripts/monk_shop_follow_sku.js  && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/monk_shop_follow_sku.js
cp /scripts-bak/normal/monk_shop_lottery.js     /scripts/monk_shop_lottery.js     && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/monk_shop_lottery.js
cp /scripts-bak/car/monk_shop_add_to_car.js     /scripts/monk_shop_add_to_car.js  && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/monk_shop_add_to_car.js

#cp /scripts-bak/car/adolf_haier.js  /scripts/adolf_haier.js  && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/adolf_haier.js
#cp /scripts-bak/car/adolf_ETIP.js  /scripts/adolf_ETIP.js  && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/adolf_ETIP.js

#cp /scripts-bak/normal/jd_live_lottery_social.js     /scripts/jd_live_lottery_social.js
#cp /scripts-bak/normal/jd_zjd_tuan.js     /scripts/jd_zjd_tuan.js
#cp /scripts-bak/normal/jd_zjd.js     /scripts/jd_zjd.js

cp /scripts-bak/i-chenzhe/z_shop_captain.js   /scripts/z_shop_captain.js
cp /scripts-bak/i-chenzhe/z_fanslove.js   /scripts/z_fanslove.js  && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/z_fanslove.js
cp /scripts-bak/i-chenzhe/z_wish.js  /scripts/z_wish.js    && sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/z_wish.js

cp /scripts-bak/i-chenzhe/z_city_cash.js     /scripts/z_city_cash.js
cp /scripts-bak/i-chenzhe/z_carnivalcity.js  /scripts/z_carnivalcity.js


#cp /jd-scripts-docker/jd_ms.js  /scripts
#cp /jd-scripts-docker/jd_vote.js  /scripts

#cp /jd-scripts-docker/USER_AGENTS.js /Loon
#cp /jd-scripts-docker/jdCookie.js /Loon

#cd /Loon && npm install -g


cd /jddj && npm install request && npm cache clean --force

##################################
sed -i 's/helpAuthor=true/helpAuthor=false/' /scripts/jd_jdzz.js
sed -i "s/eU9YL5XqGLxSmRSAkwxR@eU9YaO7jMvwh-W_VzyUX0Q@eU9YaurkY69zoj3UniVAgg@eU9YaOnjYK4j-GvWmXIWhA@eU9YMZ_gPpRurC-foglg@eU9Ya77gZK5z-TqHn3UWhQ@eU9Yaui2ZP4gpG-Gz3EThA@eU9YaeizbvQnpG_SznIS0w/S5KkcRx4QplfTKUz1l6UPdQ@S97g7GU9KrQGJYUM@S6Lh2RRwZrw2Jdw@S_bkiAkRItguJ/g" /scripts/jd_jdzz.js
sed -i "s/-4msulYas0O2JsRhE-2TA5XZmBQ@eU9Yar_mb_9z92_WmXNG0w@eU9YaO7jMvwh-W_VzyUX0Q@eU9YaurkY69zoj3UniVAgg@eU9YaOnjYK4j-GvWmXIWhA@eU9YaO23bvtyozuGyHsR1A/S5KkcRx4QplfTKUz1l6UPdQ@S97g7GU9KrQGJYUM@S6Lh2RRwZrw2Jdw@S_bkiAkRItguJ/g" /scripts/jd_jdzz.js

sed -i 's/helpAuthor = true/helpAuthor = false/' /scripts/jd_cash.js
sed -i "s/eU9YL5XqGLxSmRSAkwxR@eU9YaO7jMvwh-W_VzyUX0Q@eU9YaurkY69zoj3UniVAgg@eU9YaOnjYK4j-GvWmXIWhA@eU9YMZ_gPpRurC-foglg@eU9Ya77gZK5z-TqHn3UWhQ@eU9Yaui2ZP4gpG-Gz3EThA@eU9YaeizbvQnpG_SznIS0w/eU9Ya-y7Nf8i-DjUyCEW1w@al5_Nb3hPql4sDc@dV4yae6yPKV4pg@YF9mLrbjJaN4/g" /scripts/jd_cash.js
sed -i "s/-4msulYas0O2JsRhE-2TA5XZmBQ@eU9Yar_mb_9z92_WmXNG0w@eU9YaO7jMvwh-W_VzyUX0Q@eU9YaurkY69zoj3UniVAgg@eU9YaOnjYK4j-GvWmXIWhA@eU9YaO23bvtyozuGyHsR1A/eU9Ya-y7Nf8i-DjUyCEW1w@al5_Nb3hPql4sDc@dV4yae6yPKV4pg@YF9mLrbjJaN4/g" /scripts/jd_cash.js

sed -i "s/28a699ac78d74aa3b31f7103597f8927@2f14ee9c92954cf79829320dd482bf49@fdf827db272543d88dbb51a505c2e869@ce2536153a8742fb9e8754a9a7d361da@38ba4e7ba8074b78851e928af2b4f6b2/cada6cf13e48414d971a92bdba5375e8@5abc6697f1e34f8f8e14d7145a123a4c@ac3821ebe5ba4e69a097255fb57a6db6@1afd0390d67148e68e32808922be6c4f/g" /scripts/jd_bookshop.js
sed -i "s/28a699ac78d74aa3b31f7103597f8927@2f14ee9c92954cf79829320dd482bf49@fdf827db272543d88dbb51a505c2e869/cada6cf13e48414d971a92bdba5375e8@5abc6697f1e34f8f8e14d7145a123a4c@ac3821ebe5ba4e69a097255fb57a6db6@1afd0390d67148e68e32808922be6c4f/g" /scripts/jd_bookshop.js

sed -i 's/helpAu = true/helpAu = false/' /scripts/jd_dreamFactory.js
sed -i 's/helpAu = true/helpAu = false/' /scripts/jd_bean_home.js

sed -i "s/T019-aknAFRllhyoQlyI46gCjVfnoaW5kRrbA@T0225KkcRhcbp1CBJhv0wfZedQCjVfnoaW5kRrbA@T010_aU6SR8Q_QCjVfnoaW5kRrbA@T0225KkcREtN9lOGJUinl_dfcwCjVfnoaW5kRrbA@T0225KkcRBYdoFaGIxOnnPMJdACjVfnoaW5kRrbA@T027Zm_olqSxIOtH97BATGmKoWraLawCjVfnoaW5kRrbA@T0225KkcRk1N_FeCJhv3xvdfcQCjVfnoaW5kRrbA/T0225KkcRx4QplfTKUz1l6UPdQCjVfnoaW5kRrbA@T01597g7GU9KrQGJYUMCjVfnoaW5kRrbA@T0146Lh2RRwZrw2JdwCjVfnoaW5kRrbA@T012_bkiAkRItguJCjVfnoaW5kRrbA/g" /scripts/jd_health.js

sed -i "s/xBd-HlYMlLUzqSkuz0qzAzuayqOG3FfAIeOTGLowr29_KbnH2bV4EX4@RtGKzr_wSAn2eIKZRdRm07jvOMS2zVH-g8ri6aOIZPDcI8v7CA/RtGKz-ytEgmnd9WbFIY21wi0WAby6b7-_TwSjslwpiFLtlxJ2w@VcCtkb33GV_9P9rWW5gzmm8elPMfXOe8z_QdOEEwM3s@SsDgze6kG1P9Kc_WW9R_miwM1wjj9yFbflluWvGc7g@X8G0irb1AlX9Ms_WF5h_mqlwj7Qxo5h2OIxo45-u/g" /scripts/jd_city.js
###################################

crontab -r

crontab /crontab.list || {
  cp /crontab.list.old /crontab.list
  crontab /crontab.list
}
crontab -l
