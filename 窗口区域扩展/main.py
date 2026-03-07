import win32gui
from taskbar_scroll import listen_taskbar_scroll
import move_all

# 设定允许窗口活动的 X 坐标范围
# 如果你想让窗口能彻底滑出屏幕右侧，MAX_X 设为 3000
# 如果想让窗口能彻底滑出屏幕左侧，MIN_X 设为 -3000
MAX_X = 3000  
MIN_X = -3000 

step = 100 # 300 / 3

for scroll in listen_taskbar_scroll():
    # 获取第一个窗口作为坐标基准
    hwnds = move_all.get_visible_hwnds()
    if not hwnds: continue
    
    # 获取当前 X 坐标
    curr_x = win32gui.GetWindowRect(hwnds[0])[0]

    # 逻辑判断：
    # 1. 向上滚 (scroll > 0) 且 还没超过右边界 -> 允许右移
    if scroll > 0:
        if curr_x < MAX_X:
            for _ in range(3): move_all.move(step)
        else:
            print("已到达右侧极限")

    # 2. 向下滚 (scroll < 0) 且 还没超过左边界 -> 允许左移
    elif scroll < 0:
        if curr_x > MIN_X:
            for _ in range(3): move_all.move(-step)
        else:
            print("已到达左侧极限")
