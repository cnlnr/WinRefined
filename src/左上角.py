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
        elif keyboard.is_pressed('alt'):
            keyboard.press_and_release('tab')
        else:
            keyboard.press_and_release('win + 1')

            # 模拟gnome（win + tab）打开任务视图
            # keyboard.press_and_release('win + tab')


