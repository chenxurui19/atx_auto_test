# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 19:06
# @Author  : CXRui
# @File    : util.py
# @Description :
import random
import socket
import os
import psutil
import requests
import shutil


def create_port(host, start, end):
    """
    创建空闲的端口号
    :param host:
    :param start:
    :param end:
    :return:
    """
    while True:
        num = random.randint(start, end)
        s = socket.socket()
        s.settimeout(0.5)
        try:
            if s.connect_ex((host, num)) != 0:
                return num
        finally:
            s.close()


def check_wda_port_available(port=8100):
    url = "http://127.0.0.1:{}/status".format(port)
    try:
        response = requests.get(url)
    except BaseException as e:
        response = None
        print(e)
    if response:
        if response.status_code == 200:
            return True
        else:
            return False
    else:
        return False


def kill_wdaproxy(name):
    """
    :param name: device_sn or port
    :return:
    """
    pids = psutil.pids()
    print(pids)
    for pid in pids:
        try:
            p = psutil.Process(pid)
            if str(name) in p.cmdline():
                print(p.cmdline())
                print(pid)
                p.kill()
        except:
            pass


def kill_process(key_word):
    kill_logcat_cmd = f"ps -aux|grep '{key_word}'|grep -v 'grep'|awk '{{print $2}}'|xargs kill -9"
    os.system(kill_logcat_cmd)


def mkdir_empty_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        shutil.rmtree(dir_path)
        os.makedirs(dir_path)


if __name__ == '__main__':
    print(check_wda_port_available(8100))