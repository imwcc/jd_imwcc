import configparser
import sys
import os
import socket
import logging
import tempfile

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(FILE_DIR)))
# sys.path.append("..")
# from utils import sendNotify

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logging.info(FILE_DIR)

HOST_NAME = socket.gethostname()
DEBUG = HOST_NAME != 'jd-arvin'

RESULT_FILE = os.path.join(FILE_DIR, 'task.yaml')

config = configparser.ConfigParser()
config.read(os.path.join(FILE_DIR, 'exclude.cfg'))

exclude_file_list = []
exclude_yaml_file_list = []
white_files_list = []  # 忽律警告信息用

HOST_NAME = None
script_name = None
ROOT_DIR = None
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
    if key == 'host_name':
        HOST_NAME = config.get(config_name, key).replace('\n', '')
    elif key == 'script_name':
        script_name = config.get(config_name, key)
    elif key == 'root_dir':
        ROOT_DIR = config.get(config_name, key)
    else:
        logging.error("不支持的 key: " + key)

logging.info("HOST_NAME script_name ROOT_DIR {} {} {}".format(HOST_NAME, script_name, ROOT_DIR))
assert HOST_NAME is not None
assert script_name is not None
assert ROOT_DIR is not None

new_scripts_dir = os.path.join(ROOT_DIR, script_name)
logging.info(new_scripts_dir)

if __name__ == '__main__':
    scripts_list = []

    cmd = '''sed -i  's/await exec(`\${process.execPath} \${JD_DailyBonusPath} >> \${resultPath}`);/ await exec(`bash -x -D -l -c  \" \${process.execPath} \/jd\/scripts\/\${JD_DailyBonusPath}\"`/g' jd_bean_sign.js'''

    os.system('cd {};{}'.format(new_scripts_dir, cmd))
