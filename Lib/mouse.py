# mouse_tracker.py
import ctypes
from ctypes import wintypes
import time

# 加载Windows API
user32 = ctypes.windll.user32

# 定义结构体
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), 
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

class MouseTracker:
    """极简鼠标追踪器"""
    
    def __init__(self):
        self.areas = []  # 只存区域和回调
    
    def get_pos(self):
        """获取当前鼠标位置（单位：像素）"""
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y
    
    def add_area(self, rect, on_enter, on_leave):
        """添加监控区域
        rect: (x1, y1, x2, y2) 矩形坐标
        on_enter: 进入区域的函数
        on_leave: 离开区域的函数
        """
        self.areas.append({
            'rect': RECT(*rect),
            'enter': on_enter,
            'leave': on_leave,
            'inside': False  # 记录当前状态
        })
    
    def check_areas(self, x, y):
        """检查坐标是否触发区域事件"""
        for area in self.areas:
            # 判断点是否在矩形内
            inside = (area['rect'].left <= x <= area['rect'].right and
                     area['rect'].top <= y <= area['rect'].bottom)
            
            # 状态变化才触发回调
            if inside and not area['inside']:
                area['inside'] = True
                if area['enter']:
                    area['enter'](x, y)
            elif not inside and area['inside']:
                area['inside'] = False
                if area['leave']:
                    area['leave'](x, y)


# ==================== 用法示例 ====================
if __name__ == '__main__':
    def on_enter(x, y):
        print(f"🔥 进入区域！坐标: ({x}, {y})")
    
    def on_leave(x, y):
        print(f"👋 离开区域！坐标: ({x}, {y})")
    
    # 创建追踪器
    tracker = MouseTracker()
    
    # 添加一个监控区域（左上角）
    tracker.add_area((0, 0, 1, 1), on_enter, on_leave)
    
    # 用户自己控制循环
    print("开始监控，按 Ctrl+C 退出")
    try:
        while True:
            # 获取鼠标位置
            x, y = tracker.get_pos()
            
            # 检查区域事件
            tracker.check_areas(x, y)
            
            # ✅ 用户自己的代码可以放在这里
            # print(f"当前位置: ({x}, {y})")
            # if x > 1000:
            #     do_something_else()
            
            time.sleep(0.05)  # 控制刷新频率
    except KeyboardInterrupt:
        print("\n监控已停止")