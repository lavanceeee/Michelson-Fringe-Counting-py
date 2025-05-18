from PyQt6.QtWidgets import (QMenuBar, QMenu, QToolBar,
                             QFileDialog)
from PyQt6.QtGui import QAction  
from PyQt6.QtWidgets import QDialog
from core.alert_manager import alert_error
from gui.dialogs.camera_config_dialog import CameraConfigDialog
from core.log_manager import log_info, log_error, log_debug
from gui.dialogs.data_view_dialog import DataViewDialog
from core.log_manager import log_info
from core.service.video_counter import VideoCounter
from thread.figure_n_thread import FigureNThread
from gui.elements.loading_ele import LoadingDialog

class MenuBarManger:
    def __init__(self, main_window):
        # 保存主窗口引用，用于后续操作
        self.main_window = main_window

        #初始化视频计数器
        self.video_counter = VideoCounter(self.main_window)
        # 获取主窗口的菜单栏对象
        self.menubar = main_window.menuBar()
        # 调用设置菜单的方法
        self.setup_menus()

        #初始化加载动画
        self.loading_dialog = LoadingDialog(self.main_window)

    def setup_menus(self):
        """
             设置所有菜单项
             这个方法作为菜单设置的入口点，组织所有菜单的创建过程
        """

        #文件菜单
        self.file_menu = self.create_file_menu()

        #创建配置菜单
        self.config_menu = self.create_config_menu()

        #数据项菜单
        self.data_menu = self.create_data_menu()

        #创建帮助菜单
        self.help_menu = self.create_help_menu()

        #将配置菜单和帮助菜单添加到主窗口的菜单栏中
        self.menubar.addMenu(self.file_menu)
        self.menubar.addMenu(self.config_menu)
        self.menubar.addMenu(self.data_menu)
        self.menubar.addMenu(self.help_menu)

    def create_file_menu(self):
        """
        创建文件菜单及其子项
        :return: 文件菜单对象
        """
        file_menu = QMenu('文件', self.menubar)

        #子菜单项
        video_select_action = QAction('视频选择', self.main_window)
        video_select_action.triggered.connect(self.video_counter.show_video_select)

        #将动作添加到菜单中
        file_menu.addAction(video_select_action)

        return file_menu
        
    def create_config_menu(self):
        """
              创建配置菜单及其子项
              :return: 配置菜单对象
        """
        # 创建配置菜单，'配置'是显示在菜单栏上的文本
        camera_config = QMenu('摄像头配置',self.menubar)

        ip_connect_action = QAction('连接到DroidCam', self.main_window)
        self_connect_action = QAction('连接到USB摄像头',self.main_window)


        ip_connect_action.triggered.connect(self.show_camera_config)

        # 将动作添加到配置菜单中
        camera_config.addAction(ip_connect_action)
        camera_config.addAction(self_connect_action)

        return camera_config

    def show_camera_config(self):
        #摄像头配置

        dialog = CameraConfigDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted.value:
            # 获取配置的IP和端口
            ip, port = dialog.get_camera_config()

            self.main_window.camera_controller.connect_camera(ip, port)

    def create_data_menu(self):
        data_menu = QMenu('数据处理', self.menubar)

        #选项
        data_view_action =  QAction('数据查看', self.main_window)
        data_export_action = QAction('数据导出', self.main_window)

        # 将动作添加到菜单中
        data_menu.addAction(data_view_action)
        data_menu.addAction(data_export_action)

        #连接数据查看
        data_view_action.triggered.connect(self.show_data_view)

        return data_menu
    
    def show_data_view(self):
        # 获取数据源
        main_window_counts_detector = self.main_window.counts_detector
        
        # 获取原始数据
        center_brightness_save = main_window_counts_detector.center_pos_array

        #如果数据为0那么直接结束
        if len(center_brightness_save) == 0:
            log_error("您还未开启检测")
            alert_error("您还未开启检测")
            return

        #创建计算线程
        self.figure_n_thread = FigureNThread(center_brightness_save)
        self.figure_n_thread.finished_data_signal.connect(self.handle_finished_data)
        self.figure_n_thread.is_running.connect(self.show_animation)
        self.figure_n_thread.start()

    def show_animation(self, is_running):
        if is_running:
            self.loading_dialog.show()
        else:
            self.loading_dialog.hide()
            
    def handle_finished_data(self, n, threshold, smoothed_data):
        # 创建新的对话框实例并传入所有数据
        data_view_dialog = DataViewDialog(
            parent=self.main_window,  
            smoothed_data=smoothed_data,
            n=n,
            threshold=threshold
        )
        data_view_dialog.show()
        
    def create_help_menu(self):
        """
        创建帮助菜单及其子项
        :return: 帮助菜单对象
        """
        # 创建帮助菜单
        help_menu = QMenu('帮助说明', self.menubar)

        project_website_action = QAction('项目官网',self.main_window)
        help_view_action = QAction('使用文档', self.main_window)
        project_address_action = QAction('项目地址', self.main_window)

        help_menu.addAction(project_website_action)
        help_menu.addAction(help_view_action)
        help_menu.addAction(project_address_action)

        return help_menu