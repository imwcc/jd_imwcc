import yaml
import requests
import os
import socket
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
HOST_NAME = socket.gethostname()

shop_yaml= requests.get('https://antonvanke.github.io/JDBrandMember/shopid.yaml').content
yaml_result = yaml.load(shop_yaml, Loader=yaml.SafeLoader)

if HOST_NAME == 'jd-arvin':
    shop_id_file = '/jd/config/shop_id.txt'
else:
    shop_id_file = os.path.join(FILE_DIR, 'shop_id.txt')

logging.info("写入文件: " + shop_id_file)
with open(shop_id_file, 'w') as f:
    for i in yaml_result.get('shop_id'):
        f.write(i + '\n')

