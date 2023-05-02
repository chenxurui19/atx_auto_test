from common.mobileby import MobileBy


class SettingPage:
    # 进入Wi-Fi界面按钮
    wifi_text = (MobileBy.XPATH, '//XCUIElementTypeStaticText[@name="WIFI"]')

    # 选取网络的文字
    network_text = (MobileBy.XPATH, '//XCUIElementTypeStaticText[@name="网络"]')