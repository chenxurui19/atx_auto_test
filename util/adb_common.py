# -*- coding: utf-8 -*-
# @Time    : 2023/5/15 15:46
# @Author  : CXRui
# @File    : adb_common.py
# @Description :
import os
import sys
import re
import logging
import subprocess
import time
import threading

perf_dict = {
    "sys_cpu": [],
    "app_cpu": [],
    "app_memory": [],
    "app_gpu": [],
    "app_fps": []
}
# 用于控制线程的标志变量
running = False


class ADB(object):

    def shell(self, cmd, device_sn):
        run_cmd = f'adb -s {device_sn} shell {cmd}'
        result = subprocess.Popen(run_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[
            0].decode("utf-8").strip()
        return result

    def shell_no_device(self, cmd):
        run_cmd = f'adb {cmd}'
        result = os.system(run_cmd)
        return result


adb = ADB()


def filterType():
    """
    返回对应系统的过滤符，windows为findstr，其他为grep
    :return:
    """
    if sys.platform.startswith("win"):
        return "findstr"
    else:
        return "grep"


def getPid(device_sn, bundle_id):
    """
    获取进程pid
    :param device_sn:
    :param bundle_id:
    :return:
    """
    result = os.popen(f"adb -s {device_sn} shell ps | {filterType()} {bundle_id}").readlines()
    processList = ['{}:{}'.format(process.split()[1], process.split()[7]) for process in result]
    if len(processList) == 0:
        logging.warning('no pid found')
    return processList


def get_temperature(device_sn):
    """
    获取Android设备的温度
    :param device_sn:
    :return:
    """
    try:
        temperature_val = int(adb.shell("dumpsys battery | grep temperature | awk '{print $2}'", device_sn)) / 10
        return temperature_val
    except Exception as e:
        logging.info("获取温度数据失败！！！")
        return None


def get_cpu_usage_rate(device_sn, bundle_id):
    """
    获取Android设备系统CPU总占用百分比和应用占用百分比
    -m num Maximum number of processes to display.   // 最多显示多少个进程
    -n num Updates to show before exiting. // 刷新次数
    -d num Seconds to wait between updates.  // 刷新间隔时间（默认5秒）
    -s col Column to sort by (cpu,vss,rss,thr).  // 按哪列排序
    -t Show threads instead of processes.   // 显示线程信息而不是进程
    -h Display this help screen.  // 显示帮助文档
    User 15%, System 12%, IOW 0%, IRQ 0% // CPU占用率
    User 468 + Nice 125 + Sys 481 + Idle 2783 + IOW 1 + IRQ 0 + SIRQ 2 = 3860 // CPU使用情况

    PID   PR   CPU% S  #THR     VSS         RSS    PCY       UID             Name // 进程属性
    284   1     16% S         61     473068K  41488K   fg       media    /system/bin/mediaserver
    :param device_sn:
    :param bundle_id:
    :return:
    """
    cpu_usage = dict()
    output_str = adb.shell("top -n 1 -d 1", device_sn)
    # 提取系统的总占用率
    system_usage = re.search(r'User (\d+)%.*, System (\d+)%.*, IOW (\d+)%.*, IRQ (\d+)%', output_str)
    # APP的CPU占用率
    app_pid = getPid(device_sn, bundle_id)[0].split(":")[0]

    cpu_usage["system_cpu_usage"] = float(system_usage.group(1)) + float(system_usage.group(2)) + float(
        system_usage.group(3)) + float(system_usage.group(4))
    cpu_usage["app_cpu_usage"] = float(re.search(r'\b{}\s+\d+\s+(\d)+%\s+'.format(app_pid), output_str).group(1))
    global perf_dict
    perf_dict["sys_cpu"].append(cpu_usage["system_cpu_usage"])
    perf_dict["app_cpu"].append(cpu_usage["app_cpu_usage"])
    return cpu_usage


def get_men_usage_rate(device_sn, bundle_id):
    """
    获取系统总占用运行内存百分比和安卓设备应用占用运行内存百分比
    :param device_sn:
    :param bundle_id:
    :return:
    """
    men_usage = dict()
    output_str = adb.shell("dumpsys meminfo", device_sn)
    # 使用正则表达式匹配运行内存总量和已使用内存量
    match_total = float(re.search(r"Total RAM:\s+(\d+)", output_str).group(1))  # 总运行内存
    match_used = float(re.search(r"Used RAM:\s+(\d+)", output_str).group(1))  # 已使用运行内存
    match_app = float(
        re.search(r"\s+(\d+)\s+kB:\s+{}\s+".format(re.escape(bundle_id)), output_str).group(1))  # APP使用运行内存

    men_usage["system_men_usage"] = match_used / match_total * 100
    men_usage["app_men_usage"] = match_app / match_total * 100
    perf_dict["app_memory"].append(men_usage["app_men_usage"])
    return men_usage


def get_fps(device_sn, bundle_id):
    """
    获取安卓设备应用的FPS、Jank
    :param device_sn:
    :param bundle_id:
    :return:
    """
    from solox.public.fps import FPSMonitor
    dict1 = dict()
    monitors = FPSMonitor(device_id=device_sn, package_name=bundle_id, frequency=1)
    monitors.start()
    dict1["fps"], dict1["jank"] = monitors.stop()
    perf_dict["app_fps"].append(dict1["fps"])
    return dict1


def get_gpu_usage(device_sn, bundle_id, duration=1):
    """
    获取安卓设备应用占用的GPU百分比
    :param device_sn:
    :param bundle_id:
    :param duration:
    :return:
    """
    time.sleep(duration)
    output_str = adb.shell(f"dumpsys gfxinfo {bundle_id}", device_sn)
    lines = output_str.strip().split("\n")
    gpu_operations = 0
    total_operations = 0

    # 查找Recent DisplayList operations部分的开始行和结束行
    start_index = -1
    end_index = -1
    for i, line in enumerate(lines):
        if "Recent DisplayList operations" in line:
            start_index = i + 1
        elif line.startswith("Caches:"):
            end_index = i
            break

    # 统计DrawBitmap操作的数量和总操作数量
    if start_index != -1 and end_index != -1:
        for line in lines[start_index:end_index]:
            if "DrawBitmap" in line:
                gpu_operations += 1
            total_operations += 1

    # 计算GPU使用率
    if total_operations > 0:
        gpu_usage = (gpu_operations / total_operations) * 100
        perf_dict["app_gpu"].append(gpu_usage)
        return gpu_usage
    else:
        # logging.error("获取GPU数据失败！！！")
        return None


def start_collect_perf(device_sn, bundle_id):
    global running, perf_dict
    perf_dict["sys_cpu"].clear()
    perf_dict["app_cpu"].clear()
    perf_dict["app_memory"].clear()
    perf_dict["app_gpu"].clear()
    perf_dict["app_fps"].clear()
    if not running:
        running = True
        # 创建并启动线程
        thread1 = threading.Thread(target=lambda: run_function(get_cpu_usage_rate, device_sn, bundle_id))
        thread2 = threading.Thread(target=lambda: run_function(get_men_usage_rate, device_sn, bundle_id))
        thread3 = threading.Thread(target=lambda: run_function(get_gpu_usage, device_sn, bundle_id))
        thread4 = threading.Thread(target=lambda: run_function(get_fps, device_sn, bundle_id))
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()


def run_function(func, *args):
    while running:
        func(*args)


def stop_collect_perf():
    global running, perf_dict
    running = False
    return perf_dict


if __name__ == '__main__':
    start_collect_perf("bade2f7", "com.tencent.qqmusic")
    time.sleep(10)
    data = stop_collect_perf()
    print(data)
