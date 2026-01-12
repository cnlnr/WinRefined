# appbar.py
"""
Windows AppBar 封装库
提供注册和注销应用程序工具栏的功能
"""

import ctypes
from ctypes import wintypes
from enum import IntEnum

# Windows API 常量
class ABMsg(IntEnum):
    """AppBar message identifiers"""
    NEW = 0x00000000
    REMOVE = 0x00000001
    QUERY_POS = 0x00000002
    SET_POS = 0x00000003
    GET_STATE = 0x00000004
    GET_TASKBAR_POS = 0x00000005
    ACTIVATE = 0x00000006
    GET_AUTOHIDEBAR = 0x00000007
    SET_AUTOHIDEBAR = 0x00000008
    WINDOWPOS_CHANGED = 0x00000009
    SET_STATE = 0x0000000A

class ABEdge(IntEnum):
    """AppBar edge identifiers"""
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3

# Windows 消息
WM_USER = 0x0400
APPBAR_CALLBACK = WM_USER + 0x01

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

# 加载 shell32.dll
_shell32 = ctypes.windll.shell32

# 全局变量
_g_uSide = ABEdge.TOP
_g_fAppRegistered = False

class AppBar:
    """AppBar 管理类"""
    
    def __init__(self):
        self._hwnd = None
        self._registered = False
        self._edge = ABEdge.TOP
    
    @property
    def is_registered(self) -> bool:
        """检查 AppBar 是否已注册"""
        return self._registered
    
    @property
    def edge(self) -> ABEdge:
        """获取当前屏幕边缘"""
        return self._edge
    
    def register(self, hwnd: int) -> bool:
        """
        注册 AppBar
        
        Args:
            hwnd: 窗口句柄 (int)
            
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        global _g_fAppRegistered, _g_uSide
        
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uCallbackMessage = APPBAR_CALLBACK
        
        # 注册 AppBar
        result = _shell32.SHAppBarMessage(ABMsg.NEW, ctypes.byref(abd))
        
        if result:
            self._registered = True
            self._hwnd = hwnd
            self._edge = ABEdge.TOP
            _g_fAppRegistered = True
            _g_uSide = ABEdge.TOP
            return True
        
        return False
    
    def unregister(self) -> bool:
        """
        注销 AppBar
        
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        global _g_fAppRegistered
        
        if not self._hwnd or not self._registered:
            return False
        
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = self._hwnd
        
        # 注销 AppBar
        _shell32.SHAppBarMessage(ABMsg.REMOVE, ctypes.byref(abd))
        
        self._registered = False
        self._hwnd = None
        _g_fAppRegistered = False
        
        return True
    
    def __del__(self):
        """析构函数，确保注销 AppBar"""
        if self._registered:
            self.unregister()


# 函数式接口（类似原始 C++ 代码）
def register_access_bar(hwnd: int, register: bool) -> bool:
    """
    注册或注销 AppBar
    
    Args:
        hwnd: 窗口句柄
        register: True 注册，False 注销
        
    Returns:
        bool: 成功返回 True，失败返回 False
    """
    global _g_uSide, _g_fAppRegistered
    
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    
    if register:
        abd.uCallbackMessage = APPBAR_CALLBACK
        
        # 注册 AppBar
        if not _shell32.SHAppBarMessage(ABMsg.NEW, ctypes.byref(abd)):
            return False
        
        _g_uSide = ABEdge.TOP
        _g_fAppRegistered = True
        return True
    
    else:
        # 注销 AppBar
        _shell32.SHAppBarMessage(ABMsg.REMOVE, ctypes.byref(abd))
        _g_fAppRegistered = False
        return True


# 获取全局状态
def get_registration_state() -> bool:
    """获取 AppBar 注册状态"""
    return _g_fAppRegistered


def get_current_edge() -> ABEdge:
    """获取当前屏幕边缘"""
    return _g_uSide