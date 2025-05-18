from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal

#弹窗选择
class SelectDialog(QDialog):

    send_data_type_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("导出数据类型")
        self.setFixedSize(300, 150)

        self.layout = QVBoxLayout()

        self.excel_checkbox = QCheckBox("亮度数组(xlsx)")
        self.pic_checkbox = QCheckBox("亮度图(png)")
        self.video_checkbox = QCheckBox("已录制视频(mp4)")

        for cb in [self.excel_checkbox, self.pic_checkbox, self.video_checkbox]:
            cb.stateChanged.connect(self.allowed_click_ok_button)
            self.layout.addWidget(cb)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect(self.emit_selected_data_type)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
        
        self.setLayout(self.layout)

    def allowed_click_ok_button(self):
        enabled = any(cb.isChecked() for cb in [self.excel_checkbox, self.pic_checkbox, self.video_checkbox])
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enabled)

    def emit_selected_data_type(self):
        selected_types = []
        for cb in [self.excel_checkbox, self.pic_checkbox, self.video_checkbox]:
            if cb.isChecked():
                selected_types.append(cb.text())
        self.send_data_type_signal.emit(selected_types)
        self.accept()



        





        