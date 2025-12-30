# 将鼠标移至左上角触发 Win + Tab 按键
from lib import *

tracker = mouse.MouseTracker()
tracker.zb = (0, 0, 1, 1)

while True:
    tracker.zjkqy()
    print("游标进入监控区域，触发 Win + Tab")
    key.hotkey('win', 'tab')

    tracker.bzjkqy()
    print("游标离开监控区域")
