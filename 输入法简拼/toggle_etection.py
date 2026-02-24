from pynput import keyboard
import ctypes  # 用于调用Windows系统API检测按键状态

# 用于记录Ctrl键是否被按下（检测组合键用）
ctrl_pressed = False

# Windows系统API：获取键盘状态
def get_capslock_state():
    """获取CapsLock键的当前状态（跨Windows版本兼容）"""
    # 调用user32.dll的GetKeyState函数，VK_CAPITAL对应CapsLock键(0x14)
    hllDll = ctypes.WinDLL("User32.dll")
    # 返回值非0表示开启，0表示关闭
    return hllDll.GetKeyState(0x14) != 0

def start_keyboard_listener(key):
    global ctrl_pressed
    
    try:
        # 检测Ctrl键按下
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = True
        
        # 检测Shift键按下
        elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
            print("检测到 Shift 键被按下")
        
        # 检测Ctrl+空格组合键
        elif key == keyboard.Key.space and ctrl_pressed:
            print("检测到 Ctrl + 空格 组合键被按下")
            
    except Exception as e:
        print(f"按键按下检测异常: {e}")
        pass

def on_release(key):
    global ctrl_pressed
    
    try:
        # 检测CapsLock键释放（状态切换）
        if key == keyboard.Key.caps_lock:
            # 调用自定义函数获取CapsLock状态（兼容所有版本）
            caps_state = get_capslock_state()
            status = "开启" if caps_state else "关闭"
            print(f"CapsLock 键被切换，当前状态：{status}")
        
        # 释放Ctrl键时重置标记
        elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = False
        
        # 按ESC键退出监听
        elif key == keyboard.Key.esc:
            print("退出按键监听")
            return False
    except Exception as e:
        print(f"按键释放检测异常: {e}")
        pass

def start_keyboard_listener():
    """
    启动键盘监听器（封装核心监听逻辑）
    监听CapsLock、Shift、Ctrl+空格按键，按ESC退出
    """
    print("开始监听键盘事件（按ESC键退出）...")
    print("="*50)
    
    # 封装监听器启动逻辑
    with keyboard.Listener(on_press=start_keyboard_listener, on_release=on_release) as listener:
        listener.join()

# 启动键盘监听
if __name__ == "__main__":
    # 直接调用封装后的函数即可
    start_keyboard_listener()