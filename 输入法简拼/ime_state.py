from pywinauto import Desktop
import ctypes

def get_ime_state():

    desktop = Desktop(backend="uia")
    taskbar = desktop.window(class_name="Shell_TrayWnd")
    xaml = taskbar.child_window(
        class_name="Windows.UI.Input.InputSite.WindowClass",
        control_type="Pane"
    )

    for btn in xaml.children(
        control_type="Button",
        class_name="SystemTray.NormalButton"
    ):
        text = btn.window_text()
        if "输入指示器" in text:
            return text

    return None

def is_capslock_on():
    return (ctypes.windll.user32.GetKeyState(0x14) & 1) != 0

def is_chinese_ime_from_state():
    state = get_ime_state()
    if is_capslock_on():
        return None
    elif "中文" in state:
        return True
    elif "英语" in state:
        return False
    else:
        raise ValueError("无法识别输入法状态")

import time

def monitor_ime_state(check_interval: float = 0.2):
    """
    循环监控输入法状态，仅当状态变化时返回原始状态值
    
    :param check_interval: 检测间隔时间（秒），默认0.2秒
    :return: 生成器，返回值为 None（大写锁定）/ True（中文）/ False（英文）
    """
    # 初始化上一次状态为特殊值，确保第一次能检测到初始状态
    last_state = object()
    
    try:
        while True:
            # 获取当前输入法原始状态
            current_state = is_chinese_ime_from_state()
            
            # 仅状态变化时返回值
            if current_state != last_state:
                yield current_state  # 返回最新的状态值
                last_state = current_state  # 更新上一次状态
            
            # 使用传入的时间参数控制检测频率
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        # 捕获Ctrl+C，静默退出（无打印）
        return

if __name__ == "__main__":

    print(get_ime_state())
    print("=" * 30)

    print("当前输入法状态：", end="")
    result = is_chinese_ime_from_state()
    if result is None:
        print("大写锁定")
    else:
        print("中文" if result else "英文")