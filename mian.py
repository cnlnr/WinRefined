from pynput import keyboard
from pynput.keyboard import Key, KeyCode, Controller

# 初始化键盘控制器，用于模拟按键操作
keyboard_ctrl = Controller()
# 记录已按下的键，避免长按重复触发
pressed_keys = set()

def on_press(key):
    """按键按下时的回调函数"""
    # 避免重复触发：已按下的键不再处理
    if key in pressed_keys:
        return
    pressed_keys.add(key)

    # 退出逻辑：按 Esc 键停止监听
    if key == Key.esc:
        print("已按下 Esc，程序退出")
        return False  # 返回 False 终止监听器

    # 仅处理英文字母（区分大小写）
    try:
        char = key.char
        if char.isalpha():
            print(f"检测到字母: {char}，模拟按下并释放单引号(')键")
            # 模拟按下单引号键 → 释放单引号键（完整的按键操作）
            keyboard_ctrl.press("'")
            keyboard_ctrl.release("'")
    except AttributeError:
        # 非字符键（如Ctrl、方向键等），不做处理
        pass

def on_release(key):
    """按键松开时的回调函数"""
    # 从已按下集合中移除，恢复可触发状态
    if key in pressed_keys:
        pressed_keys.remove(key)

if __name__ == "__main__":
    print("程序已启动！")
    print("功能：按任意英文字母键，自动模拟输入单引号(')")
    print("退出：按 Esc 键\n")
    
    # 启动键盘监听器
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()