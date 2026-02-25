import time
import pyautogui
import math
import ctypes

def calculate_cumulative_movement(sample_interval=0.01, duration=0.2):
    """
    计算指定时长内鼠标的累计移动距离和主方向
    sample_interval: 采样间隔（越小越精准，但占用资源略高）
    duration: 总检测时长
    """
    # 初始化变量
    total_distance = 0  # 累计移动距离
    prev_x, prev_y = pyautogui.position()  # 上一个采样点坐标
    total_dx = 0  # 累计x轴位移（右正左负）
    total_dy = 0  # 累计y轴位移（下正上负）
    
    # 计算需要采样的次数
    sample_count = int(duration / sample_interval)
    
    for _ in range(sample_count):
        time.sleep(sample_interval)
        curr_x, curr_y = pyautogui.position()
        
        # 计算当前采样点与上一个采样点的欧氏距离（真实移动距离）
        dx = curr_x - prev_x
        dy = curr_y - prev_y
        distance = math.hypot(dx, dy)  # 等价于sqrt(dx² + dy²)
        
        # 累加距离和位移
        total_distance += distance
        total_dx += dx
        total_dy += dy
        
        # 更新上一个采样点坐标
        prev_x, prev_y = curr_x, curr_y
    
    # 确定主移动方向
    moves = {
        "Right": max(total_dx, 0),
        "Left": max(-total_dx, 0),
        "Down": max(total_dy, 0),
        "Up": max(-total_dy, 0),
    }
    main_direction = max(moves, key=moves.get)
    
    return main_direction, total_distance

def wait_for_large_movement(up_th=400, down_th=400, left_th=500, right_th=550, 
                           sample_interval=0.002, duration=0.02):
    """
    循环检测鼠标累计移动，超过阈值时返回方向
    解决了"移动后回原点"导致的误判问题
    """
    while True:
        direction, total_distance = calculate_cumulative_movement(sample_interval, duration)
        
        # 判断是否超过对应方向的阈值
        if direction == "Up" and total_distance > up_th:
            return "Up"
        if direction == "Down" and total_distance > down_th:
            return "Down"
        if direction == "Left" and total_distance > left_th:
            return "Left"
        if direction == "Right" and total_distance > right_th:
            return "Right"


# 鼠标按键代码
VK_LBUTTON = 0x01  # 左键
VK_RBUTTON = 0x02  # 右键
VK_MBUTTON = 0x04  # 中键

def is_mouse_pressed() -> bool:
    """
    检测鼠标任意键（左/中/右）是否按下
    返回: True/False
    """
    left = ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000 != 0
    right = ctypes.windll.user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000 != 0
    middle = ctypes.windll.user32.GetAsyncKeyState(VK_MBUTTON) & 0x8000 != 0
    return left or right or middle


if __name__ == "__main__":
    print("开始检测鼠标大幅移动...")
    print("提示：采样间隔0.01s，检测时长0.2s，可根据需要调整参数")
    while True:
        result = wait_for_large_movement()
        print("触发方向:", result)
        print("鼠标点击状态:", "按下" if is_mouse_pressed() else "未按")
        time.sleep(0.4)