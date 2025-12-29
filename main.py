from pynput import mouse, keyboard
import time

# ==================== 极简配置 ====================
THRESHOLD = 30
CHECK_INTERVAL = 0.1
WAIT_INTERVAL = 0.05
_kb = keyboard.Controller()

# ==================== 合并后的监控函数 ====================
def monitor(action):
    """监控循环（检测+等待全部内联）"""
    print(f"\n{'='*40}")
    print(f"  监控模式: {action.__name__}")
    print(f"{'='*40}")
    print(f"热区: 左上角 {THRESHOLD}x{THRESHOLD} 像素")
    print("按 Ctrl+C 退出\n")
    
    try:
        while True:
            # 直接内联：检测鼠标是否在左上角
            with mouse.Controller() as m:
                x, y = m.position
                if x < THRESHOLD and y < THRESHOLD:
                    print(f"[{time.strftime('%H:%M:%S')}] 触发 {action.__name__}")
                    action()
                    
                    # 直接内联：等待鼠标离开
                    print("等待鼠标离开...")
                    while True:
                        x, y = m.position
                        if x >= THRESHOLD or y >= THRESHOLD:
                            break
                        time.sleep(WAIT_INTERVAL)
                    
                    print("✓ 已离开，继续监听\n")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n程序已退出")





# ==================== 只保留一个工具函数 ====================
def send_win_hotkey(key):
    """发送 Win+组合键"""
    with _kb.pressed(keyboard.Key.cmd):
        _kb.tap(key)

# ==================== 快捷键函数 ====================
def rwst():
    """任务视图"""
    send_win_hotkey(keyboard.Key.tab)

def yy():
    """启动应用"""
    send_win_hotkey('1')



# ==================== 主函数（只负责选择启动） ====================
def main():
    monitor(rwst) # 如果你想要使用 Win+1 快捷键，修改括号内容为 yy

if __name__ == "__main__":
    main()