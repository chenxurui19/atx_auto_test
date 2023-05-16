# -*- coding: utf-8 -*-
# @Time    : 2023/5/9 17:09
# @Author  : CXRui
# @File    : perf_util.py
# @Description : 性能测试工具
import time
import tidevice
from tidevice._perf import DataType
from config.config import GlobalVar
import adb_common

global perf_thread, sys_cpu_perf, app_cpu_perf, memory_pef, gpu_pef, fps_pef, worker_process
perf_dict = dict()
perf_dict["sys_cpu"] = list()
perf_dict["app_cpu"] = list()
perf_dict["app_memory"] = list()
perf_dict["app_gpu"] = list()
perf_dict["app_fps"] = list()


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

    def start_get_perf(self):
        """
        获取手机运行应用的性能数据
        :param device_sn: 手机设备号
        :param bundle_id: 应用包名
        :param platform: 平台名：Android，
        :return:
        """
        global perf_thread, perf_dict, sys_cpu_perf, app_cpu_perf, memory_pef, gpu_pef, fps_pef
        perf_dict["sys_cpu"].clear()
        perf_dict["app_cpu"].clear()
        perf_dict["app_memory"].clear()
        perf_dict["app_gpu"].clear()
        perf_dict["app_fps"].clear()
        if self.platform == GlobalVar.IOS:  # iOS获取性能数据线程
            t = tidevice.Device(self.device_sn)
            perf_thread = tidevice.Performance(t, [DataType.CPU, DataType.MEMORY, DataType.NETWORK, DataType.FPS,
                                                   DataType.PAGE,
                                                   DataType.SCREENSHOT, DataType.GPU])

            def callback(_type: tidevice.DataType, value: dict):
                if _type.value == "cpu":
                    perf_dict["sys_cpu"].append(value["sys_value"] / value["count"])
                    perf_dict["app_cpu"].append(value["value"] / value["count"])
                elif _type.value == "memory":
                    perf_dict["app_memory"].append(value["value"])
                elif _type.value == "gpu":
                    perf_dict["app_gpu"].append(value["value"])
                elif _type.value == "fps":
                    perf_dict["app_fps"].append(value["value"])
                else:
                    pass

            perf_thread.start(self.bundle_id, callback=callback)
        else:  # Android获取性能数据线程
            adb_common.start_collect(self.device_sn, self.bundle_id)

    def stop_get_perf(self):
        """
        停止获取手机运行应用的性能数据
        :return: 性能数据
        """
        global perf_thread, perf_dict
        if self.platform == GlobalVar.IOS:
            perf_thread.stop()
            perf_dict["app_fps"] = perf_dict["app_fps"][1:]  # 第一个数值不取
            return perf_dict
        else:
            perf_data = adb_common.stop_collect()
            return perf_data


if __name__ == '__main__':
    # android
    perf_util = PerfUtil("bade2f7", "com.tencent.qqmusic")
    perf_util.start_get_perf()
    time.sleep(10)
    data = perf_util.stop_get_perf()
    print(data)

    # ios
    perf_util = PerfUtil("9926f93e701c2ef0fab94c171daedcc8e9357d67", "com.tencent.xin")
    perf_util.start_get_perf()
    time.sleep(10)
    data = perf_util.stop_get_perf()
    print(data)
