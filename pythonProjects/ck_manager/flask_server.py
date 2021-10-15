import logging
import os
import time

import yaml
from flask import Flask, request
from flask_restful import Api, Resource
from UserInfo import UserInfo

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
api = Api(app)

datas = [{'id': 1, 'name': 'xag', 'age': 18}, {'id': 2, 'name': 'xingag', 'age': 19}]
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

# v4 直接放入config
ck_manager_config = None
ck_out_of_login_yaml = None
if os.path.isdir('/jd/config'):
    # 获取配置文件的路径
    yamlPath = os.path.join('/jd/config', 'ck_flask.yaml')
    ck_manager_config = os.path.join('/jd/config', 'ck_manager.cfg')
    ck_out_of_login_yaml = os.path.join('/jd/config', 'ck_out_of_login.yaml')
else:
    yamlPath = os.getenv('ck_flask_yaml_path')
    ck_manager_config = os.getenv('ck_manager_config')
    ck_out_of_login_yaml = os.path.join(FILE_DIR, 'ck_out_of_login.yaml')
if not os.path.isfile(ck_out_of_login_yaml):
    os.system(f'touch {ck_out_of_login_yaml}')


#
# def __is_valid_json(json_data) -> bool:
#     return True


def _is_valid_json(json_data):
    return json_data.get('cookie', None) is not None


class UserView(Resource):
    """
    通过继承 Resource 来实现调用 GET/POST 等动作方法
    """

    def get(self):
        """
        GET 请求
        :return:
        """
        return {'code': 200, 'msg': 'success', 'data': datas}

    def post(self):
        # 参数数据
        json_data = request.get_json()
        if not _is_valid_json(json_data):
            logging.error("无效的Jason格式")
            return {'code': 400, 'msg': '无效的Jason格式'}

        cookie_str = json_data.get('cookie').strip().replace(' ', '')
        logging.info("cookie_str=" + cookie_str)
        if 'wskey' in cookie_str:
            temp_list = []
            for key in cookie_str.split(';'):
                if 'pin=' in key:
                    temp_list.append(key)
                elif 'wskey=' in key:
                    temp_list.append(key)
            assert len(temp_list) >= 2
            json_data['appkey'] = ';'.join(temp_list)
            json_data['cookie'] = ''
        elif 'pt_key' in cookie_str:
            temp_list = []
            for key in cookie_str.split(';'):
                if 'pt_pin=' in key:
                    temp_list.append(key)
                elif 'wskey' in key:
                    temp_list.append(key)
            assert len(temp_list) >= 2
            json_data['cookie'] = ';'.join(temp_list)
        else:
            logging.error("cookie中关键字错误")
            return {'code': 400, 'msg': 'cookie中关键字错误'}
        logging.info("格式化后的jason: " + str(json_data))
        # 1. 导入 yaml
        user_info_l = []
        with open(yamlPath, 'r', encoding='utf-8') as f:
            yaml_load_result = yaml.load(f.read(), Loader=yaml.FullLoader)
            signServer = yaml_load_result.get('sign_server', None)

            if yaml_load_result.get('cookies') is not None:
                for ck in yaml_load_result.get('cookies'):
                    user = UserInfo(sign_server=signServer, **ck).format_ck()
                    if not user.has_config_key():
                        logging.error("无效的用户: {}".format(user.get_user_dict()))
                        continue
                    user_info_l.append(user)
            if signServer is None:
                logging.error("sign error {}".format("signserver 没有配置"))

        new_user = UserInfo(sign_server=signServer, **json_data).format_ck()
        if not new_user.has_config_key():
            logging.error("无效的用户: {}".format(new_user.get_user_dict()))
            return {'code': 400, 'msg': '没有配置cookie或者wskey!'}, 400

        if not new_user.update_ws_key_to_pt_key(delay=False):
            logging.error("wskey 更新失败: {}".format(new_user.get_user_dict()))
            return {'code': 400, 'msg': 'wskey 更新失败!'}, 400

        is_new_user = True
        for user in user_info_l:
            if user.get_pt_pin() == new_user.get_pt_pin():
                is_new_user = False
                logging.info("更新CK: old:" + str(user.get_user_dict()))
                logging.info("更新CK: new:" + str(new_user.get_user_dict()))
                user.update_ck_from_user(new_user)

        if is_new_user:
            logging.info("添加新用户: new:" + str(new_user.get_user_dict()))
            user_info_l.append(new_user)

        with open(yamlPath, 'w', encoding='utf-8') as w_f:
            # 覆盖原先的配置文件
            result_ck_list = []
            for user_info in user_info_l:
                result_ck = user_info.get_user_dict()
                result_ck_list.append(result_ck)
            yaml_load_result['cookies'] = result_ck_list
            yaml.dump(yaml_load_result, w_f, encoding='utf-8', allow_unicode=True, default_flow_style=False,
                      sort_keys=False)

        # 返回新增的最后一条数据
        logging.info("数据添加完成: " + new_user.get_pt_pin())
        return {'code': 200, 'msg': 'ok'}


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/ping_server')
def ping_server():
    time.sleep(2)
    return {'code': 200, 'msg': 'success'}


api.add_resource(UserView, '/ck')
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000, debug=False, threaded=True)
