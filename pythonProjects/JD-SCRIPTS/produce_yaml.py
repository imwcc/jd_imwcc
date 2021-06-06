import configparser
import sys
import os
import socket
import yaml
sys.path.append("..")
from utils import parse_yaml

import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
print(FILE_DIR)

HOST_NAME = socket.gethostname()
DEBUG = HOST_NAME != 'jd-arvin'

RESULT_FILE = os.path.join(FILE_DIR, 'task.yaml')

config = configparser.ConfigParser()
config.read('exclude.cfg')

exclude_file_list = []
exclude_yaml_file_list = []

for key in config['EXCLUDE']:
    if key == 'js_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_file_list.append(str(i).strip())
    elif key == 'yaml_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_yaml_file_list.append(str(i).strip())

if HOST_NAME == 'arvin-wang':
    ROOT_DIR = '/home/arvin/code'

elif HOST_NAME == 'jd-arvin':
    ROOT_DIR = '/jd/own'

elif HOST_NAME == 'ubuntu157362':
    ROOT_DIR = '/home/arvin/code'

if HOST_NAME == 'jd-arvin':
    new_scripts_dir = os.path.join(ROOT_DIR, 'hapecoder_JD-SCRIPT')
else:
    new_scripts_dir = os.path.join(ROOT_DIR, 'JD-SCRIPT')

if not os.path.exists(new_scripts_dir):
    logging.error("找不到配置文件")
    exit(-1)

if __name__ == '__main__':
    old_crontab_list = []
    result_crontab_list = []

    yaml_dir = os.path.join(new_scripts_dir, '.github/workflows')
    yaml_files = os.listdir(yaml_dir)

    yaml_parse = parse_yaml.parse_yaml()
    result_dic = {}
    result_dic['name'] = "JD-SCRIPTS"
    result_dic['tasks'] = []

    logging.info("exclude js list {}".format(exclude_file_list))
    logging.info("exclude yaml list {}".format(exclude_yaml_file_list))

    for yaml_file in yaml_files:
        try:

            if yaml_file in exclude_yaml_file_list:
                logging.info("yaml file {} In exclude list".format(yaml_dic.get('yaml_file_name')))
                continue

            yaml_dic = yaml_parse.begin_parse_file(os.path.join(yaml_dir, yaml_file), new_scripts_dir)
            if yaml_dic is not None and yaml_dic != {}:
                print(yaml_dic)
                if yaml_dic.get('file_name') in exclude_yaml_file_list:
                    logging.info("js file {} In exclude list".format(yaml_dic.get('file_name')))
                    continue
                result_dic['tasks'].append(yaml_dic)
        except Exception as e:
            logging.error(yaml_file)
            logging.error(str(e))

    print(result_dic)
    with open(RESULT_FILE, 'w', encoding="utf-8") as f:
        yaml.dump(result_dic, f, encoding='utf-8', allow_unicode=True)

    # 加载测试
    with open(RESULT_FILE, 'r', encoding="utf-8") as f:
        yaml.load(f.read(), Loader=yaml.SafeLoader)
