from pynput.keyboard import Controller, Key
import time

# 全局键盘控制器
kb = Controller()

# -----------------------------
# 模拟 Ctrl + Win + 左箭头
# -----------------------------
def ctrl_win_left_arrow():
    kb.press(Key.ctrl)   # 按下 Ctrl
    kb.press(Key.cmd)    # 按下 Win
    kb.press(Key.left)   # 按下左箭头
    kb.release(Key.left)
    kb.release(Key.cmd)
    kb.release(Key.ctrl)

# -----------------------------
# 模拟 Ctrl + Win + 右箭头
# -----------------------------
def ctrl_win_right_arrow():
    kb.press(Key.ctrl)   # 按下 Ctrl
    kb.press(Key.cmd)    # 按下 Win
    kb.press(Key.right)  # 按下右箭头
    kb.release(Key.right)
    kb.release(Key.cmd)
    kb.release(Key.ctrl)

# -----------------------------
# 测试示例
# -----------------------------
if __name__ == "__main__":
    print("模拟 Ctrl + Win + 右箭头（切换到右侧桌面）")
    ctrl_win_right_arrow()
    time.sleep(0.5)
    print("模拟 Ctrl + Win + 左箭头（切换到左侧桌面）")
    ctrl_win_left_arrow()