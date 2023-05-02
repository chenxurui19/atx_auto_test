# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 17:03
# @Author  : CXRui
# @File    : base_method.py
# @Description : 封装facebook-wda以及uiautomator2的方法
import logging
import os
import time
from common.mobileby import MobileBy
from config.config import GlobalVar
import aircv as ac
from datetime import datetime
from PIL import Image


class BaseMethod:
    def __init__(self, driver, platform):
        self.driver = driver
        self.platform = platform
        self.src = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    def start_app(self, bundle_id, wait=True):
        if self.platform == GlobalVar.IOS:
            self.driver.app_start(bundle_id, wait_for_quiescence=wait)
        else:
            self.driver.app_start(bundle_id, wait=wait)

    def stop_app(self, bundle_id):
        self.driver.app_stop(bundle_id)

    def restart_app(self, bundle_id, duration=3):
        """
        重启APP
        :param bundle_id: 包名
        :param duration: 重启时间，默认为3s
        :return:
        """
        self.stop_app(bundle_id)
        time.sleep(duration)
        self.start_app(bundle_id)

    def start_setting(self):
        """
        打开设置
        :return:
        """
        if self.platform == GlobalVar.IOS:
            self.start_app("com.apple.Preferences")
        else:
            self.start_app("com.android.settings")

    def stop_setting(self):
        """
        关闭设置
        :return:
        """
        if self.platform == GlobalVar.IOS:
            self.stop_app("com.apple.Preferences")
        else:
            self.click_home()
            self.stop_app("com.android.settings")

    def click_home(self):
        """
        home button
        :return:
        """
        if self.platform == GlobalVar.IOS:
            self.driver.home()
        else:
            self.driver.press("home")

    def tap_middle(self):
        """
        点击屏幕中央
        :return:
        """
        self.driver.click(0.5, 0.5)

    def find_element_by_xpath(self, element_xpath, index=0):
        """
        根据xpath查找控件
        :param element_xpath: xpath字符串
        :param index: 索引
        :return: 控件对象
        """
        if self.platform == GlobalVar.IOS:
            return self.driver.xpath(element_xpath)[index]
        else:
            try:
                return self.driver.xpath(element_xpath).all()[index]
            except IndexError as e:
                raise Exception("Element Not Found")

    def find_element_by_id(self, element_id, index=0):
        """
        :param index: 索引
        :param element_id: resourceId for Android
        :return: 控件对象
        """
        return self.driver(resourceId=element_id)[index]

    def find_element_by_name(self, element_name, index=0):
        """
        :param element_name: name for iOS
        :param index:
        :return:
        """
        return self.driver(name=element_name)[index]

    def find_element_by_text(self, class_name, text, index):
        """
        :param class_name: 控件的类型
        :param text: 控件的文本
        :param index: 索引
        :return:
        """
        return self.driver(className=class_name, text=text)[index]

    def find_element_by_text_contains(self, class_name, text, index):
        return self.driver(className=class_name, text=text)[index]

    def find_element_by_text_contains(self, class_name, text_contains, index):
        """
        :param class_name: 控件的类型
        :param text_contains: 匹配文本
        :param index: 索引
        :return:
        """
        return self.driver(className=class_name, textContains=text_contains)[index]

    def find_element(self, locator, index=0):
        """
        :param locator: 元组：(定位方法, 定位文本)，比如('xpath', '//*[@text="视频"]')
        :param index: 索引
        :return:
        """
        method = locator[0]
        values = locator[1]
        if method == MobileBy.ID:
            el = self.find_element_by_id(values, index)
            if el:
                return el
            else:
                raise Exception("Element Not Found")
        elif method == MobileBy.NAME:
            el = self.find_element_by_name(values, index)
            if el:
                return el
            else:
                raise Exception("Element Not Found")
        elif method == MobileBy.XPATH:
            el = self.find_element_by_xpath(values, index)
            if el:
                return el
            else:
                raise Exception("Element Not Found")
        elif method == MobileBy.TEXT:
            el = self.find_element_by_text(values[0], values[1], index)
            if el:
                return el
            else:
                raise Exception("Element Not Found")
        elif method == MobileBy.TEXT_CONTAINS:
            el = self.find_element_by_text_contains(values[0], values[1], index)
            if el:
                return el
            else:
                raise Exception("Element Not Found")
        else:
            raise Exception("Method Not Support")

    def click_element(self, locator, index=0):
        """
        :param locator: (定位方法, 定位文本)，比如('xpath', '//*[@text="视频"]')
        :param index: 索引
        :return:
        """
        self.find_element(locator, index).click()

    def long_click_element(self, locator, duration=3, index=0):
        """
        长按控件
        :param locator: (定位方法, 定位文本)，比如('xpath', '//*[@text="视频"]')
        :param index: 索引
        :return:
        """
        if self.platform == GlobalVar.IOS:
            self.find_element(locator, index).tap_hold(duration)
        else:
            self.find_element(locator, index).long_click(duration)

    def is_exist(self, locator, index=0):
        """
        判断控件是否存在
        :param locator: (定位方法, 定位文本)，比如('xpath', '//*[@text="视频"]')
        :param index: 索引
        :return: 是否存在该控件（bool）
        """
        try:
            el = self.find_element(locator, index)
        except Exception as e:
            return False
        return el

    def get_text(self, locator, index=0):
        """
        获取控件的文本
        :param locator: (定位方法, 定位文本)，比如('xpath', '//*[@text="视频"]')
        :param index: 索引
        :return: 控件的文本
        """
        if self.platform == GlobalVar.IOS:
            return self.find_element(locator, index).text
        else:
            return self.find_element(locator, index).get_text()

    def wait_exist(self, locator, timeout=10.0):
        """
        等待控件出现
        :param locator: (定位方法, 定位文本)，比如('xpath', '//*[@text="视频"]')
        :param timeout: 超时时间（s）
        :param index: 索引
        :return: 控件是否存在
        """
        method = locator[0]
        values = locator[1]
        if method == MobileBy.ID:
            return self.driver(resourceId=values).wait(timeout=timeout)
        elif method == MobileBy.NAME:
            return self.driver(name=values).wait(timeout=timeout)
        elif method == MobileBy.XPATH:
            return True if self.driver.xpath(values).wait(timeout=timeout) else False
        elif method == MobileBy.TEXT:
            return self.driver(className=values[0], text=values[1]).wait(timeout=timeout)
        elif method == MobileBy.TEXT_CONTAINS:
            return self.driver(className=values[0], textContains=values[1]).wait(timeout=timeout)
        else:
            raise Exception("Method Not Support")

    def wait_no_exist(self, locator, timeout=3.0):
        """
        等待控件消失
        :param locator: (定位方法, 定位文本)，比如('xpath', '//*[@text="视频"]')
        :param timeout: 超时时间（s）
        :param index: 索引
        :return: 控件是否不存在
        """
        method = locator[0]
        values = locator[1]
        if method == MobileBy.ID:
            return self.driver(resourceId=values).wait_gone(timeout=timeout)
        elif method == MobileBy.NAME:
            return self.driver(name=values).wait_gone(timeout=timeout)
        elif method == MobileBy.XPATH:
            return True if self.driver.xpath(values).wait_gone(timeout=timeout) else False
        elif method == MobileBy.TEXT:
            return self.driver(className=values[0], text=values[1]).wait_gone(timeout=timeout)
        elif method == MobileBy.TEXT_CONTAINS:
            return self.driver(className=values[0], textContains=values[1]).wait_gone(timeout=timeout)
        else:
            raise Exception("Method Not Support")

    def swipe_by_screen(self, direction):
        """
        整个屏幕滑动
        :param direction: 方向，['left', 'right', 'up', 'down'] 其中的一个
        :return:
        """
        if direction not in ['left', 'right', 'up', 'down']:
            raise Exception("Direction Not Support")
        if self.platform == 'iOS':
            if direction == "left":
                self.driver.swipe_left()
            if direction == "right":
                self.driver.swipe_right()
            if direction == "up":
                self.driver.swipe_up()
            if direction == "down":
                self.driver.swipe_down()
        else:
            self.driver.swipe_ext(direction)

    def set_text(self, locator, text, index=0):
        """
        文本输入框输入文本
        :param locator:
        :param text:
        :param index:
        :return:
        """
        self.find_element(locator, index).set_text(text)

    def clear_text(self, locator, index=0):
        """
        清楚输入框文本
        :param locator: (定位方法, 定位文本)，比如('xpath', '//*[@text="视频"]'
        :param index: 索引
        :return:
        """
        self.find_element(locator, index).clear_text()

    def clear_app_data(self, bundle_id=GlobalVar.get_bundle_id()):
        """
        清除应用数据
        :return:
        """
        if self.platform == GlobalVar.IOS:
            pass
        else:
            self.driver.app_clear(bundle_id)

    def element_screenshot(self, locator: tuple = None, index: int = 0) -> str:
        """
        对控件进行截图，返回截图文件路径
        :param locator:
        :param index:
        :return:
        """
        aircv_image_path = os.path.join(self.src, "aircv_image")
        pic_time = datetime.now().strftime("%Y%m%d%H%M%S")
        screen_image_name = os.path.join(aircv_image_path, "screen_img_" + pic_time + ".png")
        if not os.path.exists(aircv_image_path):
            os.makedirs(aircv_image_path)
        if locator:  # 如果指定了控件，则对控件截图
            self.find_element(locator, index).screenshot().save(screen_image_name)
        else:  # 否则，对测试机全屏截图
            self.driver.screenshot().save(screen_image_name)
        return screen_image_name

    def click_image(self, image_name: str = None, threshold: float = 0.9):
        """
        图像匹配点击: 代码对控件进行截图，然后再进行匹配点击，可以正常识别。手动截图再进行扣取图片作为待识别图片，无法识别，不知道为啥
        :param image_name: 待识别的图片名称
        :param threshold: 图片匹配的阈值，在0到1之间。因为图像匹配并不需要每个像素精确一致，可以模糊匹配，所以这个值设定得越高，找到的区域就越接近模板图，但设得太高就有可能找不到
        :return:
        """
        try:
            screen_image_name = self.element_screenshot()
        except Exception as e:
            return e("截图失败")
        imgsrc = ac.imread(screen_image_name)  # 打开查找截图
        imgobj = ac.imread(image_name)  # 打开待识别的图片
        match_result = ac.find_template(imgsrc, imgobj, threshold)
        logging.info(f"match_result:{match_result}")
        screen_image_width, screen_image_height = Image.open(screen_image_name).size
        if match_result:
            x1, y1 = match_result["result"]
            self.driver.click(x1 / screen_image_width, y1 / screen_image_height)
        else:
            return Exception("Image recognition failure")


