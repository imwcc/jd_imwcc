#!/usr/bin/env bash
local workdir='/jd/scripts'

cd $workdir
#npm audit fix --save --registry=https://registry.npm.taobao.org
npm i -g png-js  --registry=https://registry.npm.taobao.org
npm install -g crypto-js  --registry=https://registry.npm.taobao.org
npm install -g png-js  --registry=https://registry.npm.taobao.org
npm install -g  dotenv  --registry=https://registry.npm.taobao.org
npm install -g  tough-cookie 
