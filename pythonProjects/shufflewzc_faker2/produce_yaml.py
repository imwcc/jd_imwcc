import configparser
import sys
import os
import socket
import yaml

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(FILE_DIR)))
HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME
if DEBUG:
    import utils_tool
    import parse_yaml
    from ConfigParse import ConfigParse
else:
    from utils import parse_yaml, utils_tool
    from utils.ConfigParse import ConfigParse
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

RESULT_FILE = os.path.join(FILE_DIR, 'task.yaml')

config = ConfigParse(os.path.join(FILE_DIR, 'exclude.cfg'), DEBUG)
exclude_file_list = config.get_exclude_js_exclude_files()
exclude_yaml_file_list = config.get_exclude_yaml_exclude_files()

ROOT_DIR = config.get_config_root_dir()
new_scripts_dir = os.path.join(ROOT_DIR, config.get_config_script_name())
script_name = config.get_config_script_name()

assert script_name is not None
assert ROOT_DIR is not None
assert new_scripts_dir is not None

logging.info("new_scripts_dir->" + new_scripts_dir)
if not os.path.exists(new_scripts_dir):
    logging.error("找不到配置文件: {}".format(new_scripts_dir))
    exit(-1)

if __name__ == '__main__':
    old_crontab_list = []
    result_crontab_list = []

    crontab_list_file = os.path.join(new_scripts_dir, 'docker/crontab_list.sh')

    yaml_parse = parse_yaml.parse_yaml()
    result_dic = {}

    result_dic['name'] = script_name
    result_dic['tasks'] = []

    logging.info("exclude js list {}".format(exclude_file_list))
    logging.info("exclude yaml list {}".format(exclude_yaml_file_list))
    if os.path.isfile(crontab_list_file):
        with open(crontab_list_file, 'r', encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                logging.info("line: " + line)
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

                elif '.py' in line and '*' in line:
                    crontab_config = utils_tool.get_crontab_from_line(line)
                    py_name = utils_tool.get_py_name(line)
                    script_file = os.path.join(new_scripts_dir, py_name)
                    env_name = utils_tool.get_env_name(script_file)
                    if os.path.isfile(script_file):
                        if js_name in exclude_file_list:
                            logging.warning("skip, due to {} in exclude_file_list".format(js_name))
                            continue
                        temp_dic = {}
                        temp_dic['name'] = env_name
                        temp_dic['file_name'] = py_name
                        temp_dic['script_dir'] = new_scripts_dir
                        temp_dic['schedule_cron'] = crontab_config
                        temp_dic['script_file'] = script_file
                        logging.info(temp_dic)
                        result_dic.get('tasks').append(temp_dic)
                    else:
                        logging.error("{} not found".format(script_file))

    else:
        logging.error("file 不存在: " + str(crontab_list_file))

    # 解析完 docker/crontab_list.sh, 继续解析文件,进行补充, 目前仅仅支持 js
    for file_name in os.listdir(new_scripts_dir):
        if file_name in exclude_file_list:
            logging.info("file_name: {}在排除列表中".format(file_name))
            continue
        if '.js' in file_name:
            crontab_dict = utils_tool.get_full_crontab_dic(os.path.join(new_scripts_dir, file_name))
            if crontab_dict != utils_tool.UN_DEFINE:
                local_not_find = True
                for local_dic_crontab_config in result_dic.get('tasks'):
                    if utils_tool.get_file_name_from_dict(crontab_dict) == utils_tool.get_file_name_from_dict(
                            local_dic_crontab_config):
                        local_not_find = False
                        break
                if local_not_find:
                    result_dic.get('tasks').append(crontab_dict)


    with open(RESULT_FILE, 'w', encoding="utf-8") as f:
        yaml.dump(result_dic, f, encoding='utf-8', allow_unicode=True)

    # 加载测试
    with open(RESULT_FILE, 'r', encoding="utf-8") as f:
        yaml.load(f.read(), Loader=yaml.SafeLoader)
