# atx_auto_test
这是一款基于ATX（即uiautomator2+facebook_wda）二次封装的移动ui自动化框架，按照规定的自动化用例编写用例风格，可以一套用例兼容Android和iOS测试设备，同时测试iOS APP时也无需手动启动WDA，测试结束会生成详细可观的Allure报告和pytest-html报告，相比与Appium会有更快的启动速度和控件查找速度。
## 效果展示
![效果展示_1.png](exampe_image%2F%E6%95%88%E6%9E%9C%E5%B1%95%E7%A4%BA_1.png)
![效果展示_2.png](exampe_image%2F%E6%95%88%E6%9E%9C%E5%B1%95%E7%A4%BA_2.png)
性能数据收集开关打开(iOS性能数据跟perfdog几乎相同，Android性能数据只实现获取gpu和温度)
![效果展示_3.png](exampe_image%2F%E6%95%88%E6%9E%9C%E5%B1%95%E7%A4%BA_3.png)
## 目录结构
```
.
├── README.md   # 项目文档
├── aircv_image # 图片识别资源存放目录
│   └── WechatIMG97.jpeg
├── app_case
│   ├── __init__.py
│   ├── conftest.py # pytest特有的测试配置文件，可以理解成一个专门放fixture(设备、工具)的地方
│   ├── pytest.ini  # pytest的主配置文件,可以改变pytest的默认行为,有很多可配置的选项
│   └── test_setting_wifi.py    # 示例案例
├── common
│   ├── __init__.py
│   └── mobileby.py
├── config
│   ├── __init__.py
│   └── config.py   # 用于保存全局变量
├── page    # 遵循page object模式（即PO模式）
│   ├── __init__.py
│   ├── base_method.py  # wda以及uiautomator2的方法
│   └── system  # 系统界面控件操作，写APP相关控件操作可以参考此目录
│       ├── __init__.py
│       ├── android # 定义页面元素，文件名和android页面一一对应
│       │   ├── __init__.py
│       │   └── setting_page.py
│       ├── ios # 定义页面元素，文件名和ios页面一一对应
│       │   ├── __init__.py
│       │   └── setting_page.py
│       └── method  # 定义页面操作，文件名和页面元素的文件一一对应
│           ├── __init__.py
│           └── setting_method.py
├── requirements.txt    # 所依赖的库，pip install -r requirements.txt(如安装过慢，可以指定国内镜像源，如豆瓣：pip install -r requirements.txt -i https://pypi.douban.com/simple/)
└── util
    ├── __init__.py
    ├── table_util.py   # 生成csv文档记录工具
    └── util.py # atx服务工具类
```
## 准备工作
### 本地环境搭建
命令行执行
```angular2html
pip install -r requirements.txt
```
如安装过慢，可以指定国内镜像源，如豆瓣
```angular2html
pip install -r requirements.txt -i https://pypi.douban.com/simple/
```
### 安装元素查看器，weditor
```angular2html
pip install weditor
```
### 启动weditor
```angular2html
python -m weditor
```
### PyCharm启动示例
按照如下配置，点击执行按钮即可<br /> 
![pycharm_start.png](exampe_image%2Fpycharm_start.png)
-m：需要执行的标签，例如案例setting_wifi，如需同时执行标签A和标签B，则可填写-m "A or B"，如需要执行同时满足标签A和B，则可填写-m "A and B"<br /> 
--count：需要执行的次数，例如--count=100，就是执行100次<br />
--device_sn：设备号，Android用adb devices，iOS用tidevice list<br />
--html：html_report生成地址，一般填写--html=../html_report/html_report.html即可<br /> 
--alluredir：allure测试结果存放地址，一般填写--allure_dir=../allure_result即可，测试完成allure报告会自动生成在allure_report<br />
--perf_flag: 性能数据采集开关，默认关闭，1为开启，0为关闭，填写--perf_flag=1即为打开
