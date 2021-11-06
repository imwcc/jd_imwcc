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
HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME
if DEBUG:
    import utils_tool
    import parse_yaml
else:
    from utils import parse_yaml, utils_tool

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logging.info(FILE_DIR)

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
# assert HOST_NAME is not None
assert script_name is not None
assert ROOT_DIR is not None

new_scripts_dir = os.path.join(ROOT_DIR, script_name)
logging.info(new_scripts_dir)

# 处理 gua_city.js
def deal_dreamFactory(file_name_obsolute_path, fileName):
    if not os.path.isfile(file_name_obsolute_path):
        logging.error("file_name_obsolute_path {} is not a file".format(file_name_obsolute_path))
        return
    patch_file = os.path.join(FILE_DIR,'patch', 'apply_help_zhaogong_half.patch')
    cmd = "cd {}; git apply {}".format(new_scripts_dir, patch_file)
    logging.info("cmd " + cmd)
    status = os.system(cmd) >> 8
    logging.info("status " + str(status))
    if status > 0:
        logging.error("git apply patch failed: " + str(patch_file))
    else:
        logging.error("git apply patch success " + str(patch_file))


if __name__ == '__main__':
    scripts_list = []

    # 针对单个文件
    for file_name in os.listdir(new_scripts_dir):
        if '.js' not in file_name:
            continue
        if file_name in exclude_file_list:
            logging.info("file {} 在排除列表中".format(file_name))
            continue
        if file_name == "jd_carnivalcity_help.js":
            utils_tool.replace_file_line(os.path.join(new_scripts_dir, file_name), "$.updatePkActivityIdRes = await getAuthorShareCode",
                                        "  $.updatePkActivityIdRes = []")

        if file_name == 'jd_dreamFactory.js':
            deal_dreamFactory(os.path.join(new_scripts_dir, file_name), file_name)

    # 主要针对全局修改
    for file_name in os.listdir(new_scripts_dir):
        if file_name == 'utils' and os.path.isdir(os.path.join(new_scripts_dir, file_name)):
            cmd = 'cp -rf {} {}'.format(os.path.join(new_scripts_dir, file_name), '/jd/scripts')
            if os.path.isdir(os.path.join('/jd/scripts', file_name)):
                cmd = 'cp -rf {}/* {}/{}'.format(os.path.join(new_scripts_dir, file_name), '/jd/scripts', file_name)
            logging.info("run {}".format(cmd))
            os.system(cmd)
            continue

        if file_name == 'function' and os.path.isdir(os.path.join(new_scripts_dir, file_name)):
            cmd = 'cp -rf {} {}'.format(os.path.join(new_scripts_dir, file_name), '/jd/scripts')
            if os.path.isdir(os.path.join('/jd/scripts', file_name)):
                cmd = 'cp -rf {}/* {}/{}'.format(os.path.join(new_scripts_dir, file_name), '/jd/scripts', file_name)
            logging.info("run {}".format(cmd))
            os.system(cmd)
            continue


        if '.js' not in file_name:
            continue
        if file_name in exclude_file_list:
            logging.info("file {} 在排除列表中".format(file_name))
            continue

        absolute_file_name = os.path.join(new_scripts_dir, file_name)
        utils_tool.replace_file_line(os.path.join(new_scripts_dir, file_name), "$.authorMyShareIds = ",
                                     "  $.authorMyShareIds=[];\n")

        utils_tool.replace_file_str(os.path.join(new_scripts_dir, file_name), "await readShareCode()",
                                     "false")

        cmd1 = "cd {}; sed -i 's/const ShHelpAuthorFlag = true/const ShHelpAuthorFlag = false/g' {}".format(
            new_scripts_dir, file_name)
        cmd2 = "cd {};sed -i 's/\$.innerShInviteLists = getRandomArrayElements/ \/\/$.innerShInviteLists = getRandomArrayElements/g' {}".format(
            new_scripts_dir, file_name)

        cmd3 = "cd {}; sed -i 's/$.ShInviteLists.push(...$.ShInviteList,/ \/\/$.ShInviteLists.push(...$.ShInviteList,/g' {}".format(
            new_scripts_dir, file_name)

        # remove_nick_name = "cd {};sed -i 's/$.nickName\ =\ data.data.userInfo.baseInfo.nickname/$.nickName=\"\"/g' {}".format(
        #     new_scripts_dir, file_name)

        remove_nick_name = "cd {};sed -i 's/].nickname/].arvin/g' {}".format(
            new_scripts_dir, file_name)

        cmds = [cmd1, cmd2, cmd3, remove_nick_name]
        for cmd in cmds:
            logging.info("run {}".format(cmd))
            os.system(cmd)
        if os.path.isfile(absolute_file_name) and not file_name.startswith('jd'):
            cmd = 'cp -f {} {}'.format(os.path.join(new_scripts_dir, file_name), '/jd/scripts')
            logging.info("run {}".format(cmd))
            os.system(cmd)
