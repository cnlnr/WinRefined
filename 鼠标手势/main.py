import cursor_direction
import time
import keyboard


while True:
        result = cursor_direction.wait_for_large_movement(up_th=400, down_th=400, left_th=500, right_th=550, 
                                                          sample_interval=0.002, duration=0.02)
        if cursor_direction.is_mouse_pressed():
            continue  # 如果鼠标按钮被按下，跳过本次检测
        if result == "Right":
            keyboard.press_and_release('ctrl + win + right')
        elif result == "Left":
            keyboard.press_and_release('ctrl + win + left')
        time.sleep(0.4)

""" 提示
alt + esc 切换窗口
alt + shift + esc 反向切换窗口
win + tab
win + d
"""