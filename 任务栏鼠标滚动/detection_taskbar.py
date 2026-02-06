import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

# -----------------------------
# 获取鼠标下窗口句柄
# -----------------------------
def get_hwnd_under_mouse():
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return user32.WindowFromPoint(pt)

# -----------------------------
# 获取窗口类名
# -----------------------------
def get_class_name(hwnd):
    if not hwnd:
        return ""
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value

# -----------------------------
# 检测鼠标是否在任务栏
# -----------------------------
def is_mouse_over_taskbar():
    hwnd = get_hwnd_under_mouse()
    while hwnd:
        if get_class_name(hwnd) == "Shell_TrayWnd":
            return True  # 鼠标下窗口是任务栏或任务栏子控件
        hwnd = user32.GetParent(hwnd)
    return False

# -----------------------------
# 主循环示例
# -----------------------------
if __name__ == "__main__":
    import time
    
    try:
        while True:
            if is_mouse_over_taskbar():
                print("鼠标在任务栏")
            else:
                print("鼠标不在任务栏")
            time.sleep(0.2)  # 每 0.2 秒检测一次
    except KeyboardInterrupt:
        print("退出检测")
