import ctypes
import ctypes.wintypes as wintypes
from enum import IntEnum
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer

# DPI 感知设置
def _enable_dpi_awareness():
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except AttributeError:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            ctypes.windll.user32.SetProcessDPIAware()

_enable_dpi_awareness()

# Windows API 定义
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

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uCallbackMessage', wintypes.UINT),
        ('uEdge', wintypes.UINT),
        ('rc', wintypes.RECT),
        ('lParam', wintypes.LPARAM),
    ]

# 加载 DLL 并定义函数签名
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

_gdi32.GetDeviceCaps.argtypes = [wintypes.HDC, wintypes.INT]
_gdi32.GetDeviceCaps.restype = wintypes.INT

# ==================== 核心类 ====================
class DebugAppBarLeft(QWidget):
    LOGICAL_WIDTH = 80
    LOGICAL_HEIGHT = 40
    
    def __init__(self, edge=ABEdge.LEFT):
        super().__init__()
        
        self._edge = edge
        
        # 根据边缘设置窗口尺寸
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
        self.physical_width = int(self.LOGICAL_WIDTH * self.dpi_scale)
        
        print(f"🔍 DPI 缩放: {self.dpi_scale * 100:.0f}%")
        print(f"🔍 边缘: {edge.name}")
        
        self._registered = False
        self.winId()
    
    # ==================== 修复：添加缺失的方法 ====================
    def logical_to_physical(self, logical_pixels: int) -> int:
        """Qt 逻辑像素 → Windows 物理像素"""
        return int(logical_pixels * self.dpi_scale)
    
    def physical_to_logical(self, physical_pixels: int) -> int:
        """Windows 物理像素 → Qt 逻辑像素"""
        return int(physical_pixels / self.dpi_scale)
    # ==================== 修复结束 ====================
    
    def _get_dpi_scale(self):
        try:
            hwnd_desktop = _user32.GetDesktopWindow()
            hdc = _user32.GetDC(hwnd_desktop)
            
            if hdc is None or hdc == 0:
                raise RuntimeError("GetDC failed")
            
            dpi_x = _gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            _user32.ReleaseDC(hwnd_desktop, hdc)
            
            scale = dpi_x / 96.0
            print(f"📊 WinAPI DPI: {dpi_x} (缩放: {scale:.2f})")
            return scale
            
        except Exception as e:
            print(f"❌ DPI 检测失败: {e}，回退到 1.0")
            return 1.0
    
    def nativeEvent(self, eventType, message):
        if eventType != "windows_generic_MSG":
            return super().nativeEvent(eventType, message)
        
        msg = ctypes.wintypes.MSG.from_address(message.__int__())
        
        if msg.message == APPBAR_CALLBACK:
            print(f"✅ AppBarCallback wParam: {msg.wParam}")
            if msg.wParam == 8:
                print("📍 位置改变")
                self.update_appbar_pos()
            return (True, 0)
        
        return super().nativeEvent(eventType, message)
    
    def update_appbar_pos(self):
        if not self._registered:
            return
        
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uEdge = int(self._edge)
        
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        available_rect = screen.availableGeometry()
        
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
            physical_height = int(self.LOGICAL_HEIGHT * self.dpi_scale)
            abd.rc.bottom = physical_height
        
        print(f"📐 请求: {abd.rc.left},{abd.rc.top}-{abd.rc.right},{abd.rc.bottom}")
        
        _shell32.SHAppBarMessage(ABMsg.SET_POS, ctypes.byref(abd))
        
        if self._edge == ABEdge.LEFT:
            self.setGeometry(
                abd.rc.left,
                abd.rc.top,
                int((abd.rc.right - abd.rc.left) / self.dpi_scale),
                abd.rc.bottom - abd.rc.top
            )
        else:
            self.setGeometry(
                abd.rc.left,
                abd.rc.top,
                abd.rc.right - abd.rc.left,
                int((abd.rc.bottom - abd.rc.top) / self.dpi_scale)
            )
        
        print(f"✅ 最终: {self.geometry()}")
    
    def register_appbar(self):
        hwnd = int(self.winId())
        print(f"\n{'='*60}")
        print(f"🔍 句柄: {hwnd} | 可见: {self.isVisible()} | DPI: {self.dpi_scale * 100:.0f}%")
        print(f"🔍 边缘: {self._edge.name}")
        print(f"{'='*60}")
        
        if hwnd == 0:
            print("❌ 错误：句柄为 0")
            return False
        
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uCallbackMessage = APPBAR_CALLBACK
        
        print(f"📤 ABM_NEW...")
        result = _shell32.SHAppBarMessage(ABMsg.NEW, ctypes.byref(abd))
        print(f"📥 结果: {result}")
        
        if result:
            self._registered = True
            print("✅ 注册成功")
            self.update_appbar_pos()
            return True
        else:
            print("❌ 注册失败")
            error = ctypes.get_last_error()
            print(f"❌ 错误码: {error}")
            return False
    
    def unregister_appbar(self):
        if not self._registered:
            return
        
        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        
        print(f"📤 ABM_REMOVE...")
        _shell32.SHAppBarMessage(ABMsg.REMOVE, ctypes.byref(abd))
        
        self._registered = False
        print("✅ 已注销")
    
    def showEvent(self, event):
        super().showEvent(event)
        print("\n🖼️ 显示事件")
        QTimer.singleShot(500, self.register_appbar)
    
    def closeEvent(self, event):
        print("\n🚪 关闭事件")
        self.unregister_appbar()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    print("=" * 70)
    print("AppBar 顶部注册示例")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    
    # 创建顶部应用栏
    window = DebugAppBarLeft(edge=ABEdge.TOP)
    
    # 测试坐标转换方法
    print(f"📊 逻辑高度 40px → 物理高度: {window.logical_to_physical(40)}px")
    print(f"📊 物理高度 80px → 逻辑高度: {window.physical_to_logical(80)}px")
    
    window.show()
    
    sys.exit(app.exec())