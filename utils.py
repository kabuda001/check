import json
import os
import random
import re
import sqlite3
import time
import traceback
# import tomli_w
from functools import wraps


def pip_install():
    print("正在安装依赖")
    os.system("pip3 install requests rsa tomli tomli_w beautifulsoup4")


try:
    import tomli
except ModuleNotFoundError:
    pip_install()
    import tomli

from checksendNotify import send



class config_get(object):
    def __init__(self, custom_path=None):
        """
        config_path: 自定义配置文件路径
        config_file: 实际使用的配置文件路径
        config_format: 实际使用的配置文件格式
        """
        if custom_path is None:
            self.config_path = self.get_config_path()
            self.config_file = self.get_config_file()
            self.config_format = self.get_config_format()
        else:
            self.config_file = custom_path
            self.config_format = self.get_config_format()

    def get_config_format(self):
        if self.config_file.endswith('.toml'):
            return "toml"
        else:
            return "json"

    @staticmethod
    def get_config_path():
        ql_old = "/ql/config/"
        ql_new = "/ql/data/config/"
        if os.path.isdir(ql_new):
            print('成功 当前环境为青龙面板v2.12+ 继续执行\n')
            return ql_new
        elif os.path.isdir(ql_old):
            print('成功 当前环境为青龙面板v2.12- 继续执行\n')
            return ql_old
        else:
            print('失败 请检查环境')
            exit(0)

    def get_config_file(self):
        toml_file = f"{self.config_path}check.toml"
        json_file = f"{self.config_path}check.json"
        if os.path.exists(toml_file):
            print(f"启用了toml配置文件\n路径为{toml_file}\n")
            return toml_file
        elif os.path.exists(json_file):
            print(f"启用了json配置文件\n路径为{json_file}\n")
            return json_file
        else:
            print("未找到配置文件")
            self.move_config_file()
            return toml_file

    def move_config_file(self):
        print("尝试移动配置文件到目录")
        if self.config_path == "/ql/config/":
            self.move_configuration_file_old()
        else:
            self.move_configuration_file_new()

    def get_real_key(self, expression):
        """
        从配置文件中获取，re表达式想要的KEY
        :return:
        """
        pattern = re.compile(expression, re.I)
        real_key = ''
        if self.config_format == "toml":
            for key in self.get_key_for_toml(self.config_file):
                if pattern.match(key) is not None:
                    real_key = key
        else:
            for key in self.get_key_for_json(self.config_file):
                if pattern.match(key) is not None:
                    real_key = key
        if real_key != '':
            return real_key
        else:
            print("啊哦没有找到")
            exit(1)

    def get_value(self, expression):
        real_key = self.get_real_key(expression)
        if self.config_format == "toml":
            return self.get_value_for_toml(self.config_file, real_key)
        else:
            return self.get_value_for_json(self.config_file, real_key)

    @staticmethod
    def move_configuration_file_old():
        print("移动配置文件")
        os.system("cp /ql/repo/kabuda001_check/check.sample.toml /ql/config/check.toml")

    @staticmethod
    def move_configuration_file_new():
        print("移动配置文件")
        os.system("cp /ql/data/repo/kabuda001_check/check.sample.toml /ql/data/config/check.toml")

    @staticmethod
    def get_value_for_toml(toml_path, key):
        with open(toml_path, "rb") as f:
            try:
                toml_dict = tomli.load(f)
                return toml_dict.get(key)
            except tomli.TOMLDecodeError:
                print(
                    f"错误：配置文件 {toml_path} 格式不对，请学习 https://toml.io/cn/v1.0.0\n错误信息：\n{traceback.format_exc()}"
                )
                exit(1)

    @staticmethod
    def get_value_for_json(json_path, key):
        with open(json_path, "r", encoding="utf8") as f:
            try:
                json_dict = json.load(f)
                return json_dict.get(key)
            except json.decoder.JSONDecodeError:
                print(f"错误：配置文件 {json_path} 格式不对，错误信息{traceback.format_exc()}")

    @staticmethod
    def get_key_for_toml(toml_path):
        with open(toml_path, "rb") as f:
            try:
                toml_dict = tomli.load(f)
                return toml_dict.keys()
            except tomli.TOMLDecodeError:
                print(
                    f"错误：配置文件 {toml_path} 格式不对，请学习 https://toml.io/cn/v1.0.0\n错误信息：\n{traceback.format_exc()}"
                )
                exit(1)

    @staticmethod
    def get_key_for_json(json_path):
        with open(json_path, "r", encoding="utf8") as f:
            try:
                json_dict = json.load(f)
                return json_dict.keys()
            except json.decoder.JSONDecodeError:
                print(f"错误：配置文件 {json_path} 格式不对，错误信息{traceback.format_exc()}")


class check(object):
    def __init__(self, run_script_name, run_script_expression, Configuration_flag=False):
        """
        :param run_script_name: 执行脚本的说明
        :param run_script_expression: 需要获取的配置键的re表达式
        :param Configuration_flag: 是否只检测True或False(默认为False)
        """
        self.run_script_name = run_script_name
        self.run_script_expression = run_script_expression
        self.Configuration_flag = Configuration_flag

    @staticmethod
    def other_task():
        # change_db()
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapper():
            if not self.Configuration_flag:
                config = config_get()
                value_list = config.get_value(self.run_script_expression)
                push_message = ""
                num = 1
                for value in value_list:
                    print(f"<----------------账号【{num}】---------------->")
                    print(f"获取到的账号信息为:{value}\n")
                    num += 1
                    try:
                        result = func(value=value) + '\n\n'
                        print(f"执行结果:\n{result}")
                        push_message += result
                    except IndexError:
                        print("可能是示例格式被运行\n错误信息:")
                        print(f"{traceback.format_exc()}")
                        push_message += ''
                    except AttributeError:
                        print("可能是配置文件的键名出现问题\n"
                              "例如:在此次更新中什么值得买的键名从smzdm_cookie变成了cookie\n")
                        print(f"{traceback.format_exc()}")
                        push_message += ''
                    except TypeError:
                        print(f"{traceback.format_exc()}")
                        push_message += ''
                send(self.run_script_name, push_message)
            else:
                config = config_get()
                flag = config.get_value(self.run_script_expression)
                if flag is not None and flag:
                    print(f"开始执行{self.run_script_name}")
                    func()
                else:
                    print(f"设置为不执行{self.run_script_name}")

        return wrapper



if __name__ == "__main__":
    pip_install()

