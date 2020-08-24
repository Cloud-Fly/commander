#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import os
import platform
import sqlite3
import subprocess
import sys
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import *

sf_name = "commander"
dbname = './yunqi.db'  # 存储预设的数据库名字
presetTableName = 'commandConfig'  # 存储命令配置的表名


# 创建日志打印方法
def create_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Log等级总开关

    # 第二步，创建一个handler，用于写入日志文件
    rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))[:-4]

    log_path = os.path.dirname(os.path.realpath(sys.argv[0])) + os.sep + 'logs' + os.sep
    log_name = log_path + rq + '.log'
    logfile = log_name
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    if not os.path.exists(logfile):
        with open(logfile, mode='w', encoding='utf-8') as ff:
            logger.info("{%s}--file-create!" % logfile)
    fh = logging.FileHandler(logfile, mode='a', encoding="utf-8")
    fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

    # 第三步，定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    # 第四步，将logger添加到handler里面
    logger.addHandler(fh)
    return logger


logger = create_logging()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filename = sf_name
        self.version = "1.1.0"
        self.version_detail = [
            ("1.0.0", "增加菜单栏")
        ]
        self.author = "Yunqi"
        self.initGui()
        self.status = self.statusBar()

    """
    初始化UI
    """

    def initGui(self):
        # 设置窗口的标题
        self.setWindowTitle(sf_name)
        QToolTip.setFont(QFont('SansSerif', 10))
        # 设置状态栏
        self.statusBar().showMessage('Ready')
        # 定义中心控件为多 tab 页面
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        # 定义多个不同功能的 tab
        # 配置tab页
        self.config_cmd = CmdConfigTab()
        # 历史 tab
        self.history_cmd = CmdHistoryTab()
        # 将不同功能的 tab 添加到主 tabWidget
        self.tabs.addTab(self.config_cmd, '指令配置')
        self.tabs.addTab(self.history_cmd, '历史记录')

        self.init_menu()
        self.resize(850, 850 * 0.618)
        # 根据内容自适应大小
        # self.adjustSize()
        if platfm == 'Windows':
            self.setWindowIcon(QIcon('logo.ico'))
        else:
            self.setWindowIcon(QIcon('icon.icns'))
        self.show()

    # 初始化菜单按钮
    def init_menu(self):
        # 创建一个菜单栏
        menubar = self.menuBar()
        # 添加菜单
        fileMenu = menubar.addMenu('&文件')
        exitAction = QAction(QIcon('exit.png'), '&退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('退出应用')
        exitAction.triggered.connect(qApp.quit)
        # 添加事件
        fileMenu.addAction(exitAction)
        # action 关于
        aboutAction = QAction(QIcon(), '&关于', self)
        aboutAction.setStatusTip('关于应用')
        aboutAction.triggered.connect(self.showAboutDialog)
        helpMenu = menubar.addMenu('&帮助')
        helpMenu.addAction(aboutAction)

    # 创建按钮
    def create_button(self, label, name, func):
        btn = QPushButton(label, self)
        btn.clicked.connect(func)
        # 动态创建类参数
        setattr(self, name, btn)

    # 显示关于对话框
    def showAboutDialog(self):
        aboutDialog = QDialog()
        btn = QPushButton('确定', aboutDialog)
        btn.move(50, 50)
        btn.clicked.connect(aboutDialog.close)
        abouttest = QLabel("版本号：v%s\n联系人：%s" % (self.version, self.author), aboutDialog)
        abouttest.move(5, 5)
        aboutDialog.setWindowTitle("关于")
        aboutDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        # aboutDialog.setWindowIcon()
        aboutDialog.setWindowModality(Qt.ApplicationModal)
        aboutDialog.exec_()

    # 日志输出
    def log_output(self, msg):
        self.logEdit.append('[%s] ' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + msg + '\n')

    """
    控制窗口显示在屏幕中心的方法
    """

    # def center(self):
    #     # 获得窗口
    #     qr = self.frameGeometry()
    #     # 获得屏幕中心点
    #     cp = QDesktopWidget().availableGeometry().center()
    #     # 显示到屏幕中心
    #     qr.moveCenter(cp)
    #     self.move(qr.topLeft())


############# 不同功能的 Tab ################
class CmdConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        # 创建界面
        self.config_ui = QHBoxLayout()
        # 构建左边命令及按钮
        if True:
            self.cmd_config_vbox = QVBoxLayout()
            self.cmd_info_label = QLabel('命令：')
            self.cmd_info_text = QTextEdit()
            self.cmd_info_text.setAlignment(Qt.AlignLeft)
            self.cmd_info_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.cmd_config_vbox.addWidget(self.cmd_info_label)
            self.cmd_config_vbox.addWidget(self.cmd_info_text)

            self.配置命令按钮组 = QHBoxLayout()
            self.提取参数变量按钮 = QPushButton('提取参数')
            self.提取参数变量按钮.clicked.connect(self.extractParamVar)
            self.生成命令按钮 = QPushButton('生成命令')
            self.生成命令按钮.clicked.connect(self.genCmd)
            self.配置命令按钮组.addWidget(self.提取参数变量按钮)
            self.配置命令按钮组.addWidget(self.生成命令按钮)

        # 处理最后部件显示
        if True:
            self.最顶层布局vbox = QVBoxLayout()
            self.最顶层布局vbox.addLayout(self.cmd_config_vbox)
            self.最顶层布局vbox.addLayout(self.配置命令按钮组)
            self.setLayout(self.最顶层布局vbox)
            pass
        # 检查数据库是否存在
        self.createDB()

    # 检查数据库是否存在
    def createDB(self):
        cursor = conn.cursor()
        result = cursor.execute('select * from sqlite_master where name = "%s";' % (presetTableName))
        if result.fetchone() == None:
            logger.warning('表%s没有找到，开始重新创建' % (presetTableName))
            # 创建初始表
            pass
        else:
            logger.info('默认表%s已存在' % (presetTableName))
            pass
        conn.commit()
        # 不在这里关数据库了()
        return True

    # 抽取文本内容
    def extractParamVar(self):
        pass

    # 生成命令
    def genCmd(self):
        pass

    pass


class CmdHistoryTab(QWidget):
    pass


# 命令输出窗口中的多行文本框
class OutputBox(QTextEdit):
    # 定义一个 QTextEdit 类，写入 print 方法。用于输出显示。
    def __init__(self, parent=None):
        super(OutputBox, self).__init__(parent)
        self.setReadOnly(True)

    # 输出内容
    def print(self, text):
        self.append('[%s] ' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + text + '\n')


# 后台 系统托盘中提供一个图标
class SystemTray(QSystemTrayIcon):
    def __init__(self, icon, window):
        super(SystemTray, self).__init__()
        self.window = window
        self.setIcon(icon)
        self.setParent(window)
        self.activated.connect(self.trayEvent)  # 设置托盘点击事件处理函数
        self.tray_menu = QMenu(QApplication.desktop())  # 创建菜单
        # self.RestoreAction = QAction(u'还原 ', self, triggered=self.showWindow)  # 添加一级菜单动作选项(还原主窗口)
        self.QuitAction = QAction(u'退出 ', self, triggered=self.quit)  # 添加一级菜单动作选项(退出程序)
        # self.tray_menu.addAction(self.RestoreAction)  # 为菜单添加动作
        self.tray_menu.addAction(self.QuitAction)
        self.setContextMenu(self.tray_menu)  # 设置系统托盘菜单
        self.show()

    def showWindow(self):
        self.window.showNormal()
        self.window.activateWindow()
        self.window.setWindowFlags(Qt.Window)
        self.window.show()

    def quit(self):
        sys.stdout = sys.__stdout__
        self.hide()
        qApp.quit()

    def trayEvent(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            if main.isMinimized() or not main.isVisible():
                # 若是最小化，则先正常显示窗口，再变为活动窗口（暂时显示在最前面）
                self.window.showNormal()
                self.window.activateWindow()
                self.window.setWindowFlags(Qt.Window)
                self.window.show()
            else:
                # 若不是最小化，则最小化
                self.window.showMinimized()
                # self.window.setWindowFlags(Qt.SplashScreen)
                self.window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    conn = sqlite3.connect(dbname)
    platfm = platform.system()
    if platfm == 'Windows':
        #
        subprocessStartUpInfo = subprocess.STARTUPINFO()
        subprocessStartUpInfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
        subprocessStartUpInfo.wShowWindow = subprocess.SW_HIDE
    else:
        pass
    main = MainWindow()
    if platfm == 'Windows':
        tray = SystemTray(QIcon('logo.ico'), main)
    else:
        tray = SystemTray(QIcon('icon.icns'), main)
    sys.exit(app.exec_())
    conn.close()
