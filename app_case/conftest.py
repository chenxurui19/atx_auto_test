# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 18:45
# @Author  : CXRui
# @File    : conftest.py
# @Description :    pytest特有的测试配置文件，可以理解成一个专门放fixture(设备、工具)的地方
import logging
import os
import sys
import pytest
from util import util
from config.config import GlobalVar
from tidevice import Device
from datetime import datetime
import subprocess
import time
import wda
import uiautomator2 as u2
from py.xml import html
from urllib.parse import quote

src = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))   # 当前的目录详细位置
driver = None
platform = ""   # 手机的平台
device_sn = ""  # 手机的设备号
server_ip = "127.0.0.1"  # WDA代理运行的ip，一般WDA都在同一台电脑执行，使用'127.0.0.1'不需要修改
datetime_format = "%Y-%m-%d_%H.%M.%S"  # 时间格式化
bundle_id = None    # 测试的包名
phone_log_progress = None  # 抓取log的进程
phone_log_path = ""  # 测试机缓存日志临时保存地址


# ----------------------------启动ATX服务--------------------------------
@pytest.fixture(scope="class")
def driver_setup(request):
    """
    启动atx（uiautomator2/facebook-wda）
    :param request:
    :return:
    """
    global driver, platform, device_sn, bundle_id, phone_log_progress
    device_sn = cmd_device_sn(request)
    GlobalVar.set_device_sn(device_sn)
    bundle_id = cmd_bundle_id(request)
    GlobalVar.set_bundle_id(bundle_id)

    log_dir = f"{src}/log/"  # log文件夹不存在就创建
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    report_dir = f"{src}/html_report/"  # html_report不存在就创建
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    wda_port = str(util.create_port(server_ip, 8100, 20000))  # 创建wda空闲端口号
    if len(device_sn) > 20:
        platform = GlobalVar.IOS
        GlobalVar.set_test_platform(GlobalVar.IOS)
        log_path = "{}{}_{}.log".format(log_dir, "wda_log", datetime.now().strftime(datetime_format))
        d = Device(device_sn)
        cmd = [sys.executable, "-m", "tidevice", "-u", d.udid, "wdaproxy", "--port", wda_port]  # 启动WDA
        with open(log_path, "w+") as logfile:
            subprocess.Popen(cmd, stdout=logfile, stderr=logfile)
        # connect wda
        for i in range(100):
            time.sleep(5)

            if util.check_wda_port_available(wda_port):
                wda_client = wda.Client("http://" + server_ip + ":" + wda_port)
                request.cls.driver = wda_client.session(alert_action=wda._proto.AlertAction.ACCEPT)
                request.cls.platform = platform
                driver = request.cls.driver
                break
    else:
        GlobalVar.set_test_platform(GlobalVar.ANDROID)
        platform = GlobalVar.ANDROID
        request.cls.driver = u2.connect(device_sn)
        request.cls.platform = platform
        driver = request.cls.driver

    # 开启测试机缓存日志保存
    save_device_log()


# ----------------------------注册命令行参数--------------------------------
def pytest_addoption(parser):
    """
    注册命令行参数
    :param parser:
    :return:
    """
    parser.addoption("--device_sn", action="store", default="", help="手机设备号")
    parser.addoption("--bundle_id", action="store", default="", help="测试包名")


# ----------------------------配置html_report报告--------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    html_report用法：
    https://pytest-html.readthedocs.io/en/latest/index.html
    https://blog.csdn.net/FloraCHY/article/details/125521949
    :param item:测试用例对象
