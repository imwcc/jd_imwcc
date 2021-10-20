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
else:
    from utils import parse_yaml, utils_tool
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)




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

scripts_dir = None
script_name = None
ROOT_DIR = None
if DEBUG:
    config_key = "DEBUG_CONFIG"
else:
    config_key = "CONFIG"

print(config[config_key])
for key in config[config_key]:
    if key == 'script_name':
        scripts_dir = script_name = config.get(config_key, key).replace('\n', '')
    elif key == 'root_dir':
        ROOT_DIR = config.get(config_key, key).replace('\n', '')
    else:
        logging.info("不能识别的config key: " + key)

# ========================== 不变
assert scripts_dir is not None
assert script_name is not None
assert ROOT_DIR is not None

new_scripts_dir = os.path.join(ROOT_DIR, scripts_dir)
logging.info("new_scripts_dir->" + new_scripts_dir)

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

    with open(RESULT_FILE, 'w', encoding="utf-8") as f:
        yaml.dump(result_dic, f, encoding='utf-8', allow_unicode=True)

    # 加载测试
    with open(RESULT_FILE, 'r', encoding="utf-8") as f:
        yaml.load(f.read(), Loader=yaml.SafeLoader)
