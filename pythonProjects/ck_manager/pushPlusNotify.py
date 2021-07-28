# encoding:utf-8

import requests
import json
import logging


def pushPlusNotify(token, content, title='京东脚本通知', topic=''):
    url = 'http://www.pushplus.plus/send'
    if topic != '':
        body = {
            "token": token,
            "title": title,
            "content": content,
            "template": "txt",
            "topic": topic,
            "channel": "wechat"
        }
    else:
        body = {
            "token": token,
            "title": title,
            "content": content,
            "template": "txt",
            "channel": "wechat"
        }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(url, data=json.dumps(body), headers=headers)
        if r.ok and r.json()['code'] == 200:
            logging.info(f'push+发送{title}通知消息完成。')
        else:
            logging.error(f"push+发送{topic}通知消息失败：{r.json()['msg']}")
    except Exception as e:
        logging.error(e)