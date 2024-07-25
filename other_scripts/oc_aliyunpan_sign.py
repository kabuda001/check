#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file: oc_aliyunpan_sign.py
@author: zhaoc
@time: 2024/7/25 14:09


cron: 20 8 * * *
new Env('阿里云盘4月自动签到');
"""

import sys
import os

parantPath = os.path.abspath(os.path.join(os.getcwd(), "../"))
sys.path.append(parantPath)

from utils import check
import requests
import datetime
import traceback


class ALiYunPan:
    def __init__(self, check_items):
        self.check_items = check_items

    def get_access_token(refresh_token):
        access_token = ''
        try:
            url = "https://auth.aliyundrive.com/v2/account/token"

            data_dict = {
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/json;charset=UTF-8",
                "origin": "https://www.aliyundrive.com",
                "pragma": "no-cache",
                "referer": "https://www.aliyundrive.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            }

            resp = requests.post(url, json=data_dict, headers=headers)
            resp_json = resp.json()
            print(f"resp_json={resp_json}")

            token = {}
            token['access_token'] = resp_json.get('access_token', "")
            token['refresh_token'] = resp_json.get('refresh_token', "")
            token['expire_time'] = resp_json.get('expire_time', "")
            print(
                f"获取得到新的access_token={token['access_token'][:10]}......,新的refresh_token={token['refresh_token']},过期时间={token['expire_time']}")
            access_token = token['access_token']
        except:
            print(f"获取异常:{traceback.format_exc()}")

        return access_token

    def get_reward(self, day, access_token):
        try:
            url = 'https://member.aliyundrive.com/v1/activity/sign_in_reward'
            headers = {
                "Content-Type": "application/json",
                "Authorization": access_token,
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 D/C501C6D2-FAF6-4DA8-B65B-7B8B392901EB"
            }
            body = {
                'signInDay': day
            }

            resp = requests.post(url, json=body, headers=headers)
            resp_text = resp.text
            print(f"resp_json={resp_text}")

            resp_json = resp.json()
            result = resp_json.get('result', {})
            name = result.get('name', '')
            description = result.get('description', '')
            return {'name': name, 'description': description}
        except:
            print(f"获取签到奖励异常={traceback.format_exc()}")

        return {'name': 'null', 'description': 'null'}

    @staticmethod
    def sign_in(access_token):
        now = datetime.datetime.now()
        time = '[' + now.strftime("%Y-%m-%d %H:%M:%S") + ']'
        sign_in_days_lists = []
        not_sign_in_days_lists = []

        try:
            url = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
            headers = {
                "Content-Type": "application/json",
                "Authorization": access_token,
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 D/C501C6D2-FAF6-4DA8-B65B-7B8B392901EB"
            }
            body = {}

            resp = requests.post(url, json=body, headers=headers)
            resp_text = resp.text
            resp_json = resp.json()

            # 未登录
            # {"code":"AccessTokenInvalid","message":"not login","requestId":"0a0080e216757311048316214ed958"}
            code = resp_json.get('code', '')
            if code == "AccessTokenInvalid":
                print(f"请检查token是否正确")
            elif code is None:
                # success = resp_json.get('success', '')
                # logger.debug(f"success={success}")

                result = resp_json.get('result', {})
                sign_in_logs_list = result.get("signInLogs", [])
                sign_in_count = result.get("signInCount", 0)
                msg = ''

                if len(sign_in_logs_list) > 0:
                    for i, sign_in_logs_dict in enumerate(sign_in_logs_list, 1):

                        status = sign_in_logs_dict.get('status', '')
                        day = sign_in_logs_dict.get('day', '')
                        isReward = sign_in_logs_dict.get('isReward', 'false')
                        if status == "":
                            print(
                                f"sign_in_logs_dict={sign_in_logs_dict}")
                            print(f"签到信息获取异常:{resp_text}")
                        elif status == "miss":
                            # logger.warning(f"第{day}天未打卡")
                            not_sign_in_days_lists.append(day)
                        elif status == "normal":
                            reward = {}
                            if not isReward:  # 签到但未领取奖励
                                reward = self.get_reward(day, access_token)
                            else:
                                reward = sign_in_logs_dict.get('reward', {})
                            # 获取签到奖励内容
                            if reward:
                                name = reward.get('name', '')
                                description = reward.get('description', '')
                            else:
                                name = '无奖励'
                                description = ''
                            today_info = '✅' if day == sign_in_count else '☑'
                            log_info = f"{today_info}打卡第{day}天，获得奖励：**[{name}->{description}]**"
                            print(log_info)
                            msg = log_info + '\n\n' + msg
                            sign_in_days_lists.append(day)

                    log_info = f"🔥打卡进度:{sign_in_count}/{len(sign_in_logs_list)}"
                    print(log_info)

                    msg = log_info + '\n\n' + msg
                    return time + msg
                else:
                    print(f"resp_json={resp_json}")
                    return time + resp_json
            else:
                print(f"resp_json={resp_json}")
                # logger.debug(f"code={code}")
                return time + resp_json

        except:
            print(f"签到异常={traceback.format_exc()}")
            return time + "签到异常=" + traceback.format_exc()

    def main(self):
        msg_all = ""
        refresh_token = str(self.check_items.get("refresh_token"))
        access_token = self.get_access_token(refresh_token)
        msg = self.sign_in(access_token)
        msg_all += msg
        return msg_all


@check(run_script_name="阿里云盘", run_script_expression="aliyunpan")
def main(*args, **kwargs):
    return ALiYunPan(check_items=kwargs.get("value")).main()


if __name__ == "__main__":
    main()
