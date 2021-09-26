import logging
import os
import json
from UserInfo import UserInfo

# 支持的环境变量有 jd_wskey, jd_ck
# qinglong 转 UserInfo
class QingLongCkInfo:
    def __init__(self, qinglong_db_file):
        assert os.path.isfile(qinglong_db_file)
        self.__env_dic_all = []
        self.__env_dic_delete_ids = []
        self.__result_env_dic = []

        with open(qinglong_db_file, 'r') as file:
            for line in file.read().split('\n'):
                line = line.strip()
                if line == '':
                    continue
                item_dic = json.loads(s=line)
                if item_dic.get('$$deleted', None):
                    self.__env_dic_delete_ids.append(item_dic.get('_id'))
                self.__env_dic_all.append(item_dic)

        for env_item in self.__env_dic_all:
            is_valid = True
            for _id in self.__env_dic_delete_ids:
                if env_item.get('_id') == _id:
                    is_valid = False
            if is_valid:
                self.__result_env_dic.append(env_item)
            else:
                logging.info("remove item {}".format(env_item))
        # 根据位置排序
        # TODO 还需要根据位置查重
        def bubbleSort(arr: list):
            n = len(arr)
            for i in range(n):
                for j in range(0, n - i - 1):
                    if (arr[j]).get('position') < (arr[j + 1]).get('position'):
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
        bubbleSort(self.__result_env_dic)

    def get_qinglong_user(self) -> list:
        result_users = {}
        for item_dic in self.__result_env_dic:
            logging.info(item_dic)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    u = QingLongCkInfo('/home/arvin/work/ql/db/env.db')
    u.get_qinglong_user()