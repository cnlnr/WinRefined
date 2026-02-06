from pynput.keyboard import Controller, Key
import time

keyboard = Controller()

def simulate_ctrl_alt_tab_left():
    """
    模拟按下 Ctrl+Alt+Tab，一次性触发窗口切换界面
    """
    keyboard.press(Key.ctrl)      # 按下 Ctrl
    keyboard.press(Key.alt)       # 按下 Alt
    keyboard.press(Key.tab)       # 按下 Tab
    # ---------------- 松开所有键 ----------------
    keyboard.release(Key.tab)
    keyboard.release(Key.alt)
    keyboard.release(Key.ctrl)

# ---------------- 示例 / 测试 ----------------
if __name__ == "__main__":
    print("运行示例：模拟 Ctrl+Alt+Tab")
    simulate_ctrl_alt_tab_left()
    print("模拟完成")
