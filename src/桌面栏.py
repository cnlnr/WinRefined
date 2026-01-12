# appbar_left_dpi_final.py
"""
AppBar 左侧注册 - 最终修复版本
修复内容：
1. GetDeviceCaps 在 gdi32.dll 而非 user32.dll
2. 正确加载所有 Windows API 函数
3. 完整添加函数原型定义
"""

import ctypes
import ctypes.wintypes as wintypes
from enum import IntEnum
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QRect, QTimer
import sys

# 设置进程 DPI 感知（必须在任何 Qt 代码之前）
try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    print("✅ 已设置进程 DPI 感知（Per Monitor V2）")
except:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        print("✅ 已设置进程 DPI 感知（Per Monitor）")
    except:
        ctypes.windll.user32.SetProcessDPIAware()
        print("⚠️ 已设置进程 DPI 感知（System DPI）")

# Windows API 定义
class ABMsg(IntEnum):
    NEW = 0x00000000
    REMOVE = 0x00000001
    QUERY_POS = 0x00000002
    SET_POS = 0x00000003

class ABEdge(IntEnum):
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3

WM_USER = 0x0400
APPBAR_CALLBACK = WM_USER + 0x01

# Windows 常量
LOGPIXELSX = 88
LOGPIXELSY = 90

# AppBar 数据结构
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uCallbackMessage', wintypes.UINT),
        ('uEdge', wintypes.UINT),
        ('rc', wintypes.RECT),
        ('lParam', wintypes.LPARAM),
    ]

# 加载 Windows DLL
_shell32 = ctypes.windll.shell32
_user32 = ctypes.windll.user32
_gdi32 = ctypes.windll.gdi32  # GetDeviceCaps 在这里！

# 定义 GetDeviceCaps 函数原型（关键修复）
_gdi32.GetDeviceCaps.argtypes = [wintypes.HDC, wintypes.INT]
_gdi32.GetDeviceCaps.restype = wintypes.INT

# 定义其他需要的 WinAPI 函数原型
_user32.GetDC.argtypes = [wintypes.HWND]
_user32.GetDC.restype = wintypes.HDC
_user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
_user32.ReleaseDC.restype = wintypes.INT
_user32.GetDesktopWindow.argtypes = []
_user32.GetDesktopWindow.restype = wintypes.HWND

