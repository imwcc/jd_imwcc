#!/usr/bin/env bash
local workdir='/jd/scripts'

cd $workdir
npm audit fix --save --registry=https://registry.npm.taobao.org
npm i png-js -S --save --registry=https://registry.npm.taobao.org
npm install crypto-js --save --registry=https://registry.npm.taobao.org
npm install png-js --save --registry=https://registry.npm.taobao.org
npm install dotenv --save --registry=https://registry.npm.taobao.org

