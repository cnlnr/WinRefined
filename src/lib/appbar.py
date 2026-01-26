# -*- coding: utf-8 -*-
import ctypes
import ctypes.wintypes as wintypes
from enum import IntEnum
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer

# ===================== ctypes 64位兼容修复 =====================
# 在64位Windows上，ctypes.wintypes中没有LONG_PTR、WPARAM、LPARAM
# 需要手动定义，保证后续API调用不会报错
if not hasattr(wintypes, 'LONG_PTR'):
    wintypes.LONG_PTR = ctypes.c_longlong
if not hasattr(wintypes, 'WPARAM'):
    wintypes.WPARAM = wintypes.UINT_PTR if ctypes.sizeof(ctypes.c_void_p) == 8 else wintypes.UINT
if not hasattr(wintypes, 'LPARAM'):
    wintypes.LPARAM = wintypes.LONG_PTR

# ===================== DPI 感知 =====================
# 保证高分屏下Qt窗口缩放正确
def enable_dpi_awareness():
    try:
        # Windows 10/11 per-monitor v2 DPI感知
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except:
        try:
            # 备用方式，兼容旧版本Windows
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            # 再备用：系统感知
            ctypes.windll.user32.SetProcessDPIAware()

enable_dpi_awareness()

# ===================== 常量定义 =====================
# AppBar消息类型
class ABMsg(IntEnum):
    NEW = 0        # 注册AppBar
    REMOVE = 1     # 注销AppBar
    QUERY_POS = 2  # 查询系统可用区域
    SET_POS = 3    # 设置AppBar区域

# AppBar停靠边缘
class ABEdge(IntEnum):
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3

# Windows消息常量
WM_USER = 0x0400
APPBAR_CALLBACK = WM_USER + 0x01  # AppBar回调消息ID
LOGPIXELSX = 88  # DPI检测参数

# 扩展窗口样式，用于永不抢占焦点
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000

# ===================== 结构体定义 =====================
# AppBar交互必须用的结构体
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),        # 结构体大小
        ('hWnd', wintypes.HWND),           # 窗口句柄
        ('uCallbackMessage', wintypes.UINT), # 回调消息ID
        ('uEdge', wintypes.UINT),          # 停靠边
        ('rc', wintypes.RECT),             # 窗口矩形
        ('lParam', wintypes.LPARAM),       # 扩展参数
    ]

# ===================== DLL绑定 =====================
_shell32 = ctypes.WinDLL('shell32')
_user32 = ctypes.WinDLL('user32')
_gdi32 = ctypes.WinDLL('gdi32')

