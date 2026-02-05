import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32

# ---------------- 获取鼠标下的窗口 ----------------
def get_hwnd_under_mouse():
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return user32.WindowFromPoint(pt)

# ---------------- 获取窗口类名 ----------------
def get_class_name(hwnd):
    if not hwnd:
        return ""
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value

# ---------------- 判断鼠标是否在任务栏 ----------------
def is_mouse_over_taskbar():
    hwnd = get_hwnd_under_mouse()
    while hwnd:
        class_name = get_class_name(hwnd)
        if class_name == "Shell_TrayWnd":  # 任务栏
            return True
        hwnd = user32.GetParent(hwnd)
    return False

# ---------------- 循环检测 ----------------
try:
    while True:
        if is_mouse_over_taskbar():
            print("鼠标在任务栏上")
        else:
            print("鼠标不在任务栏上")
        time.sleep(0.2)
except KeyboardInterrupt:
    print("退出")
