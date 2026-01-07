"""
将鼠标移动到左上角区域时，触发相应的操作，如模拟按下 Win+Tab
按住Ctrl键时，启动任务管理器
按住alt切换应用
"""
from pynput import mouse
import keyboard

def caozuo():
    # 打开或关闭任务栏第一个应用，试试放ai应用
    # keyboard.press_and_release('win + 1')

    # 打开或关闭任务视图
    # keyboard.press_and_release('win + tab')


    if keyboard.is_pressed('ctrl'):
        keyboard.press_and_release('shift + esc')
    elif keyboard.is_pressed('alt'):
        keyboard.press_and_release('tab + ')
    else:
        keyboard.press_and_release('win + tab')
        



def create_mouse_handler():
    """创建鼠标处理器，使用闭包保存状态"""
    inside_region = False  # 外部函数变量
    
    def on_move(x, y):
        nonlocal inside_region  # 声明修改外部变量
        
        currently_inside = x < 10 and y < 10
        
        if currently_inside and not inside_region:
            inside_region = True
            caozuo()

        elif not currently_inside and inside_region:
            inside_region = False
    
    return on_move  # 返回内部函数

# 创建监听器
listener = mouse.Listener(on_move=create_mouse_handler())
listener.start()
listener.join()