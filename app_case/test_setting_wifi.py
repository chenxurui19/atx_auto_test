import logging
import time
import pytest
from page.system.method.setting_method import SettingMethod
global setting_method


@pytest.mark.usefixtures("driver_setup")
class TestSettingWifi:
    @pytest.fixture()
    def init_setup(self):
        global setting_method
        setting_method = SettingMethod(self.driver, self.platform)
        logging.info("前置：启动设置")
        setting_method.start_setting()
        time.sleep(3)
        yield 1
        logging.info("后置：杀掉设置")
        setting_method.stop_setting()

    @pytest.mark.setting_wifi
    def test_setting_wifi(self, init_setup):
        """
        测试用例案例：打开设置->点击进入WiFi界面->断言，判断是否进入WiFi界面
        :param init_setup: 前置条件 and 后置条件
        :return:
        """
        logging.info("测试：点击Wi-Fi,进入到Wi-Fi连接界面")
        setting_method.click_wifi_text()
        time.sleep(3)
        assert setting_method.check_network_text_status(), "没有进入到Wi-Fi界面"
