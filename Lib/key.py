# key.py
"""
Windows虚拟按键模拟库
使用user32.dll实现按键模拟功能
无需额外依赖，仅需Python标准库
"""

import ctypes
import time

# ==================== 常量定义 ====================

# 键盘事件标志
KEYEVENTF_KEYUP = 0x0002

# 常用虚拟键码映射
VK_CODE = {
    # 字母键
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,

    # 数字键
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,

    # 功能键
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,

    # 控制键
    'backspace': 0x08, 'tab': 0x09, 'enter': 0x0D, 'shift': 0x10,
    'ctrl': 0x11, 'alt': 0x12, 'pause': 0x13, 'caps_lock': 0x14,
    'esc': 0x1B, 'space': 0x20, 'page_up': 0x21, 'page_down': 0x22,
    'end': 0x23, 'home': 0x24, 'left': 0x25, 'up': 0x26,
    'right': 0x27, 'down': 0x28, 'print_screen': 0x2C,
    'insert': 0x2D, 'delete': 0x2E, 'win': 0x5B,

    # 符号键
    ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD, '.': 0xBE,
    '/': 0xBF, '`': 0xC0, '[': 0xDB, '\\': 0xDC, ']': 0xDD, "'": 0xDE,
}

# 需要Shift组合的符号映射
SHIFT_SYMBOLS = {
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
    '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
    '_': '-', '+': '=', '{': '[', '}': ']', '|': '\\',
    ':': ';', '"': "'", '<': ',', '>': '.', '?': '/',
    '~': '`'
}

# 修饰键集合
MODIFIER_KEYS = {'shift', 'ctrl', 'alt', 'win'}

# ==================== 核心功能 ====================

class KeySimulator:
    """按键模拟器核心类"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        
    def _key_event(self, vk_code: int, is_keyup: bool = False):
        """发送键盘事件"""
        flags = KEYEVENTF_KEYUP if is_keyup else 0
        self.user32.keybd_event(vk_code, 0, flags, 0)
        
    def press(self, key: str):
        """按下指定按键"""
        vk = self._parse_key(key)
        self._key_event(vk, is_keyup=False)
        
    def release(self, key: str):
        """释放指定按键"""
        vk = self._parse_key(key)
        self._key_event(vk, is_keyup=True)
        
    def tap(self, key: str, delay: float = 0):
        """单击按键（按下后释放）"""
        self.press(key)
        if delay > 0:
            time.sleep(delay)
        self.release(key)
        
    def _parse_key(self, key: str) -> int:
        """解析按键字符串为虚拟键码"""
        key_lower = key.lower()
        if key_lower in VK_CODE:
            return VK_CODE[key_lower]
        raise ValueError(f"不支持的按键: {key}")
            
    def is_modifier(self, key: str) -> bool:
        """判断是否为修饰键"""
        return key.lower() in MODIFIER_KEYS

# 全局实例
_simulator = KeySimulator()

# ==================== 便捷API ====================

def press(key: str):
    """按下按键"""
    _simulator.press(key)

def release(key: str):
    """释放按键"""
    _simulator.release(key)

def tap(key: str, delay: float = 0):
    """单击按键"""
    _simulator.tap(key, delay)

def hotkey(*keys, delay: float = 0):
    """
    触发组合键
    
    Args:
        *keys: 按键序列（如 'ctrl', 'c'）
        delay: 按键间延迟（秒）
    """
    if not keys:
        return
    
    modifiers = []
    normal_keys = []
    
    for key in keys:
        if _simulator.is_modifier(key):
            modifiers.append(key)
        else:
            normal_keys.append(key)
    
    # 按下修饰键
    for mod in modifiers:
        press(mod)
        if delay > 0:
            time.sleep(delay)
    
    # 按下并释放普通键
    for key in normal_keys:
        tap(key, delay=delay)
    
    # 释放修饰键
    for mod in reversed(modifiers):
        release(mod)
        if delay > 0:
            time.sleep(delay)

def write(text: str, interval: float = 0):
    """
    输入文本字符串
    
    Args:
        text: 要输入的文本
        interval: 字符间延迟（秒），默认0秒
    """
    for char in text:
        if char.isupper():
            hotkey('shift', char.lower())
        elif char in SHIFT_SYMBOLS:
            hotkey('shift', SHIFT_SYMBOLS[char])
        elif char == ' ':
            tap('space', delay=0)
        elif char.lower() in VK_CODE:
            tap(char.lower(), delay=0)
        else:
            raise ValueError(f"无法直接输入字符: {char!r}")
        
        if interval > 0:
            time.sleep(interval)

# ==================== 示例用法 ====================

if __name__ == "__main__":
    print("3秒后开始测试...")
    time.sleep(3)

    # 打开开始菜单
    tap('win')
    time.sleep(1)

    # 输入记事本并回车
    write("notepad")
    tap('enter')
    time.sleep(1)
    tap('enter')
    time.sleep(2)

    # 输入Hello（自动处理大写）
    write("Hello", interval=0.1)
    tap('enter')
    tap('enter')

    time.sleep(1)

    # 测试符号键
    write("Shift+1 = !", interval=0.1)
    tap('enter')
    tap('f5')

    time.sleep(1)

    # 全选
    hotkey('ctrl', 'a')
    time.sleep(1)
