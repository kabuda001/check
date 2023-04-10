#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file: oc_pt.py
@author: zhaoc
@time: 2023/2/2 7:44 下午


cron: 20 8 * * *
new Env('PT站自动签到');
"""

import sys
import os

parantPath = os.path.abspath(os.path.join(os.getcwd(), "../"))
sys.path.append(parantPath)

from utils import check
import requests
import datetime


class PT:
    def __init__(self, check_items):
        self.check_items = check_items

    @staticmethod
    def checkin(site, url, referer, cookie):
        now = datetime.datetime.now()
        time = '[' + now.strftime("%Y-%m-%d %H:%M:%S") + ']'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        try:
            headers = {
                'user-agent': user_agent,
                'referer': referer,
                'cookie': cookie
            }
            response = requests.get(url, headers=headers, timeout=10)
            now = datetime.datetime.now()
            time = '[' + now.strftime("%Y-%m-%d %H:%M:%S") + ']'
            if response.status_code == 200:
                response = response.text
                if '签到成功' in response or '恭喜您' in response:
                    return time + site + '签到成功~\n'
                elif '重复刷新' in response or '重复' in response or '簽到過' in response or '已经打卡' in response:
                    return time + site + '你已签到过了~\n'
                elif '开小差' in response and '已经打卡' not in response:
                    return time + site + '签到失败~\n'
                elif '首页' or '首頁' in response:
                    return time + site + '今日已访问~\n'
            else:
                return time + site + '网站无法访问~\n'
        except:
            return time + site + '网站无法访问~\n'

    def main(self):
        msg_all = ""
        site = str(self.check_items.get("site"))
        url = str(self.check_items.get("url"))
        referer = str(self.check_items.get("referer"))
        cookie = str(self.check_items.get("cookie"))
        msg = self.checkin(site, url, referer, cookie)
        msg_all += msg
        return msg_all


@check(run_script_name="PT站", run_script_expression="PT")
def main(*args, **kwargs):
    return PT(check_items=kwargs.get("value")).main()


if __name__ == "__main__":
    main()
