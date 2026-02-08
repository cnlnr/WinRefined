import sys
import win32gui
import win32con
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPoint

TARGET_HWND = 0x328108  # 你的目标窗口句柄
MAX_W, MAX_H = 2000, 1200  # 避免 CreateDIBSection 失败


class DraggableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_pos = QPoint()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("点击拖动我！\n这是挂在 HWND 下的 UI")
        label.setStyleSheet("font-size:16px; background:#202020; color:white; padding:8px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.resize(300, 120)

    # ---------------- 鼠标拖动 ----------------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_pos = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        if not self.dragging:
            return
        delta = e.globalPosition().toPoint() - self.drag_pos
        self.drag_pos = e.globalPosition().toPoint()

        hwnd = int(self.winId())
        if not win32gui.IsWindow(hwnd):
            return

        x, y, r, b = win32gui.GetWindowRect(hwnd)
        width, height = r - x, b - y

        # 移动窗口
        new_x = x + delta.x()
        new_y = y + delta.y()
        new_x = max(0, min(new_x, MAX_W))
        new_y = max(0, min(new_y, MAX_H))

        win32gui.SetWindowPos(
            hwnd, None, new_x, new_y, width, height,
            win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
        )

    def mouseReleaseEvent(self, e):
        self.dragging = False


def embed_widget(widget: QWidget, parent_hwnd: int):
    hwnd = int(widget.winId())

    # 设置为子窗口
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~win32con.WS_POPUP
    style |= win32con.WS_CHILD
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    win32gui.SetParent(hwnd, parent_hwnd)

    # 使用 widget 自己的大小（不要拉满）
    w, h = widget.width(), widget.height()

    win32gui.SetWindowPos(
        hwnd,
        None,
        50, 50,        # 初始位置
        w, h,          # 使用自身尺寸
        win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW
    )



if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = DraggableWidget()
    widget.show()

    embed_widget(widget, TARGET_HWND)

    sys.exit(app.exec())
