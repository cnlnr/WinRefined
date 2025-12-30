# 从lib.py导入mouse和key模块，通过lib.py的路径配置解决导入问题
from lib import *

tracker = mouse.MouseTracker()
tracker.zb = (0, 0, 1, 1)

while True:
    tracker.zjkqy()
    print("游标进入监控区域，触发 Win + Tab")
    key.hotkey('win', 'tab')

    tracker.bzjkqy()
    print("游标离开监控区域")