# 设置API参数类型
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
    """
    系统边缘停靠侧边栏窗口
    特性：
    1. 永不抢占焦点
    2. 高DPI感知
    3. 自动注册AppBar，支持左/右/上/下停靠
    """
    LOGICAL_WIDTH = 80   # 逻辑宽度（缩放前）
    LOGICAL_HEIGHT = 40  # 逻辑高度（缩放前）

    def __init__(self, edge=ABEdge.LEFT):
        super().__init__()
        self.edge = edge          # 停靠边
        self._registered = False  # AppBar注册状态

        # 设置固定宽高，按边缘类型决定
        if edge in (ABEdge.LEFT, ABEdge.RIGHT):
            self.setFixedWidth(self.LOGICAL_WIDTH)
        else:
            self.setFixedHeight(self.LOGICAL_HEIGHT)

        # Qt窗口标志：无边框 + 置顶
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        # 样式：深色背景 + 红色边框（调试用）
        self.setStyleSheet("""
            background:#2b2b2b;
            color:white;
            border:2px solid red;
        """)

        # DPI缩放比例
        self.dpi_scale = self.get_dpi_scale()
        self.winId()  # 强制生成窗口句柄
        self.disable_focus()  # 设置窗口永不抢占焦点

    # ===================== 禁止抢占焦点 =====================
    def disable_focus(self):
        """
        设置窗口扩展样式 WS_EX_NOACTIVATE
        确保侧边栏不会影响主窗口操作
        """
        hwnd = int(self.winId())
        ex_style = _user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        ex_style |= WS_EX_NOACTIVATE
        _user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, ex_style)

    # ===================== DPI相关 =====================
    def get_dpi_scale(self):
        """
        获取系统DPI缩放比例
        1. 获取屏幕设备上下文 HDC
        2. 调用GetDeviceCaps(LOGPIXELSX)
        3. 计算缩放比例 = dpi / 96
        """
        hdc = _user32.GetDC(0)
        dpi = _gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
        _user32.ReleaseDC(0, hdc)
        return dpi / 96.0

    def logical_to_physical(self, v):
        """逻辑像素 → 物理像素"""
        return int(v * self.dpi_scale)

    def physical_to_logical(self, v):
        """物理像素 → 逻辑像素"""
        return int(v / self.dpi_scale)

    # ===================== AppBar回调消息 =====================
    def nativeEvent(self, eventType, message):
        """
        监听Windows消息，处理AppBar回调
        msg.wParam==8 表示屏幕分辨率或任务栏位置变化
        """
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            if msg.message == APPBAR_CALLBACK:
                if msg.wParam == 8:
                    self.update_appbar_pos()  # 更新侧边栏位置
                return True, 0
        return super().nativeEvent(eventType, message)

    # ===================== AppBar注册 =====================
    def register_appbar(self):
        """注册侧边栏窗口到系统AppBar"""
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uCallbackMessage = APPBAR_CALLBACK

        result = _shell32.SHAppBarMessage(ABMsg.NEW, ctypes.byref(abd))
        if result:
            self._registered = True
            self.update_appbar_pos()  # 注册完成后立即更新位置

    def unregister_appbar(self):
        """注销AppBar"""
        if not self._registered:
            return
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = int(self.winId())
        _shell32.SHAppBarMessage(ABMsg.REMOVE, ctypes.byref(abd))
        self._registered = False

    # ===================== 侧边栏位置更新 =====================
    def update_appbar_pos(self):
        """根据停靠边和屏幕可用区域设置窗口位置"""
        if not self._registered:
            return

        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = int(self.winId())
        abd.uEdge = int(self.edge)

        screen = QApplication.primaryScreen().availableGeometry()  # 获取屏幕可用区域
        _shell32.SHAppBarMessage(ABMsg.QUERY_POS, ctypes.byref(abd))  # 查询系统可用区域

        # 简单演示：只处理左侧停靠
        if self.edge == ABEdge.LEFT:
            abd.rc.left = 0
            abd.rc.right = self.logical_to_physical(self.LOGICAL_WIDTH)
            abd.rc.top = screen.top()
            abd.rc.bottom = screen.bottom()

        _shell32.SHAppBarMessage(ABMsg.SET_POS, ctypes.byref(abd))  # 设置AppBar位置

        # Qt窗口最终几何
        self.setGeometry(
            abd.rc.left,
            abd.rc.top,
            self.physical_to_logical(abd.rc.right - abd.rc.left),
            abd.rc.bottom - abd.rc.top
        )

    # ===================== 生命周期 =====================
    def showEvent(self, e):
        """窗口显示时注册AppBar"""
        super().showEvent(e)
        # 延迟注册，确保winId已生成
        QTimer.singleShot(300, self.register_appbar)

    def closeEvent(self, e):
        """窗口关闭时注销AppBar"""
        self.unregister_appbar()
        super().closeEvent(e)








# ===================== main =====================
if __name__ == "__main__":
    """
    当该脚本被直接运行时，Python 会执行此部分。
    如果脚本被导入为模块，这部分代码不会执行。
    """

    import sys  # 导入 sys 模块，用于获取命令行参数和退出程序

    # 创建 Qt 应用程序对象
    # QApplication 是每个 Qt GUI 程序的核心，负责管理应用级别的事件循环和资源
    # sys.argv 是命令行参数列表，Qt 可能使用它解析启动选项
    app = QApplication(sys.argv)

    # 创建一个左侧停靠的 AppBar 窗口实例
    # edge=ABEdge.LEFT 指定停靠在屏幕左侧
    # DebugAppBar 是我们自定义的 AppBar 类，封装了注册、停靠和DPI处理
    bar = DebugAppBar(edge=ABEdge.LEFT)

    # 显示窗口
    # Qt 的窗口默认是隐藏的，必须调用 show() 才会显示在屏幕上
    bar.show()

    # 启动 Qt 事件循环
    # exec() 方法会阻塞，直到程序退出
    # sys.exit() 用来返回应用程序退出状态给操作系统（通常0表示正常退出）
    sys.exit(app.exec())
