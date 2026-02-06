from detection_taskbar import start_taskbar_wheel_listener
from switch_desktop import ctrl_win_left_arrow, ctrl_win_right_arrow
import time

# 滚轮回调
def up_action():
    ctrl_win_left_arrow()

def down_action():
    ctrl_win_right_arrow()

# 启动滚轮监听
listener = start_taskbar_wheel_listener(up_action, down_action, throttle=0.0000001)

print("任务栏滚轮检测已启动，Ctrl+C 退出")

try:
    input("按任意键继续...")
except KeyboardInterrupt:
    print("退出检测")
    listener.stop()
