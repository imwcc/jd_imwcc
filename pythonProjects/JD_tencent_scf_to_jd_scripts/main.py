import json
import os
import demjson
import socket
import time

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

exclude_file_list = ['jd_cash_exchange.js', 'jd_adolf_pk.js']

if HOST_NAME == 'arvin-wang':
    ROOT_DIR='/home/arvin/code'
    JD_tencent_scf_dir = os.path.join(ROOT_DIR, 'JD_tencent_scf')
    parse_from_file = os.path.join(ROOT_DIR, 'JD_tencent_scf/jd_task.json')
    scripts_crontab_config = os.path.join(FILE_DIR, 'test_files/crontab.list')
    scripts_jd_imwcc_dir = os.path.join(ROOT_DIR, 'jd_imwcc')

    result_crontab_file = os.path.join(JD_tencent_scf_dir, 'JD_tencent_crontab.sh')

elif HOST_NAME == 'jd-arvin':
    ROOT_DIR='/jd'
    JD_tencent_scf_dir = os.path.join(ROOT_DIR, 'own/zero205_JD_tencent_scf')
    parse_from_file = os.path.join(ROOT_DIR, 'own/zero205_JD_tencent_scf/jd_task.json')
    scripts_crontab_config = os.path.join(ROOT_DIR, 'config/crontab.list')
    scripts_jd_imwcc_dir = os.path.join(ROOT_DIR, 'own/imwcc_jd_imwcc')

    result_crontab_file = '/jd/config/crontab.list'

elif HOST_NAME == 'ubuntu157362':
    ROOT_DIR='/home/arvin/code'
    JD_tencent_scf_dir = os.path.join(ROOT_DIR, 'JD_tencent_scf')
    parse_from_file = os.path.join(ROOT_DIR, 'JD_tencent_scf/jd_task.json')
    scripts_crontab_config = os.path.join(FILE_DIR, 'test_files/crontab.list')
    scripts_jd_imwcc_dir = os.path.join(ROOT_DIR, 'jd_imwcc')

    result_crontab_file = '/jd/config/crontab.list'

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

    with open(parse_from_file, 'r') as f:
        s = f.read()
        result = demjson.decode(s)
        for item in result.get("list"):
            file_name = item.get('job').get('target').split('/')[-1].strip()
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
                    comment = "# {}".format(item.get('name'))
                    print(comment)
                    result_crontab_list.append(comment)
                    crontab_item = "{} otask {}".format(item.get('time'), os.path.join(JD_tencent_scf_dir, file_name))
                    print(crontab_item)
                    result_crontab_list.append(crontab_item)


    if len(result_crontab_list) > 0:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(scripts_crontab_config, 'a+') as f:
            f.write("# =========== JD_tencent_scf start {}  ==============\n".format(current_time))
            for line in result_crontab_list:
                logging.info("写入: " + line)
                f.write(line + '\n')
            f.write("# =========== JD_tencent_scf end {} ==============\n\n".format(current_time))

