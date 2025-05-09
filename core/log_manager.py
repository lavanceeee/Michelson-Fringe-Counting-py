class LogManager:
    #单例模式
    _instance = None

    #重写__new__方法，确保只有一个实例
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance.console_view = None
        return cls._instance
    
    #设置控制台视图
    def set_console_view(self, console_view):
        self.console_view = console_view

    def log(self, message, level="info"):
        """记录日志消息"""
        if self.console_view:
            self.console_view.add_log(message, level)

    def info(self, message):
        self.log(message, "INFO")
    
    def warning(self, message):
        self.log(message, "WARNING")

    def error(self, message):
        self.log(message, "ERROR")

    def debug(self, message):
        self.log(message, "DEBUG")

#创建日志管理器实例
log_manager = LogManager()

#创建全局化函数接口
def log_info(message):
    log_manager.info(message)

def log_warning(message):
    log_manager.warning(message)

def log_error(message):
    log_manager.error(message)

def log_debug(message):
    log_manager.debug(message)


    

