import ctypes
from ctypes import wintypes
import time

# 导入Windows API函数
user32 = ctypes.windll.user32


def get_mouse_pos():
    """
    使用Windows API获取当前鼠标位置
    
    返回：(x, y) 坐标元组
    """
    point = ctypes.wintypes.POINT()
    # GetCursorPos返回BOOL值，True表示成功
    if user32.GetCursorPos(ctypes.byref(point)):
        return point.x, point.y
    else:
        # 如果获取失败，返回上次已知位置或默认值
        if hasattr(get_mouse_pos, "_last_pos"):
            return get_mouse_pos._last_pos
        return (0, 0)

# 初始化上次已知位置
get_mouse_pos._last_pos = (0, 0)


def shubiao_in_quyu(x1, y1, x2, y2):
    """
    阻塞式区域检测（使用Windows API，提高可靠性）
    
    首次调用返回当前状态，之后阻塞直到状态变化
    """
    # 函数属性：记忆状态和配置
    if not hasattr(shubiao_in_quyu, "_cfg"):
        shubiao_in_quyu._cfg = {
            'x_min': min(x1, x2),
            'x_max': max(x1, x2),
            'y_min': min(y1, y2),
            'y_max': max(y1, y2),
            'last': None
        }
    
    cfg = shubiao_in_quyu._cfg
    
    # 首次调用：立即返回当前状态
    if cfg['last'] is None:
        x, y = get_mouse_pos()
        # 更新上次已知位置
        get_mouse_pos._last_pos = (x, y)
        cfg['last'] = cfg['x_min'] <= x <= cfg['x_max'] and cfg['y_min'] <= y <= cfg['y_max']
        return cfg['last']
    
    # 持续监测直到状态变化
    while True:
        time.sleep(0.01)
        x, y = get_mouse_pos()
        # 更新上次已知位置
        get_mouse_pos._last_pos = (x, y)
        current = cfg['x_min'] <= x <= cfg['x_max'] and cfg['y_min'] <= y <= cfg['y_max']
        
        if current != cfg['last']:
            cfg['last'] = current
            return current

# ==================== 使用示例 ====================

if __name__ == "__main__":
    try:
        while True:
            # 这个调用会阻塞，直到状态变化
            status = shubiao_in_quyu(0, 0, 500, 300)
            
            if status:
                print("✅ 鼠标在指定区域内")
            else:
                print("❌ 鼠标不在指定区域内")
            
    except KeyboardInterrupt:
        print("\n监控已停止")