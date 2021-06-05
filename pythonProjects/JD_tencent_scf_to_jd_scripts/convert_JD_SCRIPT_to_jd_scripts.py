import json
import os
import demjson
import socket
import time
import yaml

import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
print(FILE_DIR)
# own 目录下面有三种目录优先级:
#   1. scripts 大佬目录
#   2. jd_imwcc 个人自定义脚本
#   3. 其它目录优先级


HOST_NAME = socket.gethostname()
DEBUG = HOST_NAME == 'arvin-wang'

logging.info("DEBUG is {}".format(DEBUG))

exclude_file_list = ['jd_cash_exchange.js', 'jd_adolf_pk.js', 'z_carnivalcity.js', 'jd_jxfactory.js', 'jd_fanslove.js',
                     'jd_shop_lottery.js', 'monk_shop_add_to_car.js', 'jd_shop_follow_sku.js']

exclude_yaml_file_list = ['000000000000.yml', 'getJDCookie.yml', 'jx_total2jxtqz.yml', '20210323jd_dpqd.yml']

if HOST_NAME == 'arvin-wang':
    ROOT_DIR = '/home/arvin/code'
    JD_tencent_scf_dir = os.path.join(ROOT_DIR, 'JD_tencent_scf')
    parse_from_file = os.path.join(ROOT_DIR, 'JD_tencent_scf/jd_task.json')
    scripts_crontab_config = os.path.join(FILE_DIR, 'test_files/crontab.list')
    scripts_jd_imwcc_dir = os.path.join(ROOT_DIR, 'jd_imwcc')

elif HOST_NAME == 'jd-arvin':
    ROOT_DIR = '/jd'
    scripts_crontab_config = os.path.join(ROOT_DIR, 'config/crontab.list')
    new_scripts_dir = os.path.join(ROOT_DIR, 'own/hapecoder_JD-SCRIPT')
    scripts_jd_imwcc_dir = os.path.join(ROOT_DIR, 'own/imwcc_jd_imwcc')


elif HOST_NAME == 'ubuntu157362':
    ROOT_DIR = '/home/arvin/code'
    new_scripts_dir = os.path.join(ROOT_DIR, 'JD-SCRIPT')
    parse_from_file = os.path.join(ROOT_DIR, 'JD_tencent_scf/jd_task.json')
    scripts_crontab_config = os.path.join(FILE_DIR, 'test_files/crontab.list')
    scripts_jd_imwcc_dir = os.path.join(ROOT_DIR, 'jd_imwcc')

else:
    logging.error("找不到配置文件")
    exit(-1)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    jd_scripts_crontab_list = []

    # 解析大佬的 docker 默认 crontab 配置文件:
    with open(scripts_crontab_config, 'r') as f:
        for line in f.readlines():
            line = line.strip().replace('\n', '')
            if line.strip() == '':
                continue
            elif line.startswith('#'):
                continue
            elif '.js' not in line and 'jtask' not in line:
                continue
            jd_scripts_crontab_list.append(line)

    # 最终扫描出来缺少的脚本 crontab + 注释
    result_crontab_list = []

    yaml_dir = os.path.join(new_scripts_dir, '.github/workflows')
    yaml_files = os.listdir(yaml_dir)

    for yaml_file in yaml_files:
        if yaml_file in exclude_yaml_file_list:
            continue
        with open(os.path.join(yaml_dir, yaml_file), 'r', encoding="utf-8") as fp:
            result = fp.read()
            yaml_result = yaml.load(result, Loader=yaml.SafeLoader)
            try:
                schedule_name = yaml_result.get('name')
                if yaml_result.get(True).get('schedule') is None:
                    logging.warning("{} 没有schedule".format(yaml_file))
                    continue
                schedule_time = yaml_result.get(True).get('schedule')[0].get('cron')
                for step in yaml_result.get('jobs').get('build').get('steps'):
                    step = step.get('run')
                    if 'node' in str(step) and '.js' in step:
                        jsname = str(step).split('node')[1].strip().split('/')[-1]

                if '.js' not in jsname:
                    raise ValueError('{} 没有找到js文件名称'.format(yaml_result.get('jobs').get('build').get('steps')))

                file_name = jsname

                if file_name != '':
                    if file_name in exclude_file_list:
                        logging.info("{} 在排除列表中".format(file_name))
                        continue

                    is_in_jd_scripts = False
                    # 判斷是否在 已經jd_scripts 配置中， 若是 退出
                    for jd_scripts_line_item in jd_scripts_crontab_list:
                        if str(file_name).split('.js')[0] in str(jd_scripts_line_item):
                            is_in_jd_scripts = True
                            logging.info("{} 已经存在于 {}".format(file_name, jd_scripts_line_item))
                            break

                    if is_in_jd_scripts:
                        continue

                    elif file_name in os.listdir(scripts_jd_imwcc_dir):
                        logging.info("{} 已经存在 jd_imwcc: ".format(file_name))
                        continue

                    else:
                        # print(item)
                        comment = "# {}".format(schedule_name)
                        result_crontab_list.append(comment)
                        crontab_item = "{} otask {}".format(schedule_time,
                                                            os.path.join(new_scripts_dir, file_name))
                        result_crontab_list.append(crontab_item)
            except Exception as e:
                logging.error(yaml_file)
                logging.error(str(e))

    logging.info("============================= 分割线 =====================================")
    if len(result_crontab_list) > 0:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(scripts_crontab_config, 'a+') as f:
            f.write("# =========== JD-SCRIPT start {}  ==============\n".format(current_time))
            for line in result_crontab_list:
                logging.info(line)
                f.write(line + '\n')
            f.write("# =========== JD-SCRIPT end {} ==============\n\n".format(current_time))
