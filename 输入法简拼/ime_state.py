from pywinauto import Desktop
import ctypes
import time

def get_ime_state():
    """获取系统托盘输入指示器的文本状态"""
    desktop = Desktop(backend="uia")
    taskbar = desktop.window(class_name="Shell_TrayWnd")
    xaml = taskbar.child_window(class_name="Windows.UI.Input.InputSite.WindowClass", control_type="Pane")
    for btn in xaml.children(control_type="Button", class_name="SystemTray.NormalButton"):
        if "输入指示器" in btn.window_text():
            return btn.window_text()
    return None

def is_capslock_on():
    """检测大写锁定键是否开启"""
    return (ctypes.windll.user32.GetKeyState(0x14) & 1) != 0

def is_chinese_ime():
    """判断当前是否为中文输入法（大写锁定时返回None）"""
    state = get_ime_state()
    if is_capslock_on():
        return None
    return "中文" in state if state else False

def monitor_ime_state(check_interval=0.2):
    """
    生成器函数：循环监控输入法状态，仅状态变化时返回值
    :param check_interval: 检测间隔（秒），默认0.2秒
    :yield: None(大写锁定)/True(中文)/False(英文)
    """
    last_state = object()
    while True:
        current_state = is_chinese_ime()
        if current_state != last_state:
            yield current_state
            last_state = current_state
        time.sleep(check_interval)

if __name__ == "__main__":
    # 创建输入法状态监控生成器
    ime_monitor = monitor_ime_state()
    # 用for循环遍历生成器（生成器是无限迭代的，循环会持续运行）
    for current_state in ime_monitor:
        print(get_ime_state())  # 打印原始状态文本
        print("=" * 30)
        print("当前输入法状态：", end="")
        # 解析状态并输出
        print("大写锁定" if current_state is None else "中文" if current_state else "英文")