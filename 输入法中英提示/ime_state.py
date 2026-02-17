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

if __name__ == "__main__":

    print(get_ime_state())
    print("=" * 30)

    print("当前输入法状态：", end="")
    result = is_chinese_ime_from_state()
    if result is None:
        print("大写锁定")
    else:
        print("中文" if result else "英文")