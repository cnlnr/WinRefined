from taskbar_mouse import TaskbarMonitor
from key_simulator import simulate_alt_tab_left


def stop_task():
    print("鼠标离开任务栏 → 停止函数")

monitor = TaskbarMonitor(start_task, stop_task)
monitor.start()

# 主线程可以干其他事情
try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    monitor.stop()
