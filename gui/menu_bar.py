from PyQt6.QtWidgets import (QMenuBar, QMenu, QToolBar,
                             QFileDialog)
from PyQt6.QtGui import QAction  # 从QtGui导入QAction
from PyQt6.QtWidgets import QDialog
from gui.dialogs.camera_config_dialog import CameraConfigDialog
from core.log_manager import log_info, log_error

class MenuBarManger:
    def __init__(self, main_window):
        # 保存主窗口引用，用于后续操作
        self.main_window = main_window
        # 获取主窗口的菜单栏对象
        self.menubar = main_window.menuBar()
        # 调用设置菜单的方法
        self.setup_menus()

    def setup_menus(self):
        """
             设置所有菜单项
             这个方法作为菜单设置的入口点，组织所有菜单的创建过程
        """

        #设置菜单栏的样式
        self.menubar.setStyleSheet("""
            QMenuBar{
                background-color: white;
                color:black;
                border-bottom: 1px solid #808080;
                }
            QMenuBar::item{
                background-color: white;
                padding: 5px 10px;
                color:black;
                }
            QMenuBar::item:selected {
                background-color: #8a9a9a;
                transition: background-color 0.3s ease-out;
                }
            QMenuBar::item:hover {
                background-color: #8a9a9a;
                transition: background-color 0.3s ease-in;
                }
            QMenuBar::item:disabled {
                background-color: #8a9a9a;
                transition: background-color 0.3s ease-in;
                }
        """)


        #创建配置菜单
        self.config_menu = self.create_config_menu()
        #创建帮助菜单
        self.help_menu = self.create_help_menu()

        #将配置菜单和帮助菜单添加到主窗口的菜单栏中
        self.menubar.addMenu(self.config_menu)
        self.menubar.addMenu(self.help_menu)

    def create_config_menu(self):
        """
              创建配置菜单及其子项
              :return: 配置菜单对象
        """
        # 创建配置菜单，'配置'是显示在菜单栏上的文本
        config_menu = QMenu('配置',self.menubar)

        # 创建设置动作（菜单项）
        settings_action = QAction('配置摄像头IP', self.main_window)
        # 将动作的触发信号连接到主窗口的show_settings方法
        settings_action.triggered.connect(self.show_camera_config)
        # 将动作添加到配置菜单中
        config_menu.addAction(settings_action)

        return config_menu

    def show_camera_config(self):
        """
        显示摄像头配置对话框
        """
        dialog = CameraConfigDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted.value:
            # 获取配置的IP和端口
            ip, port = dialog.get_camera_config()

            # 尝试连接摄像头
            if self.main_window.camera_controller.connect_camera(ip, port):
                log_info("connect camera success")
            else:
                log_error("connect camera failed")

    def create_help_menu(self):
        """
        创建帮助菜单及其子项
        :return: 帮助菜单对象
        """
        # 创建帮助菜单
        help_menu = QMenu('帮助', self.menubar)

        # 创建关于动作（菜单项）
        about_action = QAction('关于', self.main_window)
        # 将动作的触发信号连接到主窗口的show_about方法
        about_action.triggered.connect(self.main_window.show_about)
        # 将动作添加到帮助菜单中
        help_menu.addAction(about_action)

        return help_menu







