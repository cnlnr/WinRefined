import cursor_direction
import time
import keyboard


while True:
        result = cursor_direction.wait_for_large_movement()
        if cursor_direction.is_mouse_pressed():
            continue  # 如果鼠标按钮被按下，跳过本次检测
        if result == "Right":
            keyboard.press_and_release('ctrl + win + right')
        elif result == "Left":
            keyboard.press_and_release('ctrl + win + left')
        elif result == "Up":
            keyboard.press_and_release('win + tab')
        time.sleep(0.4)

""" 提示
alt + esc 切换窗口
alt + shift + esc 反向切换窗口
win + d 显示桌面
"""