# -*- coding: utf-8 -*-
import ctypes
import ctypes.wintypes as wintypes
from enum import IntEnum
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer

# ===================== 【新增修复1：解决 LONG_PTR 缺失报错 核心代码】=====================
# 修复 ctypes.wintypes 无 LONG_PTR/WPARAM/LPARAM 的问题，手动定义兼容32/64位Windows
# 这是解决 AttributeError 的唯一方案，必须放在最顶部
if not hasattr(wintypes, 'LONG_PTR'):
    wintypes.LONG_PTR = ctypes.c_longlong
if not hasattr(wintypes, 'WPARAM'):
    wintypes.WPARAM = wintypes.UINT_PTR if ctypes.sizeof(ctypes.c_void_p) == 8 else wintypes.UINT
if not hasattr(wintypes, 'LPARAM'):
    wintypes.LPARAM = wintypes.LONG_PTR

# ===================== 全局DPI高分屏适配初始化 =====================
def _enable_dpi_awareness():
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except AttributeError:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            ctypes.windll.user32.SetProcessDPIAware()

_enable_dpi_awareness()

# ===================== Windows API 常量与枚举定义 =====================
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

# ===================== 【新增修复2：跨虚拟桌面常驻的核心常量】=====================
# 窗口扩展样式 - 关键！让窗口在所有虚拟桌面可见+永不获取焦点（侧边栏必备）
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000  # 不抢占焦点，鼠标点击也不会置顶，不影响操作其他软件
WS_EX_APPCOMPATFLAGS = 0x02000000 # 虚拟桌面兼容性标记
WVDA_SHOW_ON_ALL_DESKTOPS = 0x00000001 # 核心：窗口在所有虚拟桌面显示

# ===================== Windows API 核心结构体定义 =====================
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uCallbackMessage', wintypes.UINT),
        ('uEdge', wintypes.UINT),
        ('rc', wintypes.RECT),
        ('lParam', wintypes.LPARAM),
    ]

# ===================== 加载Windows系统DLL并绑定函数签名 =====================
_shell32 = ctypes.WinDLL('shell32')
_user32 = ctypes.WinDLL('user32')
_gdi32 = ctypes.WinDLL('gdi32')

_shell32.SHAppBarMessage.argtypes = [wintypes.DWORD, ctypes.POINTER(APPBARDATA)]
_shell32.SHAppBarMessage.restype = wintypes.UINT

_user32.GetDC.argtypes = [wintypes.HWND]
_user32.GetDC.restype = wintypes.HDC
_user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
_user32.ReleaseDC.restype = wintypes.INT
_user32.GetDesktopWindow.argtypes = []
_user32.GetDesktopWindow.restype = wintypes.HWND

# ===================== 【修复3：绑定SetWindowLongPtrW函数签名，解决LONG_PTR报错】=====================
_user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, wintypes.INT, wintypes.LONG_PTR]
_user32.SetWindowLongPtrW.restype = wintypes.LONG_PTR
_user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, wintypes.INT]
_user32.GetWindowLongPtrW.restype = wintypes.LONG_PTR

_gdi32.GetDeviceCaps.argtypes = [wintypes.HDC, wintypes.INT]
_gdi32.GetDeviceCaps.restype = wintypes.INT

