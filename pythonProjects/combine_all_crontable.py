import socket
import logging
import os
import time

import configparser
import yaml

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

HOST_NAME = socket.gethostname()
DEBUG = 'jd-arvin' not in HOST_NAME

exclude_dir = []
priority_order_list = []
exclude_file_list = []

config = configparser.ConfigParser()
config.read(os.path.join(FILE_DIR, 'combine_all_crontable.cfg'))

for key in config['SCRIPTS']:
    if key == 'priority_order_list':
        for i in config.get('SCRIPTS', key).replace('\n', '').split(','):
            priority_order_list.append(str(i).strip())
    elif key == 'exclude_dir':
        for i in config.get('SCRIPTS', key).replace('\n', '').split(','):
            exclude_dir.append(str(i).strip())

for key in config['EXCLUDE']:
    if key == 'js_exclude_files':
        for i in config.get('EXCLUDE', key).replace('\n', '').split(','):
            exclude_file_list.append(str(i).strip())

logging.info("exclude dir {}".format(exclude_dir))
logging.info("scripts_config dir {}".format(priority_order_list))
logging.info("exclude_file_list {}".format(exclude_file_list))

if 'jd-arvin' in HOST_NAME:
    ROOT_DIR = '/jd/own'
    crontab_imwcc_file = '/jd/own/imwcc_jd_imwcc/imwcc_crontab.list'
    crontab_result_file = '/jd/config/crontab.list'

else:
    ROOT_DIR = FILE_DIR
    crontab_result_file = os.path.join(ROOT_DIR, 'crontab.list')

old_crontab_list_file = crontab_result_file

if __name__ == '__main__':
    old_crontab_list = []  # Save the existing crontab
    result_crontab_list = []
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if os.path.isfile(old_crontab_list_file):
        with open(old_crontab_list_file, 'r') as f:
            for line in f.readlines():
                line = line.strip().replace('\n', '')
                if line.strip() == '':
                    continue
                # 忽略被注释的 crontab, 请保留注释
                # elif line.startswith('#'):
                #     continue

                if '.js' in line and ('jtask' in line or 'otask' in line):
                    for key in line.split(' '):
                        key = key.strip().replace(' ', '')
                        if key == '':
                            continue
                        if '.js' in key and '/' in key:
                            old_crontab_list.append(key)
                            if not os.path.isfile(key):
                                logging.warning("js crontab 路径失效: " + str(key))

                elif '.py' in line and 'python' in line:
                    for key in line.split(' '):
                        key = key.strip().replace(' ', '')
                        if key == '':
                            continue
                        if '.py' in key and '/' in key:
                            old_crontab_list.append(key)
                            if not os.path.isfile(key):
                                logging.warning("py crontab 路径失效: " + str(key))

    # 1, 统计own
    result_crontab_list = []
    result_crontab_list_file_name = []
    result_crontab_list_env_name = []
    
    # 执行diy change 文件:
    logging.info("执行diy change")
    for i in priority_order_list:
        diy_change_file = os.path.join(FILE_DIR, i, 'diy_change.py')
        if os.path.isfile(diy_change_file):
            logging.info('python3 {}'.format(diy_change_file))
            status = os.system('python3 {}'.format(diy_change_file))
            if status != 0:
                logging.error('python3 {} failed'.format(diy_change_file))
                exit(-1)

    # 生成yaml 文件:
    for i in priority_order_list:
        produce_yaml_file = os.path.join(FILE_DIR, i, 'produce_yaml.py')
        if os.path.isfile(produce_yaml_file):
            logging.info('python3 {}'.format(produce_yaml_file))
            os.system('python3 {}'.format(produce_yaml_file))
        else:
            logging.error("生成yaml文件不存在,将使用旧文件: ".format(produce_yaml_file))

    for i in priority_order_list:
        task_yaml_file = os.path.join(FILE_DIR, i, 'task.yaml')
        temp_crontab_list = []
        logging.info("开始解析: {}".format(task_yaml_file))
        if os.path.isfile(task_yaml_file):
            try:
                with open(task_yaml_file, 'r') as f:
                    yaml_result = yaml.load(f.read(), Loader=yaml.SafeLoader)
                    for task in yaml_result.get('tasks'):
                        comment = task['name']
                        schedule_cron = task['schedule_cron']
                        script_file_name = str(task['file_name'])
                        script_file_absolute_path = task['script_file']

                        if script_file_name in exclude_file_list:
                            logging.info("{} 在排除列表中, 忽略".format(script_file_name))
                            continue

                        if script_file_name in result_crontab_list_file_name:
                            logging.info("{} Name: {} 已经存在于上次循环".format(str(i), script_file_name))
                            continue
                        if comment in result_crontab_list_env_name:
                            logging.warning("{} env name: {} 已经存在于上次循环".format(str(comment)))
                            continue

                        is_in_old_crontab = False
                        # 判斷是否在 老旧的 crontabl list 配置中， 若是 退出
                        for jd_scripts_line_item in old_crontab_list:
                            if script_file_name in str(jd_scripts_line_item):
                                is_in_old_crontab = True
                                logging.info("{} 已经存在于 {}".format(script_file_name, jd_scripts_line_item))
                                break
                        if is_in_old_crontab:
                            continue
                        temp_crontab_list.append("# {}".format(comment))
                        if script_file_name.endswith('.py'):
                            crontab_item = "{} python3 {}".format(schedule_cron, script_file_absolute_path)
                        else:
                            crontab_item = "{} otask {}".format(schedule_cron, script_file_absolute_path)
                        temp_crontab_list.append(crontab_item)
                        result_crontab_list_file_name.append(script_file_name)
                        result_crontab_list_env_name.append(comment)

            except Exception as e:
                logging.error(e)
        else:
            logging.error("{} 不存在".format(os.path.join(FILE_DIR, i)))

        if len(temp_crontab_list) > 0:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            result_crontab_list.append("# =========== {} start {}  ==============".format(i, current_time))
            for j in temp_crontab_list:
                result_crontab_list.append(j)
            result_crontab_list.append("# =========== {} end {}  ==============\n".format(i, current_time))

    logging.info("============================= 分割线 =====================================")
    if len(result_crontab_list) > 0:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(crontab_result_file, 'a+') as f:
            for line in result_crontab_list:
                logging.info(line)
                f.write(line + '\n')
