from pynput import keyboard

def start_auto_quote(check_interval: float = 0.0):
    """
    启动自动触发单引号功能：按英文字母时自动触发单引号
    :param check_interval: 监听器线程阻塞间隔（默认0，不阻塞）
    """
    # 初始化键盘控制器
    keyboard_ctrl = keyboard.Controller()

    def on_press(key):
        try:
            if key.char.isalpha():
                keyboard_ctrl.press("'")
                keyboard_ctrl.release("'")
        except (AttributeError, TypeError):
            pass

    # 创建并启动监听器（后台运行，非阻塞）
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    # 可选：如果需要主线程阻塞，取消下面注释（按Ctrl+C退出）
    # import time
    # try:
    #     while True:
    #         time.sleep(check_interval or 1)
    # except KeyboardInterrupt:
    #     listener.stop()
    
    return listener  # 返回监听器实例，方便手动停止（如需）

# 一键启动（直接运行该文件时自动启动）
if __name__ == "__main__":
    print("自动触发单引号已启动！按英文字母会自动加单引号")
    print("如需终止，可关闭终端或调用 stop() 方法\n")
    listener = start_auto_quote()
    input("按回车键退出...\n")  # 阻塞主线程，等待用户输入后退出或使用.stop()