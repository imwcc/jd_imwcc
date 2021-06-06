import socket
import logging
import os
import time

import yaml

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

HOST_NAME = socket.gethostname()
DEBUG = HOST_NAME != 'jd-arvin'

exclude_dir = ['test']

priority_order_list = ['JD_tencent_scf', 'JD-SCRIPTS']

if HOST_NAME == 'jd-arvin':
    ROOT_DIR = '/jd/own'
    crontab_imwcc_file = '/jd/own/imwcc_jd_imwcc/imwcc_crontab.list'
    crontab_result_file = '/jd/config/crontab.list'

else:
    ROOT_DIR = FILE_DIR
    crontab_result_file = os.path.join(ROOT_DIR, 'crontab.list')

old_crontab_list_file = crontab_result_file

if __name__ == '__main__':
    old_crontab_list = []
    result_crontab_list = []
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if os.path.isfile(old_crontab_list_file):
        with open(old_crontab_list_file, 'r') as f:
            for line in f.readlines():
                line = line.strip().replace('\n', '')
                if line.strip() == '':
                    continue
                elif line.startswith('#'):
                    continue
                elif '.js' not in line and 'jtask' not in line:
                    continue
                if '.js' in line:
                    for i in line.split():
                        if '.js' in i:
                            old_crontab_list.append(line.strip())
                elif 'jtask' in line:
                    old_crontab_list.append(line.split('jtask')[-1].strip() + '.js')

    # 1, 统计own
    result_crontab_list = []
    result_crontab_list_file_name = []

    for i in priority_order_list:
        task_yaml_file = os.path.join(FILE_DIR, i, 'task.yaml')
        temp_crontab_list = []
        if os.path.isfile(task_yaml_file):
            try:
                with open(task_yaml_file, 'r') as f:
                    yaml_result = yaml.load(f.read(), Loader=yaml.SafeLoader)
                    for task in yaml_result.get('tasks'):
                        comment = task['name']
                        schedule_cron = task['schedule_cron']
                        script_file_name = str(task['file_name'])
                        script_file_absolute_path = task['script_file']
                        print(comment, schedule_cron, script_file_name, script_file_absolute_path)

                        if script_file_name in result_crontab_list_file_name:
                            logging.info("{} Name: {} 已经存在于上次循环".format(str(i), script_file_name))
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

                        comment = "# {}".format(comment)
                        temp_crontab_list.append(comment)
                        crontab_item = "{} otask {}".format(schedule_cron, script_file_absolute_path)
                        temp_crontab_list.append(crontab_item)
                        result_crontab_list_file_name.append(script_file_name)

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