　　 :param call:测试用例的测试步骤
　　         执行完常规钩子函数返回的report报告有个属性叫report.when
            先执行when=’setup’ 返回setup 的执行结果
            然后执行when=’call’ 返回call 的执行结果
            最后执行when=’teardown’返回teardown 的执行结果
    :return:
    钩子函数：#此钩子函数在setup(初始化的操作)，call（测试用例执行时），teardown（测试用例执行完毕后的处理）都会执行一次，
    跟@pytest.mark.hookwrapper一样
    作用：
    （1）可以获取到测试用例不同执行阶段的结果（setup，call，teardown）
    （2）可以获取钩子方法的调用结果（yield返回一个result对象）和调用结果的测试报告（返回一个report对象）
    每个测试用例执行后，制作测试报告
    """
    global driver, datetime
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    report.description = get_description(item)
    report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")
    extra = getattr(report, 'extra', [])
    if report.when == 'call' or report.when == "setup" or report.when == "teardown":
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            html_path = make_html_report_path(report.nodeid)
            name = datetime.now().strftime(datetime_format)
            screenshot_html = save_screenshot(html_path, name)
            extra.append(pytest_html.extras.html(screenshot_html))
            driver_log_html = save_failed_device_log(html_path, name)
            extra.append(pytest_html.extras.html(driver_log_html))
            report.extra = extra
    if report.when == "teardown":
        # 用例测试完成，kill保存测试机日志的进程，再次缓存下次测试用例的日志
        phone_log_progress.kill()
        save_device_log()


def pytest_html_report_title(report):
    """
    更改html_report标题
    :param report:
    :return:
    """
    report.title = "自动化测试报告"


def save_screenshot(html_path, name):
    """
    保存截图到html报告
    :param html_path: html保存路径
    :param name: 截图名称
    :return:
    """
    global driver
    html_path_name = '{}/{}.png'.format(html_path, name)
    driver.screenshot(html_path_name)
    html = '<div><img src="{}" alt="screenshot" width="180" height="320"' \
           'onclick="window.open(this.src)" align="right"/></div>'.format(html_path_name)
    return html


def pytest_configure(config):
    """
    给环境表添加开始时间、测试包、以及脚本开发者名字
    :param config:
    :return:
    """
    config._metadata["测试开始时间"] = time.strftime("%Y-%m-%d %H:%M:%S")
    config._metadata["测试包"] = bundle_id


def pytest_html_results_summary(prefix, summary, postfix):
    """
    from py.xml import html
    :param prefix:
    :param summary:
    :param postfix:
    :return:
    """
    prefix.extend([html.p("测试开发：Chen Xurui")])


def get_description(item):
    """
    获取用例函数的注释
    :param item:
    :return:
    """
    doc = str(item.function.__doc__)
    index = doc.find(":param")
    if index == -1:
        index = doc.find(":return:")
    if index != -1:
        return doc[:index]
    else:
        return doc


def make_html_report_path(nodeid):
    """
    创建保存失败截图和日志的文件目录
    :param nodeid:
    :return:
    """
    base_path = nodeid.replace("()", "").replace("::::", "::").replace("::", "/")
    html_path = "../html_report/{}".format(base_path)
    if not os.path.exists(html_path):
        os.makedirs(html_path)
    return html_path


def del_temporary_file():
    """
    测试结束，删除临时缓存日志文件
    :return:
    """
    temporary_file_log = f"{src}/log/temporary_file_log.log"
    if os.path.exists(temporary_file_log):
        if sys.platform.startswith("win"):
            os.system(f"del {temporary_file_log}")
        else:
            os.system(f"rm -rf {temporary_file_log}")


def pytest_sessionfinish(session, exitstatus):
    phone_log_progress.kill()  # 杀死保存缓存日志的进程
    del_temporary_file()  # 删除临时缓存日志
    util.kill_wdaproxy(device_sn)  # 测试结束后结束本次会话
    # driver.app_stop_all()     # 结束所有APP


def save_device_log():
    """
    用例执行前，获取测试机的缓存日志，并保存
    :return:
    """
    global platform, phone_log_progress, phone_log_path
    phone_log_path = "{}/log/temporary_file_log.log".format(src)
    if platform == GlobalVar.IOS:
        cmd = ["tidevice", "-u", device_sn, "syslog"]
    else:
        os.system("adb logcat -c")  # Android抓取日志前，先清除下缓存日志
        cmd = ["adb", "-s", device_sn, "logcat", "-v", "time"]
    with open(phone_log_path, "w+") as logfile:
        # 抓取系统日志，保存成log文件
        phone_log_progress = subprocess.Popen(cmd, universal_newlines=True,
                                              stdout=logfile, stderr=logfile, stdin=logfile, encoding="utf8")


def save_failed_device_log(html_path, name):
    """
    保存测试机缓存日志
    :param html_path:
    :param name:
    :return:save_failed_device_log
    """
    global platform, phone_log_path
    html_path_name = '{}/logcat_{}.log'.format(html_path, name)
    if sys.platform.startswith("win"):
        cmd = ["move", phone_log_path, html_path_name]
    else:
        cmd = ["mv", phone_log_path, html_path_name]
    subprocess.Popen(cmd, stderr=subprocess.PIPE)
    logcat_url = quote(html_path_name)
    html = '<div><a href="{0}">{0}</a></div>'.format(logcat_url)
    return html


# ----------------------------命令行获取参数--------------------------------
def cmd_device_sn(request):
    """
    脚本获取命令行参数的接口：手机设备号
    :param request:
    :return:
    """
    value = request.config.getoption("--device_sn")
    return value


def cmd_bundle_id(request):
    """
    脚本获取命令行参数的接口：测试包名
    :param request:
    :return:
    """
    value = request.config.getoption("--bundle_id")
    return value