if __name__ == '__main__':
    # iOS，main方法启动需要手动起wda
    # import wda
    #
    # c = wda.Client("http://localhost:8100")
    # bm = BaseMethod(c, "iOS")
    # # bm.stop_setting()   # 杀死设置
    # bm.start_setting()    # 启动设置
    # bm.click_home()       # 点击home键
    # bm.tap_middle()   # 点击屏幕中间
    # bm.click_element((MobileBy.NAME, "Wi-Fi"))    # 根据Name属性查找控件，并点击
    # bm.click_element((MobileBy.XPATH, '//XCUIElementTypeCell[@name="Wi-Fi"]'))    # 根据Name属性查找控件，并点击
    # bm.click_element((MobileBy.TEXT, ("XCUIElementTypeCell", "Wi-Fi")))   # 根据Text属性查找控件，并点击
    # bm.click_element((MobileBy.TEXT_CONTAINS, ("XCUIElementTypeCell", "Wi-F")))   # 根据ClassName和Text属性混合查找查找控件，并点击
    # 根据ClassName和包含特定文本属性混合查找查找控件，并长按
    # bm.long_click_element((MobileBy.TEXT_CONTAINS, ("XCUIElementTypeCell", "Wi-F")))
    # 根据ClassName和包含特定文本属性混合查找查找控件，并判断是否存在，返回bool值
    # print(bm.is_exist((MobileBy.TEXT_CONTAINS, ("XCUIElementTypeCell", "Wi-F"))))
    # 等待控件存在，默认等待3s，返回bool值
    # print(bm.wait_exist((MobileBy.NAME, "网络")))
    # 等待控件消失，默认等待3s，返回bool值
    # print(bm.wait_no_exist((MobileBy.NAME, "网络")))
    # bm.swipe_by_screen('left')
    # bm.set_text((MobileBy.NAME, "短信"), "hhh")
    # 根据图片查找控件并点击
    # bm.click_image(os.path.join(bm.src, "aircv_image", "WechatIMG97.jpeg"))

    # Android
    import uiautomator2 as u2
    #
    c = u2.connect()
    # c.xpath('//android.widget.TextView[@text="WLAN"]').all()[0].click()
    # bm = BaseMethod(c, "Android")
    # os.system("pip list")
    # bm.clear_app_data()
    # bm.stop_setting()
    # bm.start_setting()
    # bm.click_home()
    # bm.tap_middle()
    # bm.click_element((MobileBy.ID, "com.android.settings:id/combine_relativelayout"))
    # time.sleep(3)
    # bm.click_element((MobileBy.XPATH, '//android.widget.TextView[@text="WLAN"]'))
    # bm.click_element((MobileBy.TEXT, ("android.widget.TextView", "WLAN")))
    # bm.click_element((MobileBy.TEXT_CONTAINS, ("android.widget.TextView", "WLA")))
    # bm.long_click_element((MobileBy.TEXT_CONTAINS, ("android.widget.TextView", "WLA")))
    # print(bm.is_exist((MobileBy.TEXT_CONTAINS, ("android.widget.TextView", "WLA"))))
    # print(bm.wait_exist((MobileBy.XPATH, '//android.widget.TextView[@text="选取网络"]')))
    # print(bm.wait_exist((MobileBy.TEXT, ("android.widget.TextView", "选取网络")), 10))
    # time.sleep(3)
    # print(bm.wait_no_exist((MobileBy.XPATH, '//android.widget.TextView[@text="选取网络"]')))
    # bm.swipe_by_screen('left')
    # bm.set_text((MobileBy.TEXT_CONTAINS, ("android.widget.EditText", "输入内容")), "hhhh")
    # bm.element_screenshot(locator)
    # bm.click_image(os.path.join(bm.src, "aircv_image", "screen_img_20230430202054.png"))
