import json
import os

import demjson
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
fpath = '/home/arvin/code/JD_tencent_scf/jd_task.json'

source_jd_scripts = '/home/arvin/code/jd_scripts'
source_jd_imwcc = '/home/arvin/code/jd_imwcc'

docker_giuhtb_dir = '/jd/own/zero205_JD_tencent_scf'

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print_hi('PyCharm')
    # print(result)
    print('\n')
    jd_scripts_files_list = os.listdir(source_jd_scripts)

    with open(fpath, 'r') as f:
        s = f.read()
        result = demjson.decode(s)
        for item in result.get("list"):
            file_name = item.get('job').get('target').split('/')[-1].strip()
            if file_name != '':
                if file_name in jd_scripts_files_list:
                    continue
                elif file_name in os.listdir(source_jd_imwcc):
                    print("file 在 jd_imwcc: " + file_name)
                    continue
                else:
                    # print(item)
                    print("# {}".format(item.get('name')))
                    print("{} otask {}".format(item.get('time'), os.path.join(docker_giuhtb_dir, file_name)))
                    # print("otask {} now ;\\".format(os.path.join(docker_giuhtb_dir, file_name)))


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
