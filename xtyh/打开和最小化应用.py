# 将鼠标移至左上角触发 Win + 1 按键，可以配合 AI 使用
from lib import *

tracker = mouse.MouseTracker()
tracker.zb = (0, 0, 1, 1)

while True:
    tracker.zjkqy()
    print("游标进入监控区域，触发 Win + 1")
    key.hotkey('win', '1')

    tracker.bzjkqy()
    print("游标离开监控区域")
