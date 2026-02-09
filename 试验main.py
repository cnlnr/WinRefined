import sys
import ctypes
import win32gui
import win32con
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPoint

# ----------------- 拖动可用 -----------------
MAX_W, MAX_H = 2000, 1200  # 最大尺寸限制

class DesktopOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_pos = QPoint()

        # 无边框
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("这是桌面浮层\n可拖动，不挡图标")
        label.setStyleSheet("font-size:16px; background:#202020; color:white; padding:8px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.resize(300, 120)

    # ----------------- 拖动 -----------------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_pos = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        if not self.dragging:
            return
        delta = e.globalPosition().toPoint() - self.drag_pos
        self.drag_pos = e.globalPosition().toPoint()

        new_x = self.x() + delta.x()
        new_y = self.y() + delta.y()
        new_x = max(0, min(new_x, MAX_W - self.width()))
        new_y = max(0, min(new_y, MAX_H - self.height()))

        self.move(new_x, new_y)

    def mouseReleaseEvent(self, e):
        self.dragging = False

# ----------------- 找到桌面 WorkerW -----------------
def get_desktop_hwnd():
    progman = win32gui.FindWindow("Progman", None)
    # 发送消息强制创建 WorkerW
    win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
    workerw = None

    def enum_windows(hwnd, lParam):
        nonlocal workerw
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "WorkerW":
            child = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
            if child != 0:
                workerw = hwnd
        return True

    win32gui.EnumWindows(enum_windows, None)
    if workerw:
        return workerw
    return progman  # 回退到 Progman

# ----------------- 挂到桌面 -----------------
def attach_to_desktop(widget: QWidget):
    hwnd = int(widget.winId())
    desktop_hwnd = get_desktop_hwnd()

    # 设置 WS_CHILD
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~win32con.WS_POPUP
    style |= win32con.WS_CHILD
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    # 父窗口
    win32gui.SetParent(hwnd, desktop_hwnd)

    # 放到左上角
    win32gui.SetWindowPos(hwnd, None, 50, 50, widget.width(), widget.height(),
                          win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = DesktopOverlay()
    widget.show()
    attach_to_desktop(widget)
    sys.exit(app.exec())
