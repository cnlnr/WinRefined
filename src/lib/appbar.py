# -*- coding: utf-8 -*-
import ctypes
import ctypes.wintypes as wintypes
from enum import IntEnum
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer

# ===================== ctypes 64位兼容修复 =====================
if not hasattr(wintypes, 'LONG_PTR'):
    wintypes.LONG_PTR = ctypes.c_longlong
if not hasattr(wintypes, 'WPARAM'):
    wintypes.WPARAM = wintypes.UINT_PTR if ctypes.sizeof(ctypes.c_void_p) == 8 else wintypes.UINT
if not hasattr(wintypes, 'LPARAM'):
    wintypes.LPARAM = wintypes.LONG_PTR

# ===================== DPI 感知 =====================
def enable_dpi_awareness():
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # Per Monitor v2
    except:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            ctypes.windll.user32.SetProcessDPIAware()

enable_dpi_awareness()

# ===================== 常量定义 =====================
class ABMsg(IntEnum):
    NEW = 0
    REMOVE = 1
    QUERY_POS = 2
    SET_POS = 3

class ABEdge(IntEnum):
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3

WM_USER = 0x0400
APPBAR_CALLBACK = WM_USER + 0x01
LOGPIXELSX = 88

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000  # 唯一真实有用的扩展样式

# ===================== 结构体 =====================
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uCallbackMessage', wintypes.UINT),
        ('uEdge', wintypes.UINT),
        ('rc', wintypes.RECT),
        ('lParam', wintypes.LPARAM),
    ]

# ===================== DLL =====================
_shell32 = ctypes.WinDLL('shell32')
_user32 = ctypes.WinDLL('user32')
_gdi32 = ctypes.WinDLL('gdi32')

_shell32.SHAppBarMessage.argtypes = [wintypes.DWORD, ctypes.POINTER(APPBARDATA)]
_shell32.SHAppBarMessage.restype = wintypes.UINT

_user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, wintypes.INT]
_user32.GetWindowLongPtrW.restype = wintypes.LONG_PTR
_user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, wintypes.INT, wintypes.LONG_PTR]
_user32.SetWindowLongPtrW.restype = wintypes.LONG_PTR

_user32.GetDC.argtypes = [wintypes.HWND]
_user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
_gdi32.GetDeviceCaps.argtypes = [wintypes.HDC, wintypes.INT]

# ===================== 核心 AppBar 类 =====================
class DebugAppBar(QWidget):
    LOGICAL_WIDTH = 80
    LOGICAL_HEIGHT = 40

    def __init__(self, edge=ABEdge.LEFT):
        super().__init__()
        self.edge = edge
        self._registered = False

        if edge in (ABEdge.LEFT, ABEdge.RIGHT):
            self.setFixedWidth(self.LOGICAL_WIDTH)
        else:
            self.setFixedHeight(self.LOGICAL_HEIGHT)

        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        self.setStyleSheet("""
            background:#2b2b2b;
            color:white;
            border:2px solid red;
        """)

        self.dpi_scale = self.get_dpi_scale()
        self.winId()  # 强制创建 HWND
        self.disable_focus()

    # ========== 唯一真实有用的窗口扩展样式 ==========
    def disable_focus(self):
        hwnd = int(self.winId())
        ex_style = _user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        ex_style |= WS_EX_NOACTIVATE
        _user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, ex_style)

    # ========== DPI ==========
    def get_dpi_scale(self):
        hdc = _user32.GetDC(0)
        dpi = _gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
        _user32.ReleaseDC(0, hdc)
        return dpi / 96.0

    def logical_to_physical(self, v):
        return int(v * self.dpi_scale)

    def physical_to_logical(self, v):
        return int(v / self.dpi_scale)

    # ========== AppBar 消息 ==========
    def nativeEvent(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            if msg.message == APPBAR_CALLBACK:
                if msg.wParam == 8:
                    self.update_appbar_pos()
                return True, 0
        return super().nativeEvent(eventType, message)

    # ========== AppBar 注册 ==========
    def register_appbar(self):
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uCallbackMessage = APPBAR_CALLBACK

        result = _shell32.SHAppBarMessage(ABMsg.NEW, ctypes.byref(abd))
        if result:
            self._registered = True
            self.update_appbar_pos()

    def unregister_appbar(self):
        if not self._registered:
            return
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = int(self.winId())
        _shell32.SHAppBarMessage(ABMsg.REMOVE, ctypes.byref(abd))
        self._registered = False

    # ========== 定位 ==========
    def update_appbar_pos(self):
        if not self._registered:
            return

        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = int(self.winId())
        abd.uEdge = int(self.edge)

        screen = QApplication.primaryScreen().availableGeometry()
        _shell32.SHAppBarMessage(ABMsg.QUERY_POS, ctypes.byref(abd))

        if self.edge == ABEdge.LEFT:
            abd.rc.left = 0
            abd.rc.right = self.logical_to_physical(self.LOGICAL_WIDTH)
            abd.rc.top = screen.top()
            abd.rc.bottom = screen.bottom()

        _shell32.SHAppBarMessage(ABMsg.SET_POS, ctypes.byref(abd))

        self.setGeometry(
            abd.rc.left,
            abd.rc.top,
            self.physical_to_logical(abd.rc.right - abd.rc.left),
            abd.rc.bottom - abd.rc.top
        )

    # ========== 生命周期 ==========
    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(300, self.register_appbar)

    def closeEvent(self, e):
        self.unregister_appbar()
        super().closeEvent(e)

# ===================== main =====================
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    bar = DebugAppBar(edge=ABEdge.LEFT)
    bar.show()
    sys.exit(app.exec())
