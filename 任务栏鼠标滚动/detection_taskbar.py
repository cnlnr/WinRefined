# taskbar_mouse.py
import ctypes
from ctypes import wintypes
from pynput import mouse
import time

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
            return True
        hwnd = user32.GetParent(hwnd)
    return False

# -----------------------------
# 鼠标滚轮监听（只在任务栏触发）
# -----------------------------
def start_taskbar_wheel_listener(on_scroll_up=None, on_scroll_down=None, throttle=0.1):
    """
    启动滚轮监听，只在任务栏上触发
    throttle: 两次触发最小间隔（秒）
    """
    last_time = 0

    def on_scroll(x, y, dx, dy):
        nonlocal last_time
        if not is_mouse_over_taskbar():
            return
        now = time.time()
        if now - last_time < throttle:
            return  # 节流
        last_time = now
        if dy > 0 and on_scroll_up:
            on_scroll_up()
        elif dy < 0 and on_scroll_down:
            on_scroll_down()

    listener = mouse.Listener(on_scroll=on_scroll)
    listener.start()
    return listener


# -----------------------------
# 测试示例
# -----------------------------
if __name__ == "__main__":
    print("任务栏鼠标滚轮检测示例")

    def up_action():
        print("鼠标在任务栏，滚轮向上")

    def down_action():
        print("鼠标在任务栏，滚轮向下")

    listener = start_taskbar_wheel_listener(up_action, down_action, throttle=0.1)

    try:
        while True:
            if is_mouse_over_taskbar():
                print("鼠标在任务栏")
            else:
                print("鼠标不在任务栏")
            time.sleep(1)
    except KeyboardInterrupt:
        print("退出检测")
        listener.stop()
