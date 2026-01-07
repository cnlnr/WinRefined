"""
将鼠标移动到左上角区域时，触发相应的操作，如模拟按下 Win+Tab
按住Ctrl键时，启动任务管理器
按住alt切换应用
"""
from 区域检测 import shubiao_in_quyu
import keyboard


while True:
    if shubiao_in_quyu(0, 0, 10, 10):
        if keyboard.is_pressed('ctrl'):
            keyboard.press_and_release('shift + esc')
        else:
            keyboard.press_and_release('win + tab')




# 打开或关闭任务栏第一个应用，试试放ai应用
# keyboard.press_and_release('win + 1')

# 打开或关闭任务视图
# keyboard.press_and_release('win + t')

# 打开或关闭任务管理器
# keyboard.press_and_release('ctrl + shift + esc')

