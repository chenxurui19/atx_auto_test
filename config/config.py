# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 18:53
# @Author  : CXRui
# @File    : config.py
# @Description : 用于保存全局变量
class GlobalVar:
    IOS = "iOS"
    ANDROID = "Android"
    DEVICE_SN = ""
    TEST_PLATFORM = "iOS"
    BUNDLE_ID = ""

    @staticmethod
    def set_device_sn(device_sn):
        GlobalVar.DEVICE_SN = device_sn

    @staticmethod
    def get_device_sn():
        return GlobalVar.DEVICE_SN

    @staticmethod
    def set_test_platform(test_platform):
        GlobalVar.TEST_PLATFORM = test_platform

    @staticmethod
    def get_test_platform():
        return GlobalVar.TEST_PLATFORM

    @staticmethod
    def set_bundle_id(bundle_id):
        GlobalVar.BUNDLE_ID = bundle_id

    @staticmethod
    def get_bundle_id():
        return GlobalVar.BUNDLE_ID