class DebugAppBarLeft(QWidget):
    """左侧 AppBar - DPI 感知版本"""
    
    LOGICAL_WIDTH = 80  # 逻辑像素（设计尺寸）
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AppBar - LEFT - DPI Fixed")
        self.setStyleSheet("""
            background-color: #2b2b2b; 
            color: white; 
            border: 3px solid red;
        """)
        
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # 计算 DPI 缩放
        self.dpi_scale = self.get_dpi_scale()
        self.physical_width = int(self.LOGICAL_WIDTH * self.dpi_scale)
        
        print(f"🔍 DPI 缩放比例: {self.dpi_scale * 100:.0f}%")
        print(f"🔍 逻辑宽度: {self.LOGICAL_WIDTH}px → 物理宽度: {self.physical_width}px")
        
        # 设置 Qt 窗口逻辑尺寸
        self.setFixedWidth(self.LOGICAL_WIDTH)
        
        self._registered = False
        self._edge = ABEdge.LEFT
        
        # 强制创建句柄
        self.winId()
    
    def get_dpi_scale(self):
        """获取 DPI 缩放比例"""
        # 方式1：Qt 方法
        screen = QApplication.primaryScreen()
        qt_dpi = screen.logicalDotsPerInch()
        qt_scale = qt_dpi / 96.0
        
        # 方式2：WinAPI 方法（gdi32.dll）
        hwnd_desktop = _user32.GetDesktopWindow()
        hdc = _user32.GetDC(hwnd_desktop)
        winapi_dpi = _gdi32.GetDeviceCaps(hdc, LOGPIXELSX)  # 正确调用
        _user32.ReleaseDC(hwnd_desktop, hdc)
        
        api_scale = winapi_dpi / 96.0
        
        print(f"📊 Qt DPI: {qt_dpi} (缩放: {qt_scale:.2f})")
        print(f"📊 WinAPI DPI: {winapi_dpi} (缩放: {api_scale:.2f})")
        
        return api_scale  # 使用 WinAPI 值
    
    def logical_to_physical(self, logical_pixels):
        """Qt 逻辑像素 → Windows 物理像素"""
        return int(logical_pixels * self.dpi_scale)
    
    def physical_to_logical(self, physical_pixels):
        """Windows 物理像素 → Qt 逻辑像素"""
        return int(physical_pixels / self.dpi_scale)
    
    def nativeEvent(self, eventType, message):
        """处理 Windows 原生消息"""
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            
            if msg.message == APPBAR_CALLBACK:
                print(f"✅ 收到 AppBarCallback! wParam: {msg.wParam}")
                if msg.wParam == 8:  # ABN_POSCHANGED
                    print("📍 AppBar 位置改变")
                    self.update_appbar_pos()
                return True, 0
        
        return super().nativeEvent(eventType, message)
    
    def update_appbar_pos(self):
        """更新 AppBar 位置"""
        if not self._registered:
            return
            
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uEdge = int(self._edge)
        
        # 获取可用屏幕区域
        screen = QApplication.primaryScreen()
        available_rect = screen.availableGeometry()
        
        print(f"🖥️ 可用屏幕区域: {available_rect}")
        
        # 查询系统允许的位置
        _shell32.SHAppBarMessage(ABMsg.QUERY_POS, ctypes.byref(abd))
        
        # 设置左侧区域坐标（物理像素）
        abd.rc.left = 0
        abd.rc.right = self.physical_width
        abd.rc.top = available_rect.top()
        abd.rc.bottom = available_rect.bottom()
        
        print(f"📐 请求物理坐标: ({abd.rc.left},{abd.rc.top}) - ({abd.rc.right},{abd.rc.bottom})")
        
        # 设置位置
        _shell32.SHAppBarMessage(ABMsg.SET_POS, ctypes.byref(abd))
        
        # 应用最终位置（转换回逻辑像素）
        self.setGeometry(
            abd.rc.left,
            abd.rc.top,
            self.physical_to_logical(abd.rc.right - abd.rc.left),
            abd.rc.bottom - abd.rc.top
        )
        
        print(f"✅ 最终窗口几何 (逻辑): {self.geometry()}")
    
    def register_appbar(self):
        """注册左侧 AppBar"""
        hwnd = int(self.winId())
        print(f"\n{'='*60}")
        print(f"🔍 窗口句柄: {hwnd}")
        print(f"🔍 是否可见: {self.isVisible()}")
        print(f"🔍 DPI 缩放: {self.dpi_scale * 100:.0f}%")
        print(f"{'='*60}")
        
        if hwnd == 0:
            print("❌ 错误：窗口句柄为 0！")
            return False
        
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uCallbackMessage = APPBAR_CALLBACK
        
        print(f"📤 发送 ABM_NEW 消息到左侧...")
        result = _shell32.SHAppBarMessage(ABMsg.NEW, ctypes.byref(abd))
        print(f"📥 返回结果: {result}")
        
        if result:
            self._registered = True
            print("✅ AppBar 左侧注册成功！")
            self.update_appbar_pos()
            return True
        else:
            print("❌ AppBar 左侧注册失败！")
            error = ctypes.get_last_error()
            print(f"❌ 错误码: {error}")
            return False
    
    def unregister_appbar(self):
        """注销 AppBar"""
        if not self._registered:
            return
            
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        
        print(f"📤 发送 ABM_REMOVE 消息...")
        _shell32.SHAppBarMessage(ABMsg.REMOVE, ctypes.byref(abd))
        
        self._registered = False
        print("✅ AppBar 已注销")
    
    def showEvent(self, event):
        """窗口显示时注册"""
        super().showEvent(event)
        print("\n🖼️ 窗口显示事件触发")
        QTimer.singleShot(500, self.register_appbar)
    
    def closeEvent(self, event):
        """窗口关闭时注销"""
        print("\n🚪 窗口关闭事件触发")
        self.unregister_appbar()
        super().closeEvent(event)

def main():
    print("=" * 70)
    print("AppBar 左侧注册 - DPI 最终修复版")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    window = DebugAppBarLeft()
    window.show()
    
    print(f"\n📱 主窗口句柄: {int(window.winId())}")
    print(f"📱 窗口是否可见: {window.isVisible()}")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()