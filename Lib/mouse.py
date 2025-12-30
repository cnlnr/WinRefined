# mouse_tracker.py
import ctypes
from ctypes import wintypes
import time

# 加载Windows API
user32 = ctypes.windll.user32

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), 
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

class MouseTracker:
    """极简鼠标追踪器 - 状态驱动"""
    
    def __init__(self, check_interval=0.05):
        self.areas = []
        self.check_interval = check_interval
    
    def get_pos(self):
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y
    
    @property
    def zb(self):
        if self.areas:
            r = self.areas[0]['rect']
            return (r.left, r.top, r.right, r.bottom)
        return None
    
    @zb.setter
    def zb(self, rect):
        """设置监控区域 (x1, y1, x2, y2)"""
        self.areas = [{
            'rect': RECT(*rect),
            'inside': False  # 无需初始化，每次调用独立判断
        }]
    
    def zjkqy(self):
        """**阻塞直到鼠标在监控区域内**（已在里面则立即返回）"""
        if not self.areas:
            return
        
        rect = self.areas[0]['rect']
        
        while True:
            x, y = self.get_pos()
            inside = (rect.left <= x <= rect.right and 
                     rect.top <= y <= rect.bottom)
            
            # 已在区域内 → 立即返回
            if inside:
                return
            
            time.sleep(self.check_interval)
    
    def bzjkqy(self):
        """**阻塞直到鼠标在监控区域外**（已在外面则立即返回）"""
        if not self.areas:
            return
        
        rect = self.areas[0]['rect']
        
        while True:
            x, y = self.get_pos()
            inside = (rect.left <= x <= rect.right and 
                     rect.top <= y <= rect.bottom)
            
            # 已在区域外 → 立即返回
            if not inside:
                return
            
            time.sleep(self.check_interval)


# ==================== 正确用法 ====================
if __name__ == '__main__':
    tracker = MouseTracker(check_interval=0.05)
    tracker.zb = (0, 0, 1, 1)
    
    print("开始监控，按 Ctrl+C 退出")
    try:
        while True:
            # 阻塞直到"在里面"
            tracker.zjkqy()
            print("游标进入监控区域")
            
            # 阻塞直到"在外面"
            tracker.bzjkqy()
            print("游标离开监控区域")


            

    except KeyboardInterrupt:
        print("\n监控已停止")