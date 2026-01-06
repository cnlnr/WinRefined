import keyboard
import time

def send_ctrl_a():
    """发送Ctrl+A组合键"""
    keyboard.send('ctrl+a')
    keyboard.send('ctrl+v')
    # keyboard.send('ctrl+s')

# 注册热键：将Insert映射为Ctrl+A，并抑制原始按键
keyboard.add_hotkey('insert', send_ctrl_a, suppress=True)

print("Insert键重映射已启动")
print("现在按Insert键将触发Ctrl+A，Insert功能被屏蔽")
print("按Ctrl+C退出程序")

try:
    # 保持程序运行
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n程序已退出")