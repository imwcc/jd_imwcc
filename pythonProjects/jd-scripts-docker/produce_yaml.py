import configparser
import re
import sys
import os
import demjson
import socket
import yaml
import logging
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(FILE_DIR)))
# sys.path.append("..")
from utils import sendNotify

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
print(FILE_DIR)

HOST_NAME = socket.gethostname()
DEBUG = HOST_NAME != 'jd-arvin'

RESULT_FILE = os.path.join(FILE_DIR, 'task.yaml')

config = configparser.ConfigParser()
config.read(os.path.join(FILE_DIR, 'exclude.cfg'))

exclude_file_list = []
exclude_yaml_file_list = []
notify = sendNotify.sendNotify()

for key in config['EXCLUDE']:
    if key == 'js_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_file_list.append(str(i).strip())
    elif key == 'yaml_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_yaml_file_list.append(str(i).strip())

#===================修改 start=================
if HOST_NAME == 'arvin-wang':
    ROOT_DIR = '/home/arvin/code'

elif HOST_NAME == 'jd-arvin':
    ROOT_DIR = '/jd/own'

elif HOST_NAME == 'ubuntu157362':
    ROOT_DIR = '/home/arvin/code'
script_name = 'jd-scripts-docker'

if HOST_NAME == 'jd-arvin':
    new_scripts_dir = os.path.join(ROOT_DIR, 'hbstarjason2021_jd-scripts-docker')
else:
    new_scripts_dir = os.path.join(ROOT_DIR, script_name)

parse_task_file = os.path.join(new_scripts_dir, 'sync.sh')
#===================修改 end =================
if not os.path.exists(new_scripts_dir):
    logging.error("找不到新脚本目录")
    exit(-1)
if not os.path.isfile(parse_task_file):
    logging.error("找不到配置脚本文件")
    exit(-1)
logging.info("脚本目录: {}".format(new_scripts_dir))
logging.info("脚本原始配置文件: {}".format(parse_task_file))

if __name__ == '__main__':
    result_dic = {}

    result_dic['name'] = script_name
    result_dic['tasks'] = []

    logging.info("exclude js list {}".format(exclude_file_list))
    logging.info("exclude yaml list {}".format(exclude_yaml_file_list))

    with open(parse_task_file, 'r') as f:
        for line in f.readlines():
            line = line.strip().replace('\n', '')

            # 1. 找到from 中enable的 js 文件
            jsFromFile = None

            if line.startswith('cp '):
                for i in line.split():
                    if '.js' in i and 'from' in i:
                        jsFromFile = i.split('/')[-1]
                        break

            #2. 找到enable 文件的配置
            if jsFromFile != None:
                logging.info("文件名: " + jsFromFile)
                task_of_config = None
                with open(os.path.join(new_scripts_dir, 'from', jsFromFile), 'r') as f:
                    for line in f.readlines():
                        line = line.replace('/n', '').strip()
                        if line.startswith('cron '):
                            # logging.info(line)
                            print(line)
                            task_of_config = line
                            break
                # 3. 根据task_of_config 解析
                if task_of_config == None:
                    logging.error("找不到 cron 配置文件，请手动配置: " + jsFromFile)
                else:
                    re_str = str_pat = re.compile(r'\"(.*)\"')
                    if len(re_str.findall(task_of_config)) == 1:
                        schedule_time = re_str.findall(task_of_config)[0]
                    else:
                        logging.error("找不到 schedule_time :" + task_of_config)
                        continue

                    if len(task_of_config.split('tag=')) > 1 and task_of_config.split('tag=')[-1] != '':
                        schedule_name = task_of_config.split('tag=')[-1]
                    else:
                        logging.error("找不到 schedule_name :" + task_of_config)
                        continue
                    temp_dic = {}
                    temp_dic['name'] = schedule_name
                    temp_dic['file_name'] = jsFromFile
                    temp_dic['script_dir'] = new_scripts_dir
                    temp_dic['schedule_cron'] = schedule_time
                    temp_dic['script_file'] = os.path.join(new_scripts_dir, 'from', jsFromFile)
                    print(temp_dic)
                    result_dic.get('tasks').append(temp_dic)

    with open(RESULT_FILE, 'w', encoding="utf-8") as f:
        yaml.dump(result_dic, f, encoding='utf-8', allow_unicode=True)

    # 加载测试
    with open(RESULT_FILE, 'r', encoding="utf-8") as f:
        yaml.load(f.read(), Loader=yaml.SafeLoader)