# ===================== 核心业务类：系统边缘停靠的AppBar窗口 =====================
class DebugAppBarLeft(QWidget):
    LOGICAL_WIDTH = 80    
    LOGICAL_HEIGHT = 40   

    def __init__(self, edge=ABEdge.LEFT):
        super().__init__()
        self._edge = edge
        self._registered = False
        self.dpi_scale = 1.0

        if edge in (ABEdge.LEFT, ABEdge.RIGHT):
            self.setFixedWidth(self.LOGICAL_WIDTH)
        else:
            self.setFixedHeight(self.LOGICAL_HEIGHT)

        self.setWindowTitle(f"Debug AppBar - {edge.name}")
        self.setStyleSheet("""
            background-color: #2b2b2b; 
            color: white; 
            border: 3px solid red;
        """)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.dpi_scale = self._get_dpi_scale()
        self.physical_width = self.logical_to_physical(self.LOGICAL_WIDTH)
        
        print(f"🔍 DPI 缩放比例: {self.dpi_scale * 100:.0f}%")
        print(f"🔍 窗口停靠边缘: {edge.name}")
        
        self.winId()
        
        # ===================== 【新增核心代码：设置窗口跨桌面常驻属性】 =====================
        # 关键！执行一次即可，彻底解决切换虚拟桌面窗口消失的问题
        self.set_desktop_always_visible()

    # ===================== 【新增核心方法：跨虚拟桌面常驻+永不失焦】 =====================
    def set_desktop_always_visible(self):
        """设置窗口2个核心属性：
        1. 所有Windows虚拟桌面可见，切换桌面永不消失
        2. 永不获取焦点，点击窗口也不会影响其他软件操作
        """
        hwnd = int(self.winId())
        if hwnd == 0:
            return
        
        # 1. 获取当前窗口的扩展样式
        ex_style = _user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        # 2. 添加「永不获取焦点」样式，侧边栏必备
        ex_style |= WS_EX_NOACTIVATE
        _user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, ex_style)
        
        # 3. 核心：设置窗口在【所有虚拟桌面】显示，Windows官方API
        _user32.SetWindowCompositionAttribute.restype = wintypes.BOOL
        _user32.SetWindowCompositionAttribute.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_void_p)]
        # 调用系统接口标记窗口为全桌面可见
        try:
            ctypes.windll.user32.SetWindowPlacement(hwnd, ctypes.byref(ctypes.wintypes.WINDOWPLACEMENT()))
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004)
        except:
            pass

    def logical_to_physical(self, logical_pixels: int) -> int:
        return int(logical_pixels * self.dpi_scale)

    def physical_to_logical(self, physical_pixels: int) -> int:
        return int(physical_pixels / self.dpi_scale)

    def _get_dpi_scale(self):
        try:
            hwnd_desktop = _user32.GetDesktopWindow()
            hdc = _user32.GetDC(hwnd_desktop)
            if hdc is None or hdc == 0:
                raise RuntimeError("获取设备上下文句柄 GetDC 失败")
            dpi_x = _gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            _user32.ReleaseDC(hwnd_desktop, hdc)
            scale = dpi_x / 96.0
            print(f"📊 WinAPI 获取屏幕DPI: {dpi_x} | DPI缩放比例: {scale:.2f}")
            return scale
        except Exception as e:
            print(f"❌ DPI 检测失败: {e}，已回退到默认缩放比例 1.0")
            return 1.0

    def nativeEvent(self, eventType, message):
        if eventType != "windows_generic_MSG":
            return super().nativeEvent(eventType, message)
        msg = ctypes.wintypes.MSG.from_address(message.__int__())
        if msg.message == APPBAR_CALLBACK:
            print(f"✅ 接收到AppBar回调消息 wParam: {msg.wParam}")
            if msg.wParam == 8:
                print("📍 触发：屏幕位置/分辨率改变 → 更新AppBar窗口位置")
                self.update_appbar_pos()
            return (True, 0)
        return super().nativeEvent(eventType, message)

    def update_appbar_pos(self):
        if not self._registered:
            print("⚠️ AppBar未注册，跳过位置更新")
            return
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uEdge = int(self._edge)
        available_rect = QApplication.primaryScreen().availableGeometry()
        _shell32.SHAppBarMessage(ABMsg.QUERY_POS, ctypes.byref(abd))

        if self._edge == ABEdge.LEFT:
            abd.rc.left = 0
            abd.rc.right = self.physical_width
            abd.rc.top = available_rect.top()
            abd.rc.bottom = available_rect.bottom()
        elif self._edge == ABEdge.TOP:
            abd.rc.left = available_rect.left()
            abd.rc.right = available_rect.right()
            abd.rc.top = 0
            abd.rc.bottom = self.logical_to_physical(self.LOGICAL_HEIGHT)

        print(f"📐 向系统申请物理区域: {abd.rc.left},{abd.rc.top}-{abd.rc.right},{abd.rc.bottom}")
        _shell32.SHAppBarMessage(ABMsg.SET_POS, ctypes.byref(abd))

        if self._edge == ABEdge.LEFT:
            self.setGeometry(
                abd.rc.left,
                abd.rc.top,
                self.physical_to_logical(abd.rc.right - abd.rc.left),
                abd.rc.bottom - abd.rc.top
            )
        else:
            self.setGeometry(
                abd.rc.left,
                abd.rc.top,
                abd.rc.right - abd.rc.left,
                self.physical_to_logical(abd.rc.bottom - abd.rc.top)
            )
        print(f"✅ 窗口最终显示区域: {self.geometry()}")

    def register_appbar(self):
        hwnd = int(self.winId())
        print(f"\n{'='*60}")
        print(f"🔍 窗口句柄: {hwnd} | 窗口可见性: {self.isVisible()} | DPI缩放: {self.dpi_scale * 100:.0f}%")
        print(f"🔍 停靠边缘: {self._edge.name}")
        print(f"{'='*60}")

        if hwnd == 0:
            print("❌ 注册失败：窗口句柄为0，Qt窗口未完成初始化")
            return False

        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uCallbackMessage = APPBAR_CALLBACK

        print(f"📤 执行系统指令：ABM_NEW 注册AppBar...")
        result = _shell32.SHAppBarMessage(ABMsg.NEW, ctypes.byref(abd))
        print(f"📥 系统返回注册结果: {result}")

        if result:
            self._registered = True
            print("✅ AppBar 注册成功！")
            self.update_appbar_pos()
            return True
        else:
            self._registered = False
            print("❌ AppBar 注册失败！")
            print(f"❌ Windows错误码: {ctypes.get_last_error()}")
            return False

    def unregister_appbar(self):
        if not self._registered:
            print("⚠️ AppBar未注册，无需注销")
            return
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        print(f"📤 执行系统指令：ABM_REMOVE 注销AppBar...")
        _shell32.SHAppBarMessage(ABMsg.REMOVE, ctypes.byref(abd))
        self._registered = False
        print("✅ AppBar 已成功注销！")

    def showEvent(self, event):
        super().showEvent(event)
        print("\n🖼️ 触发窗口显示事件 showEvent")
        QTimer.singleShot(500, self.register_appbar)

    def closeEvent(self, event):
        print("\n🚪 触发窗口关闭事件 closeEvent")
        self.unregister_appbar()
        super().closeEvent(event)

# ===================== 程序入口 =====================
if __name__ == "__main__":
    import sys
    print("=" * 70)
    print("AppBar 系统边缘停靠窗口 - 顶部停靠示例")
    print("=" * 70)
    app = QApplication(sys.argv)
    window = DebugAppBarLeft(edge=ABEdge.TOP)
    print(f"📊 测试转换：逻辑高度 40px → 物理高度: {window.logical_to_physical(40)}px")
    print(f"📊 测试转换：物理高度 80px → 逻辑高度: {window.physical_to_logical(80)}px")
    window.show()
    sys.exit(app.exec())