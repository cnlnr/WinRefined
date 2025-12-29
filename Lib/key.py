#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows虚拟按键模拟库
使用SendInput API，支持字符串调用，无需任何第三方库
"""
import ctypes
from ctypes import wintypes
import time

# -------------------- 兼容性修复 --------------------
# 某些Python版本缺少ULONG_PTR，用c_void_p替代
_ULONG_PTR = ctypes.c_void_p

# -------------------- 核心：user32.dll接口 --------------------
_user32 = ctypes.WinDLL('user32', use_last_error=True)

# 定义SendInput函数原型
_SendInput = _user32.SendInput
_SendInput.argtypes = [
    wintypes.UINT,      # nInputs
    ctypes.c_void_p,    # pInputs（指向INPUT数组的指针）
    ctypes.c_int        # cbSize
]
_SendInput.restype = wintypes.UINT

# 定义keybd_event函数原型（备用）
_keybd_event = _user32.keybd_event
_keybd_event.argtypes = [
    wintypes.BYTE,      # bVk
    wintypes.BYTE,      # bScan
    wintypes.DWORD,     # dwFlags
    _ULONG_PTR          # dwExtraInfo
]
_keybd_event.restype = None

# 常量定义
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

# -------------------- 键码结构体定义（必须完整） --------------------
class KEYBDINPUT(ctypes.Structure):
    """键盘输入结构体（24字节）"""
    _fields_ = [
        ("wVk", wintypes.WORD),         # 虚拟键码（2字节）
        ("wScan", wintypes.WORD),       # 扫描码（2字节）
        ("dwFlags", wintypes.DWORD),    # 标志位（4字节）
        ("time", wintypes.DWORD),       # 时间戳（4字节）
        ("dwExtraInfo", _ULONG_PTR)     # 额外信息（指针大小）
    ]

class InputUnion(ctypes.Union):
    """联合体，所有输入类型共享内存"""
    _fields_ = [("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    """顶层输入结构体（28字节）"""
    _fields_ = [
        ("type", wintypes.DWORD),       # 输入类型（4字节）
        ("u", InputUnion)               # 联合体（24字节）
    ]

# -------------------- 键码字典（支持点号访问） --------------------
class _VKDict(dict):
    """支持点号访问的嵌套字典"""
    def __getattr__(self, key):
        try:
            val = self[key]
            return val if not isinstance(val, dict) else _VKDict(val)
        except KeyError:
            raise AttributeError(f"键 '{key}' 不存在")

# 主键码表（模块化分类）
VK = _VKDict({
    "MOD": {                # 修饰键
        "WIN_L": 0x5B,     "WIN_R": 0x5C,
        "ALT": 0x12,       "CTRL": 0x11,       "SHIFT": 0x10,
        "CAPS": 0x14,      "ESC": 0x1B,
    },
    "KEY": {                # 功能键
        "TAB": 0x09,       "ENTER": 0x0D,      "SPACE": 0x20,
        "BACK": 0x08,      "DELETE": 0x2E,     "HOME": 0x24,
        "END": 0x23,       "PAGE_UP": 0x21,    "PAGE_DOWN": 0x22,
        "PRINT": 0x2C,     "INSERT": 0x2D,
    },
    "ARROW": {              # 方向键
        "LEFT": 0x25,      "RIGHT": 0x27,
        "UP": 0x26,        "DOWN": 0x28,
    },
    "FUNC": {               # F1-F12
        **{f"F{i}": 0x6F + i for i in range(1, 13)}
    },
    "LETTER": {             # 字母 A-Z
        **{chr(65 + i): 0x41 + i for i in range(26)}
    },
    "NUM": {                # 数字 0-9
        **{f"D{i}": 0x30 + i for i in range(10)}
    },
})

# -------------------- 底层操作函数 --------------------
def _key_down(vk: int):
    """按下虚拟键"""
    _keybd_event(vk, 0, 0, 0)

def _key_up(vk: int):
    """释放虚拟键"""
    _keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

def press_key(vk: int, duration: float = 0.02):
    """按下并释放单个键（使用keybd_event，简单可靠）"""
    _key_down(vk)
    time.sleep(duration)
    _key_up(vk)

def press_combo(*vks: int, duration: float = 0.02):
    """组合键：顺序按下 → 逆序释放"""
    codes = [_resolve_vk(v) for v in vks]
    
    # 顺序按下
    for code in codes:
        _key_down(code)
    time.sleep(duration)
    
    # 逆序释放
    for code in reversed(codes):
        _key_up(code)

def send_input_key(vk: int):
    """使用SendInput发送单个键（按下+释放）"""
    # 按下
    input_down = INPUT()
    input_down.type = INPUT_KEYBOARD
    input_down.u.ki.wVk = vk
    input_down.u.ki.dwFlags = 0
    
    # 释放
    input_up = INPUT()
    input_up.type = INPUT_KEYBOARD
    input_up.u.ki.wVk = vk
    input_up.u.ki.dwFlags = KEYEVENTF_KEYUP
    
    # 打包成数组
    inputs = (INPUT * 2)(input_down, input_up)
    
    # 调用SendInput
    result = _SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))
    if result != 2:
        raise ctypes.WinError(ctypes.get_last_error())

# -------------------- 键名解析辅助 --------------------
def _resolve_vk(key):
    """智能解析键码：支持int、str、dict路径"""
    if isinstance(key, int):
        return key
    
    if isinstance(key, str):
        name = key.upper().replace("+", "")
        if name in _KEY_NAME_MAP:
            return _KEY_NAME_MAP[name]
        raise KeyError(f"未知键名: {key}")
    
    raise TypeError(f"不支持的键类型: {type(key)}")

# 键名到虚拟键码的映射表（大小写不敏感）
_KEY_NAME_MAP = {
    # 修饰键
    "WIN": VK.MOD.WIN_L, "LWIN": VK.MOD.WIN_L, "RWIN": VK.MOD.WIN_R,
    "ALT": VK.MOD.ALT, "CTRL": VK.MOD.CTRL, "SHIFT": VK.MOD.SHIFT,
    "ESC": VK.MOD.ESC, "CAPS": VK.MOD.CAPS,
    
    # 功能键
    "TAB": VK.KEY.TAB, "ENTER": VK.KEY.ENTER, "SPACE": VK.KEY.SPACE,
    "BACK": VK.KEY.BACK, "DELETE": VK.KEY.DELETE, "HOME": VK.KEY.HOME,
    "END": VK.KEY.END, "PAGEUP": VK.KEY.PAGE_UP, "PAGEDOWN": VK.KEY.PAGE_DOWN,
    "PRINT": VK.KEY.PRINT, "INSERT": VK.KEY.INSERT,
    
    # 方向键
    "LEFT": VK.ARROW.LEFT, "RIGHT": VK.ARROW.RIGHT,
    "UP": VK.ARROW.UP, "DOWN": VK.ARROW.DOWN,
    
    # F1-F12
    **{f"F{i}": getattr(VK.FUNC, f"F{i}") for i in range(1, 13)},
    
    # 字母 A-Z
    **{chr(65+i): getattr(VK.LETTER, chr(65+i)) for i in range(26)},
    
    # 数字 0-9
    **{str(i): getattr(VK.NUM, f"D{i}") for i in range(10)},
}

# -------------------- 极简接口（用户主函数） --------------------
def key(*key_names, duration: float = 0.02):
    """
    极简接口：通过键名模拟按键
    
    参数：
        key_names: 可变参数，1个=单键，多个=组合键
        duration: 按键保持时间（秒）
    
    示例：
        key("Win", "Tab")      # 打开任务视图
        key("F1")              # 按F1
        key("Ctrl", "A")       # 全选
        key("Alt", "F4")       # 关闭窗口
    """
    if not key_names:
        raise ValueError("至少要传一个键名")
    
    # 解析所有键名
    vks = [name for name in key_names]
    
    # 自动判断单键/组合键
    if len(vks) == 1:
        # 单键：按下并释放
        vk_code = _resolve_vk(vks[0])
        press_key(vk_code, duration)
    else:
        # 组合键：顺序按下→逆序释放
        codes = [_resolve_vk(v) for v in vks]
        press_combo(*codes, duration=duration)

# -------------------- 预定义常用快捷键 --------------------
class Shortcuts:
    """常用快捷键命名空间"""
    TASK_VIEW = lambda: key("Win", "Tab")
    SHOW_DESKTOP = lambda: key("Win", "D")
    ALT_TAB = lambda: key("Alt", "Tab")
    LOCK = lambda: key("Win", "L")
    TASK_MANAGER = lambda: key("Ctrl", "Shift", "Esc")
    RUN = lambda: key("Win", "R")
    SAVE = lambda: key("Ctrl", "S")
    COPY = lambda: key("Ctrl", "C")
    PASTE = lambda: key("Ctrl", "V")
    UNDO = lambda: key("Ctrl", "Z")
    REDO = lambda: key("Ctrl", "Y")
    SELECT_ALL = lambda: key("Ctrl", "A")
    CLOSE_WINDOW = lambda: key("Alt", "F4")
    SWITCH_LEFT = lambda: key("Win", "Ctrl", "Left")
    SWITCH_RIGHT = lambda: key("Win", "Ctrl", "Right")

# 动态导出为模块级函数（方便直接调用）
def _export_shortcuts():
    for name, func in Shortcuts.__dict__.items():
        if name.isupper() and callable(func):
            globals()[name.lower()] = func

_export_shortcuts()

# -------------------- 自测代码 --------------------
if __name__ == '__main__':
    print("将模拟按下win键")
    key("Win")
