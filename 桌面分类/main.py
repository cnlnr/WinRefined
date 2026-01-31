import sys
import ctypes
from functools import partial
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QFrame, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor
from desktop_dirs import get_dirs

class DesktopWidget(QWidget):
    def __init__(self, entries):
        super().__init__()
        # 窗口样式
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)  # 不显示任务栏 / Alt+Tab
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # 背景
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(main_layout)

        self.background = QWidget()
        self.background.setStyleSheet("background-color: rgba(50,50,50,220); border-radius: 15px;")
        main_layout.addWidget(self.background)

        layout = QHBoxLayout()
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(5)
        self.background.setLayout(layout)

        # 左侧拖动条
        self.drag_frame = QFrame()
        self.drag_frame.setFixedWidth(25)
        self.drag_frame.setStyleSheet("background-color: rgba(80,80,80,200); border-radius:10px;")
        self.drag_frame.setCursor(QCursor(Qt.SizeAllCursor))
        layout.addWidget(self.drag_frame)

        # 按钮
        button_height = 35
        self.resize(450, button_height+10)
        self.buttons = []
        for entry in entries:
            btn = QPushButton(entry["name"])
            btn.setFixedHeight(button_height)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {background-color: rgba(80,80,80,220); color:white; border-radius:10px; border:none; font-size:14px; padding-left:10px; padding-right:10px;}
                QPushButton:hover {background-color: rgba(100,100,100,220);}
                QPushButton:checked {background-color: rgba(0,200,100,220);}
            """)
            layout.addWidget(btn)
            self.buttons.append(btn)
            btn.clicked.connect(partial(self.on_button_click, entry["path"], btn))

        self.move(300,10)
        self._drag_active = False
        self._drag_position = QPoint()

        # 设置桌面上层
        self._set_desktop_top_layer()

    def on_button_click(self, path, button):
        for b in self.buttons:
            if b != button:
                b.setChecked(False)
        button.setChecked(True)
        print(path)

    def _set_desktop_top_layer(self):
        """独立顶层窗口，保证稳定显示"""
        user32 = ctypes.windll.user32
        hwnd = int(self.winId())

        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        HWND_TOPMOST = -1

        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

    # 拖动逻辑 + 屏幕边界限制
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().x() <= self.drag_frame.width():
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self._drag_active:
            new_pos = event.globalPosition().toPoint() - self._drag_position
            screen = QApplication.primaryScreen()
            if screen:
                geom = screen.availableGeometry()
                x = max(geom.left(), min(new_pos.x(), geom.right()-self.width()))
                y = max(geom.top(), min(new_pos.y(), geom.bottom()-self.height()))
                new_pos = QPoint(x,y)
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dir_list = get_dirs()
    widget = DesktopWidget(dir_list)
    widget.show()
    sys.exit(app.exec())
