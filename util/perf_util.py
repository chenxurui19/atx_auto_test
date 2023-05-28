# -*- coding: utf-8 -*-
# @Time    : 2023/5/9 17:09
# @Author  : CXRui
# @File    : perf_util.py
# @Description : 性能测试工具
import re
import sys
import os
import logging
import time
import tidevice
import threading
import subprocess
from tidevice._perf import DataType
from config.config import GlobalVar


def filterType():
    if sys.platform.startswith("win"):
        return "findstr"
    else:
        return "grep"


class ADB(object):

    @staticmethod
    def shell(cmd, device_sn):
        run_cmd = f'adb -s {device_sn} shell {cmd}'
        result = subprocess.Popen(run_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[
            0].decode("utf-8").strip()
        return result

    @staticmethod
    def shell_no_device(cmd):
        run_cmd = f'adb {cmd}'
        result = os.system(run_cmd)
        return result


class IOSPerf:
    def __init__(self, device_sn, bundle_id):
        self.device_sn = device_sn
        self.bundle_id = bundle_id
        self.perf_dict = {
            "sys_cpu": [],
            "app_cpu": [],
            "app_memory": [],
            "sys_gpu": [],
            "app_fps": [],
            "temp": []
        }
        self.perf_thread = None
        self.t_temp = None
        self.temp_flag = True

    def get_temp(self, td):
        """
        获取温度
        :return:
        """
        while self.temp_flag:
            io_power = (td.get_io_power())
            diagnostics = io_power['Diagnostics']
            io_registry = diagnostics['IORegistry']
            temperature = io_registry['Temperature']
            temp_float = float(temperature) / 100
            self.perf_dict["temp"].append(temp_float)
            # logging.info(temp_float)
            time.sleep(1)

    def start_collect_perf(self):
        """
        获取手机运行应用的性能数据
        :param device_sn: 手机设备号
        :param bundle_id: 应用包名
        :param platform: 平台名：Android，
        :return:
        """
        self.perf_dict["sys_cpu"].clear()
        self.perf_dict["app_cpu"].clear()
        self.perf_dict["app_memory"].clear()
        self.perf_dict["sys_gpu"].clear()
        self.perf_dict["app_fps"].clear()

        t = tidevice.Device(self.device_sn)
        self.perf_thread = tidevice.Performance(t, [DataType.CPU, DataType.MEMORY, DataType.NETWORK, DataType.FPS,
                                               DataType.PAGE,
                                               DataType.SCREENSHOT, DataType.GPU])

        def callback(_type: tidevice.DataType, value: dict):
            if _type.value == "cpu":
                self.perf_dict["sys_cpu"].append(round(value["sys_value"] / value["count"], 2))
                self.perf_dict["app_cpu"].append(round(value["value"] / value["count"], 2))
            elif _type.value == "memory":
                self.perf_dict["app_memory"].append(round(value["value"], 2))
            elif _type.value == "gpu":
                self.perf_dict["sys_gpu"].append(round(value["value"], 2))
            elif _type.value == "fps":
                self.perf_dict["app_fps"].append(round(value["value"], 2))
            else:
                pass

        self.perf_thread.start(self.bundle_id, callback=callback)

        self.t_temp = threading.Thread(target=self.get_temp, args=[t])
        self.t_temp.start()

    def stop_collect_perf(self):
        self.perf_thread.stop()
        self.temp_flag = False  # 获取温度停止
        self.perf_dict["app_fps"] = self.perf_dict["app_fps"][1:]  # 第一个数值不取
        return self.perf_dict


class AndroidPerf:
    def __init__(self, device_sn, bundle_id):
        self.device_sn = device_sn
        self.bundle_id = bundle_id
        self.perf_dict = {
            "sys_cpu": [],  # 系统CPU占用率
            "app_cpu": [],  # APP的CPU占用率
            "app_memory": [],  # APP占用内存
            "sys_gpu": [],  # GPU占用率
            "app_fps": [],  # FPS
            "app_jank": [],  # JANK（卡顿次数）
            "temp": []  # 温度
        }
        self.running = True

    def get_pid(self):
        """
        获取进程pid
        :return:
        """
        result = os.popen(f"adb -s {self.device_sn} shell ps | {filterType()} {self.bundle_id}").readlines()
        processList = ['{}:{}'.format(process.split()[1], process.split()[7]) for process in result]
        if len(processList) == 0:
            logging.warning('no pid found')
        try:
            pid = int(processList[0].split(":")[0])
            return pid
        except Exception as e:
            logging.info(e)
            return None

    def get_cpu_usage(self, duration=0.5):
        """
        获取cpu占用率
        :param duration:
        :return:
        """
        pass

    def get_gpu_usage(self):
        """
        获取GPU使用率，与PerfDog误差在0.001以内
        :return:
        """
        result1 = ADB.shell("cat /sys/class/kgsl/kgsl-3d0/gpubusy", self.device_sn)
        result2 = ADB.shell('su -c "cat /sys/class/kgsl/kgsl-3d0/gpubusy"', self.device_sn)
        GUsage = 0
        if result1:
            data1 = result1.split()
            GUsage = 0 if int(data1[1]) == 0 else round(int(data1[0]) / int(data1[1]) * 100,
                                                        3)  # round(i,j)给i取j位小数，X100，转化为百分比
        elif result2:
            data2 = result2.split()
            GUsage = 0 if int(data2[1]) == 0 else round(int(data2[0]) / int(data2[1]) * 100,
                                                        3)  # round(i,j)给i取j位小数，X100，转化为百分比
        else:
            logging.info("GUsage获取失败，可能获取GPU命令不适用于被测机型")
        time.sleep(1)
        self.perf_dict["sys_gpu"].append(GUsage)
        return GUsage

    def get_temperature(self):
        """
        获取温度
        :return:
        """
        result = ADB.shell("dumpsys battery | grep temperature", self.device_sn)
        temp = re.findall(r"\d+", result)
        temp = round(float(temp[0]) / 10, 2)
        self.perf_dict["temp"].append(temp)
        time.sleep(1)
        return temp

    def get_mem(self):
        """
        获取app占用内存
        :return:
        """
        try:
            total = ADB.shell(f"dumpsys meminfo {self.bundle_id} | grep 'TOTAL'", self.device_sn)
            men_total = re.findall(r"\d+\.?\d*", total)
            if len(men_total) != 0:
                mem_dict = {
                    'Pss_Total': int(men_total[0]) // 1024,
                    'private_Dirty': int(men_total[1]) // 1024
                }
                self.perf_dict["app_memory"].append(mem_dict["Pss_Total"])
                return mem_dict
            else:
                pass
                # logging.warning("获取不到占用内存")
        except Exception as e:
            logging.warning(str(e), "get_mem(package)，请检查包名是否正确……")
            return {}

    def current_app_bundle_id(self):
        bundle_id = ADB.shell("dumpsys window | grep mCurrentFocus", self.device_sn).split(" ")[-1].split('/')[0]
        return bundle_id

    def get_fps(self):
        """
        获取被测应用的fps
        :return:
        """
        pass

    def run_function(self, func, *args):
        while self.running:
            func(*args)

    def start_collect_perf(self):
        self.perf_dict["sys_cpu"].clear()
        self.perf_dict["app_cpu"].clear()
        self.perf_dict["app_memory"].clear()
        self.perf_dict["sys_gpu"].clear()
        self.perf_dict["app_fps"].clear()
        th_cpu = threading.Thread(target=lambda: self.run_function(self.get_cpu_usage))
        th_men = threading.Thread(target=lambda: self.run_function(self.get_mem))
        th_gpu = threading.Thread(target=lambda: self.run_function(self.get_gpu_usage))
        th_fps = threading.Thread(target=lambda: self.run_function(self.get_fps))
        th_temp = threading.Thread(target=lambda: self.run_function(self.get_temperature))
        th_cpu.start()
        th_men.start()
        th_gpu.start()
        th_fps.start()
        th_temp.start()

    def stop_collect_perf(self):
        self.running = False
        return self.perf_dict


class PerfUtil:
    """
    获取设备性能Api
    """
    def __init__(self, device_sn, bundle_id, duration=0):
        self.device_sn = device_sn
        self.bundle_id = bundle_id
        if len(device_sn) > 20:
            self.platform = GlobalVar.IOS
        else:
            self.platform = GlobalVar.ANDROID
        self.duration = duration
        if self.platform == GlobalVar.IOS:
            self.perf_util = IOSPerf(self.device_sn, self.bundle_id)
        else:
            self.perf_util = AndroidPerf(self.device_sn, self.bundle_id)

    def start_get_perf(self):
        """
        开始获取手机运行应用的性能数据
        :return:
        """
        self.perf_util.start_collect_perf()

    def stop_get_perf(self):
        """
        停止获取手机运行应用的性能数据
        :return: 性能数据
        """
        perf_data = self.perf_util.stop_collect_perf()
        return perf_data


if __name__ == '__main__':
    # android
    # perf_util = PerfUtil("bade2f7", "com.tencent.qqmusic")
    # perf_util.start_get_perf()
    # time.sleep(10)
    # data = perf_util.stop_get_perf()
    # print(data)

    # ios
    perf_util = PerfUtil("9926f93e701c2ef0fab94c171daedcc8e9357d67", "com.tencent.xin")
    perf_util.start_get_perf()
    time.sleep(10)
    data = perf_util.stop_get_perf()
    print(data)
