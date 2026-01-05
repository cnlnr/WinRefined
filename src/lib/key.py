import ctypes
from ctypes import wintypes

# 加载 user32.dll
user32 = ctypes.windll.user32

# 定义常量
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_LWIN = 0x5B

# 定义 KEYBDINPUT 结构体 (严格匹配 Windows API)
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),  # ULONG_PTR
    ]

# 定义 MOUSEINPUT 结构体（用于填充 union 大小）
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]

# 定义 HARDWAREINPUT 结构体（用于填充 union 大小）
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

# 定义 INPUT 结构体
class INPUT(ctypes.Structure):
    class _INPUTunion(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]
    
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUTunion),
    ]
    _anonymous_ = ("union",)

def show_desktop():
    """发送 Win + D 快捷键显示桌面"""
    print("Sending 'Win-D'")
    
    # 创建并初始化 INPUT 数组，所有字段默认设为0
    inputs = (INPUT * 4)()
    
    # 1. 按下 Win 键
    inputs[0].type = INPUT_KEYBOARD
    inputs[0].ki.wVk = VK_LWIN
    # 其他字段保持为0 (wScan=0, dwFlags=0, time=0, dwExtraInfo=0)
    
    # 2. 按下 D 键
    inputs[1].type = INPUT_KEYBOARD
    inputs[1].ki.wVk = ord('D')
    
    # 3. 释放 D 键
    inputs[2].type = INPUT_KEYBOARD
    inputs[2].ki.wVk = ord('D')
    inputs[2].ki.dwFlags = KEYEVENTF_KEYUP
    
    # 4. 释放 Win 键
    inputs[3].type = INPUT_KEYBOARD
    inputs[3].ki.wVk = VK_LWIN
    inputs[3].ki.dwFlags = KEYEVENTF_KEYUP
    
    # 发送输入
    result = user32.SendInput(len(inputs), ctypes.byref(inputs), ctypes.sizeof(INPUT))
    
    if result != len(inputs):
        error = ctypes.get_last_error()
        print(f"SendInput failed: 0x{error:08x}")
        return False
    
    print("SendInput succeeded!")
    return True

if __name__ == "__main__":
    show_desktop()