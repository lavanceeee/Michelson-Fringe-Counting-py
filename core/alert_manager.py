from PyQt6.QtWidgets import QMessageBox


def alert_warning(message, parent=None, title="警告"):
    return QMessageBox.warning(parent, title, message, 
                              QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

def alert_error(message, parent=None, title="出错"):
        QMessageBox.critical(parent, title, message)

def alert_info(message, parent=None, title="提示"):
        QMessageBox.information(parent, title, message)

def alert_success(message, parent=None, title="成功"):
        QMessageBox.information(parent, title, message)
       

    
        


