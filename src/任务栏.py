import sys
import ctypes
from ctypes import wintypes
from PySide6 import QtCore, QtWidgets

# Windows API 常量
ABM_NEW = 0
ABM_REMOVE = 1
ABM_QUERYPOS = 2
ABM_SETPOS = 3
ABE_LEFT = 0

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uCallbackMessage', wintypes.UINT),
        ('uEdge', wintypes.UINT),
        ('rc', wintypes.RECT),
        ('lParam', wintypes.LPARAM),
    ]

shell32 = ctypes.windll.shell32

class AppBarWindow(QtWidgets.QWidget):
    def __init__(self, edge=ABE_LEFT, width=120):
        """
        创建AppBar窗口
        edge: ABE_LEFT/ABE_TOP/ABE_RIGHT/ABE_BOTTOM
        width: AppBar厚度（像素）
        """
        super().__init__()
        self.appbar_registered = False
        self.edge = edge
        self.thickness = width
        
        # 无边框工具窗口
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        
        # 半透明背景（看得见，不干扰）
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: rgba(0, 120, 212, 0.3);")  # 30%不透明蓝色
        
        # 必须先show再注册
        self.show()
        
        # 注册AppBar
        self.register_appbar()
        
    def register_appbar(self):
        """注册为AppBar（文档标准流程）"""
        try:
            hwnd = int(self.winId())
            
            # 1. 创建并注册
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(APPBARDATA)
            abd.hWnd = hwnd
            abd.uCallbackMessage = QtCore.QEvent.registerEventType()
            
            if shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(abd)):
                self.appbar_registered = True
                print(f"✓ AppBar已注册，边缘={self.edge}, 厚度={self.thickness}px")
            else:
                print("✗ AppBar注册失败")
                return False
                
            # 2. 查询并设置位置
            self.set_appbar_position()
            return True
            
        except Exception as e:
            print(f"异常: {e}")
            return False
            
    def set_appbar_position(self):
        """设置AppBar位置（文档推荐流程）"""
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        
        # 先设置窗口大小
        if self.edge in (ABE_LEFT, ABE_RIGHT):
            self.setFixedSize(self.thickness, screen.height())
        else:
            self.setFixedSize(screen.width(), self.thickness)
        
        # 配置APPBARDATA
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = int(self.winId())
        abd.uEdge = self.edge
        
        # 初始矩形
        if self.edge == ABE_LEFT:
            abd.rc.left = 0
            abd.rc.top = screen.top()
            abd.rc.right = self.thickness
            abd.rc.bottom = screen.bottom()
        elif self.edge == ABE_RIGHT:
            abd.rc.left = screen.width() - self.thickness
            abd.rc.top = screen.top()
            abd.rc.right = screen.width()
            abd.rc.bottom = screen.bottom()
        # 顶部和底部同理...
        
        # 查询系统调整
        shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
        
        # 设置最终位置
        if self.edge in (ABE_LEFT, ABE_RIGHT):
            abd.rc.right = abd.rc.left + self.thickness
        else:
            abd.rc.bottom = abd.rc.top + self.thickness
            
        shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))
        
        # 移动窗口
        self.move(abd.rc.left, abd.rc.top)
        
    def unregister_appbar(self):
        """注销AppBar（必须调用）"""
        if self.appbar_registered:
            hwnd = int(self.winId())
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(APPBARDATA)
            abd.hWnd = hwnd
            shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(abd))
            self.appbar_registered = False
            print("AppBar已注销")
            
    def nativeEvent(self, eventType, message):
        """响应系统消息"""
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            if hasattr(self, 'callback_message') and msg.message == self.callback_message:
                self.set_appbar_position()
                return True, 0
        return super().nativeEvent(eventType, message)
        
    def closeEvent(self, event):
        """窗口关闭时注销"""
        self.unregister_appbar()
        super().closeEvent(event)

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 创建左侧AppBar
    left_bar = AppBarWindow(edge=ABE_LEFT, width=120)
    
    print("""
=== AppBar任务栏已启动 ===

测试方法：
1. 打开浏览器（Chrome/Edge/Firefox）
2. 按F11进入全屏模式
3. 如果浏览器内容从左侧120px后开始 → 成功✓
4. 如果浏览器占满全屏 → 该浏览器不支持AppBar避让

注意：
- 最大化窗口（不是F11）一定会避让AppBar
- 部分全屏应用（游戏、视频播放器）可能绕过AppBar
- 这是Windows规范行为，不是代码问题
""")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()