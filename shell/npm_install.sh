#!/usr/bin/env bash
local workdir='/jd/scripts'

cd $workdir
npm audit fix
npm i png-js -S
npm install crypto-js
npm install png-js
npm install dotenv

