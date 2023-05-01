from page.base_method import BaseMethod
from config.config import GlobalVar

global LOCATOR


class SettingMethod(BaseMethod):
    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        if self.platform == GlobalVar.IOS:
            from page.system.ios.setting_page import SettingPage
        else:
            from page.system.android.setting_page import SettingPage
        global LOCATOR
        LOCATOR = SettingPage()

    def click_wifi_text(self):
        """
        点击Wi-Fi/WLAN按钮进入Wi-Fi界面
        :return:
        """
        self.click_element(LOCATOR.wifi_text)

    def check_network_text_status(self):
        """
        判断“网络”/“选取网络”文字是否存在，依此判断是否进入到Wi-Fi界面
        :return:
        """
        return self.wait_exist(LOCATOR.network_text, 10)
