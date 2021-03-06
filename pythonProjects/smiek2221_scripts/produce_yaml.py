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

HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME

if DEBUG:
    import utils_tool
    import parse_yaml
    from ConfigParse import ConfigParse
else:
    from utils import parse_yaml, utils_tool
    from utils.ConfigParse import ConfigParse

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logging.info(FILE_DIR)

# ===============不变 begin ===========================
RESULT_FILE = os.path.join(FILE_DIR, 'task.yaml')
config = configparser.ConfigParser()
config.read(os.path.join(FILE_DIR, 'exclude.cfg'))
config = ConfigParse(os.path.join(FILE_DIR, 'exclude.cfg'), DEBUG)
exclude_file_list = config.get_exclude_js_exclude_files()
exclude_yaml_file_list = config.get_exclude_yaml_exclude_files()
ROOT_DIR = config.get_config_root_dir()
new_scripts_dir = os.path.join(ROOT_DIR, config.get_config_script_name())
script_name = config.get_config_script_name()
logging.info("HOST_NAME script_name ROOT_DIR {} {} {}".format(HOST_NAME, script_name, ROOT_DIR))
assert HOST_NAME is not None
assert script_name is not None
assert ROOT_DIR is not None
assert os.path.isdir(new_scripts_dir)
# ===============不变 END ===========================

white_files_list = config.get_exclude_js_white_files()

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
            for line in f.readlines():
                if '.js' in line and '*' in line and not is_find_schedule_cron:
                    line = line.strip()
                    is_good = False
                    count = 0
                    index_begin = -1
                    for index, ch in enumerate(line):
                        if (str(ch).isdigit() or str(ch) == '*') and index_begin < 0:
                            is_good = True
                            count += 1
                            index_begin = index
                            continue
                        if is_good:
                            if str(ch).isdigit() or str(ch) == '*' or str(ch) == ',' or str(ch) == ' ' or str(ch) == '/' \
                                    or str(ch) == '-':
                                count += 1
                                continue
                            else:
                                if count >= 5:
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
                logging.info("没有找到Env信息： {}".format(script_path))
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
