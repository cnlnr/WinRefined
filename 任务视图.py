from pynput import mouse, keyboard
import time

# ==================== 配置区域 ====================
CONFIG = {
    'threshold': 30,      # 左上角检测区域(像素)
    'check_interval': 0.1, # 检测间隔(秒)
    'wait_interval': 0.05  # 等待时检测间隔(秒)
}

# ==================== 核心功能函数 ====================
def simulate_win_key(key):
    """通用函数：模拟 Win+任意键
    
    Args:
        key: 字符串(char)或按键对象(keyboard.Key)
    """
    # keyboard.Controller() 不支持 with 语句
    kb = keyboard.Controller()
    with kb.pressed(keyboard.Key.cmd):
        if isinstance(key, str):
            kb.tap(key)
        else:
            kb.tap(key)
    # 无需手动释放，Python会自动处理

def wait_mouse_leave_top_left(threshold=None):
    """阻塞等待鼠标离开左上角"""
    threshold = threshold or CONFIG['threshold']
    with mouse.Controller() as m:  # mouse.Controller 支持 with
        while True:
            x, y = m.position
            if x >= threshold or y >= threshold:
                break
            time.sleep(CONFIG['wait_interval'])

def is_mouse_in_top_left(threshold=None):
    """检测鼠标是否在左上角"""
    threshold = threshold or CONFIG['threshold']
    with mouse.Controller() as m:
        x, y = m.position
        return x < threshold and y < threshold

# ==================== 功能模式 ====================
def task_view():
    """任务视图功能 (Win+Tab)"""
    simulate_win_key(keyboard.Key.tab)

def launch_first_app():
    """启动第一个任务栏应用 (Win+1)"""
    simulate_win_key('1')

# ==================== 监控主函数 ====================
def run_monitor(trigger_func, name=""):
    """通用监控循环"""
    print(f"\n{'='*40}")
    print(f"  {name} 监控模式")
    print(f"{'='*40}")
    print(f"检测区域: x < {CONFIG['threshold']}, y < {CONFIG['threshold']}")
    print("按 Ctrl+C 退出\n")
    
    try:
        while True:
            if is_mouse_in_top_left():
                print(f"[{time.strftime('%H:%M:%S')}] 触发{name}")
                trigger_func()
                
                print("等待鼠标离开检测区域...")
                wait_mouse_leave_top_left()
                print("✓ 已离开，继续监听\n")
            
            time.sleep(CONFIG['check_interval'])
    except KeyboardInterrupt:
        print("\n程序已退出")

# ==================== 用户可调用的函数 ====================
def rwst():
    """任务视图模式 (Win+Tab)"""
    run_monitor(task_view, "任务视图(Win+Tab)")

def yy():
    """应用启动模式 (Win+1)"""
    run_monitor(launch_first_app, "启动应用(Win+1)")
