import win32gui
from pynput.keyboard import Controller, Key

# -----------------------------
# 全局键盘控制器
# -----------------------------
kb = Controller()

# -----------------------------
# 检测 Alt+Tab（任务切换）窗口是否存在
# -----------------------------
def is_task_switch_active():
    """检查任务切换界面是否存在"""
    found = False
    def enum_cb(hwnd, _):
        nonlocal found
        if win32gui.IsWindowVisible(hwnd):
            if win32gui.GetClassName(hwnd) == "XamlExplorerHostIslandWindow" and win32gui.GetWindowText(hwnd) == "任务切换":
                found = True
    win32gui.EnumWindows(enum_cb, None)
    return found

# -----------------------------
# 按 ESC 关闭任务切换
# -----------------------------
def exit_task_switch():
    """如果任务切换界面存在，则按 ESC 关闭"""
    if is_task_switch_active():
        kb.press(Key.esc)
        kb.release(Key.esc)

# -----------------------------
# 模拟 Ctrl+Alt+Tab 触发任务切换
# -----------------------------
def trigger_task_switch():
    """模拟一次性按下 Ctrl+Alt+Tab 触发任务切换界面"""
    kb.press(Key.ctrl)
    kb.press(Key.alt)
    kb.press(Key.tab)
    kb.release(Key.tab)
    kb.release(Key.alt)
    kb.release(Key.ctrl)


# -----------------------------
# 模拟按下键盘左箭头
# -----------------------------
def left_arrow():
    kb.press(Key.left)    # 按下左箭头
    kb.release(Key.left)  # 松开左箭头

# -----------------------------
# 模拟按下键盘右箭头
# -----------------------------
def right_arrow():
    kb.press(Key.right)    # 按下右箭头
    kb.release(Key.right)  # 松开右箭头



# -----------------------------
# 示例调用
# -----------------------------
if __name__ == "__main__":
    print("模拟 Ctrl+Alt+Tab → 触发任务切换")
    trigger_task_switch()

    # 给系统一点时间显示任务切换界面
    import time
    time.sleep(1)
    
    print("模拟按下左箭头")
    left_arrow()
    time.sleep(1)
    print("模拟按下右箭头")
    right_arrow()
    time.sleep(1)
    
    print("检测并按 ESC 关闭任务切换")
    exit_task_switch()
    print("完成")
