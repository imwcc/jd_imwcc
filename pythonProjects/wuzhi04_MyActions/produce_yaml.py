import configparser
import sys
import os
import socket
import yaml

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(FILE_DIR)))
from utils import parse_yaml, utils_tool
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME

RESULT_FILE = os.path.join(FILE_DIR, 'task.yaml')

exclude_file_list = []
exclude_yaml_file_list = []

config = configparser.ConfigParser()
config.read(os.path.join(FILE_DIR, 'exclude.cfg'))
for key in config['EXCLUDE']:
    if key == 'js_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_file_list.append(str(i).strip())
    elif key == 'yaml_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_yaml_file_list.append(str(i).strip())

if HOST_NAME == 'arvin-wang':
    ROOT_DIR = '/home/arvin/code'
elif HOST_NAME == 'ubuntu157362':
    ROOT_DIR = '/home/arvin/code'
else:
    ROOT_DIR = '/jd/own'
# ========================== 不变

if 'jd-arvin' in HOST_NAME:
    new_scripts_dir = os.path.join(ROOT_DIR, 'wuzhi04_MyActions')
else:
    new_scripts_dir = os.path.join(ROOT_DIR, 'MyActions')

script_name = 'MyActions'

if not os.path.exists(new_scripts_dir):
    logging.error("找不到配置文件")
    exit(-1)

if __name__ == '__main__':
    old_crontab_list = []
    result_crontab_list = []

    crontab_list_file = os.path.join(new_scripts_dir, 'docker/crontab_list.sh')
    assert os.path.isfile(crontab_list_file)

    yaml_parse = parse_yaml.parse_yaml()
    result_dic = {}

    result_dic['name'] = script_name
    result_dic['tasks'] = []

    logging.info("exclude js list {}".format(exclude_file_list))
    logging.info("exclude yaml list {}".format(exclude_yaml_file_list))

    with open(crontab_list_file, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('#'):
                continue
            is_find_schedule_cron = False
            if '.js' in line and '*' in line:
                crontab_config = utils_tool.get_crontab_from_line(line)
                js_name = utils_tool.get_js_name(line)
                script_file = os.path.join(new_scripts_dir, js_name)
                env_name = utils_tool.get_env_name(script_file)
                if os.path.isfile(script_file):
                    if js_name in exclude_file_list:
                        logging.warning("skip, due to {} in exclude_file_list".format(js_name))
                        continue
                    temp_dic = {}
                    temp_dic['name'] = env_name
                    temp_dic['file_name'] = js_name
                    temp_dic['script_dir'] = new_scripts_dir
                    temp_dic['schedule_cron'] = crontab_config
                    temp_dic['script_file'] = script_file
                    logging.info(temp_dic)
                    result_dic.get('tasks').append(temp_dic)
                else:
                    logging.error("{} not found".format(script_file))

    with open(RESULT_FILE, 'w', encoding="utf-8") as f:
        yaml.dump(result_dic, f, encoding='utf-8', allow_unicode=True)

    # 加载测试
    with open(RESULT_FILE, 'r', encoding="utf-8") as f:
        yaml.load(f.read(), Loader=yaml.SafeLoader)
