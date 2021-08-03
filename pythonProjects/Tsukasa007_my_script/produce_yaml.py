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
# from utils import sendNotify

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logging.info(FILE_DIR)




RESULT_FILE = os.path.join(FILE_DIR, 'task.yaml')

config = configparser.ConfigParser()
config.read(os.path.join(FILE_DIR, 'exclude.cfg'))

exclude_file_list = []
exclude_yaml_file_list = []
white_files_list = [] #忽律警告信息用



script_name = None
ROOT_DIR = None
check_cron_in_js_line = False

HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME
if not DEBUG:
    config_name = 'CONFIG'
else:
    config_name = 'DEBUG_CONFIG'

for key in config['EXCLUDE']:
    if key == 'js_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_file_list.append(str(i).strip())
    elif key == 'yaml_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_yaml_file_list.append(str(i).strip())
    elif key == 'js_white_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            white_files_list.append(str(i).strip())

for key in config[config_name]:
    if key == 'script_name':
        script_name = config.get(config_name, key)
    elif key == 'root_dir':
        ROOT_DIR = config.get(config_name, key)
    elif key == 'check_cron_in_js_line':
        check_cron_in_js_line = config.get(config_name, key).lower() == 'true'
    else:
        logging.error("不支持的 key: " + key)

logging.info("script_name ROOT_DIR {} {}".format(script_name, ROOT_DIR))
assert HOST_NAME is not None
assert script_name is not None
assert ROOT_DIR is not None

new_scripts_dir = os.path.join(ROOT_DIR, script_name)
logging.info(new_scripts_dir)

parse_task_file = os.path.join(new_scripts_dir, 'sync.sh')
# ===================修改 end =================
if not os.path.exists(new_scripts_dir):
    logging.error("找不到新脚本目录: {}".format(new_scripts_dir))
    exit(-1)

logging.info("脚本目录: {}".format(new_scripts_dir))
logging.info("脚本原始配置文件: {}".format(parse_task_file))

if __name__ == '__main__':
    result_dic = {}

    result_dic['name'] = script_name
    result_dic['tasks'] = []

    untrack_files_list = []
    unable_read_crontab_files_list = []

    logging.info("exclude js list {}".format(exclude_file_list))
    logging.info("exclude yaml list {}".format(exclude_yaml_file_list))

    scripts_list = []
    for file_name in os.listdir(new_scripts_dir):
        if '.js' not in file_name:
            continue
        if file_name in exclude_file_list:
            logging.info("file {} 在排除列表中".format(file_name))
            continue
        scripts_list.append(file_name)

    for script_name in scripts_list:
        script_path = os.path.join(new_scripts_dir, script_name)
        with open(script_path, 'r') as f:
            is_find_schedule_cron = False
            is_find_Env = False
            crontab_config = None
            schedule_name = None
            logging.info("开始解析: " + script_name)
            for line in f.readlines():
                if check_cron_in_js_line:
                    if not ('.js' in line and '*' in line and not is_find_schedule_cron):
                        continue
                    # else:
                    #     logging.info("开始检查目标行: " + line)

                if not is_find_schedule_cron:
                    line = line.strip()
                    is_good = False
                    count = 0
                    index_begin = -1
                    for index, ch in enumerate(line):
                        if (str(ch).isdigit() or str(ch) == '*') and index_begin < 0:
                            # logging.info("目标行开始check:")
                            # logging.info(line)
                            is_good = True
                            count += 1
                            index_begin = index
                            continue
                        if is_good:
                            if str(ch).isdigit() or str(ch) == '*' or str(ch) == ',' or str(ch) == ' ' or str(ch) == '/' \
                                    or str(ch) == '-':
                                count += 1
                                if count == len(line):
                                    is_find_schedule_cron = True
                                    crontab_config = str(line[index_begin:index]).strip()
                                continue
                            else:
                                if count >= 10:
                                    # logging.info('=====start =====')
                                    # logging.info(line[index_begin:index])
                                    # logging.info('=====end =====')
                                    is_find_schedule_cron = True
                                    crontab_config = str(line[index_begin:index]).strip()
                                else:
                                    pass
                                    # logging.info('=====错误 begin=====')
                                    # logging.info(count)
                                    # logging.info(index_begin)
                                    # logging.info(index)
                                    # logging.info(line)
                                    # logging.info('====错误 end======')
                                break
                    # logging.info('file: ' + script_name)
                    # logging.info(line)
                elif "new Env" in line:
                    begin_index = line.find('new Env') + 8
                    end_index = -1
                    for index, ch in enumerate(line):
                        if str(ch) == ')':
                            end_index = index
                    # logging.info(line)
                    # logging.info(type(begin_index))
                    # logging.info(type(end_index))
                    # logging.info(begin_index, end_index)
                    schedule_name = str(line[begin_index:end_index]).replace("'", "").replace("\"", "")
                    # logging.info("名字: {}".format(schedule_name))
                    is_find_Env = True
                elif "new API" in line:
                    begin_index = line.find('new API') + 8
                    end_index = -1
                    for index, ch in enumerate(line):
                        if str(ch) == ')':
                            end_index = index
                    # logging.info(line)
                    # logging.info(type(begin_index))
                    # logging.info(type(end_index))
                    # logging.info(begin_index, end_index)
                    schedule_name = str(line[begin_index:end_index]).replace("'", "").replace("\"", "")
                    # logging.info("名字: {}".format(schedule_name))
                    is_find_Env = True
            if is_find_Env:
                assert schedule_name is not None
                if is_find_schedule_cron:
                    assert crontab_config is not None
                    # logging.info('schedule_cron: ' + crontab_config)
                else:
                    logging.info("定时器解析失败,使用默认配置 {}".format(script_name))
                    crontab_config = "30 0 * * *"
                    if script_name not in white_files_list:
                        unable_read_crontab_files_list.append(script_name)

                temp_dic = {}
                temp_dic['name'] = schedule_name
                temp_dic['file_name'] = script_name
                temp_dic['script_dir'] = new_scripts_dir
                temp_dic['schedule_cron'] = crontab_config
                temp_dic['script_file'] = script_path
                logging.info(temp_dic)

                result_dic.get('tasks').append(temp_dic)
            else:
                logging.error("没有找到Env信息： {}".format(script_path))
                untrack_files_list.append(script_name)

    with open(RESULT_FILE, 'w', encoding="utf-8") as f:
        yaml.dump(result_dic, f, encoding='utf-8', allow_unicode=True)

    # 加载测试
    with open(RESULT_FILE, 'r', encoding="utf-8") as f:
        yaml.load(f.read(), Loader=yaml.SafeLoader)

    logging.info("=========untrack_files_list begin ===========")
    logging.info("{}".format(','.join(untrack_files_list)))
    logging.info("=========untrack_files_list end ===========")

    logging.info("=========unable_read_crontab_files_list begin ===========")
    logging.info("{}".format(','.join(unable_read_crontab_files_list)))
    logging.info("=========unable_read_crontab_files_list end ===========")
