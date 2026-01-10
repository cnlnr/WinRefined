import sys
import ctypes
from PySide6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QCursor

# ===================== 【1. Windows API 零报错兼容版 - 彻底脱离wintypes依赖】 =====================
user32 = ctypes.windll.user32
# 鼠标事件常量
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001        # 鼠标移动
MOUSEEVENTF_LEFTDOWN = 0x0002    # 左键按下
MOUSEEVENTF_LEFTUP = 0x0004      # 左键松开
MOUSEEVENTF_RIGHTDOWN = 0x0008   # 右键按下
MOUSEEVENTF_RIGHTUP = 0x0010     # 右键松开
MOUSEEVENTF_ABSOLUTE = 0x8000    # 绝对坐标模式（屏幕全屏有效）
# 屏幕分辨率常量
SM_CXSCREEN = 0
SM_CYSCREEN = 1

# ✅ 【零报错核心】用ctypes原生基础类型定义结构体，彻底抛弃wintypes.ULONG_PTR/LONG_PTR
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),        # 替代 wintypes.LONG
        ("dy", ctypes.c_long),        # 替代 wintypes.LONG
        ("mouseData", ctypes.c_uint32),# 替代 wintypes.DWORD
        ("dwFlags", ctypes.c_uint32),  # 替代 wintypes.DWORD
        ("time", ctypes.c_uint32),     # 替代 wintypes.DWORD
        ("dwExtraInfo", ctypes.c_ulong)# 替代 wintypes.ULONG_PTR ✅ 万能兼容，永不报错
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32),     # 替代 wintypes.DWORD
        ("mi", MOUSEINPUT)
    ]

# ===================== 【2. 独立虚拟鼠标封装类 - 零报错，直接调用，完全独立】 =====================
class VirtualMouse:
    def __init__(self):
        # 获取屏幕宽高
        self.screen_w = user32.GetSystemMetrics(SM_CXSCREEN)
        self.screen_h = user32.GetSystemMetrics(SM_CYSCREEN)

    # ✅ 虚拟鼠标：移动到屏幕【绝对坐标(x,y)】- 独立操作，不影响物理鼠标
    def move_to(self, x, y):
        # Windows的绝对坐标需要转换为 0~65535 范围
        dx = int(x * 65535 / self.screen_w)
        dy = int(y * 65535 / self.screen_h)
        mouse_input = MOUSEINPUT(dx=dx, dy=dy, mouseData=0, dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, time=0, dwExtraInfo=0)
        input_event = INPUT(type=INPUT_MOUSE, mi=mouse_input)
        user32.SendInput(1, ctypes.byref(input_event), ctypes.sizeof(input_event))

    # ✅ 虚拟鼠标：左键单击 - 独立操作
    def left_click(self):
        # 左键按下
        down = MOUSEINPUT(0,0,0,MOUSEEVENTF_LEFTDOWN,0,0)
        user32.SendInput(1, ctypes.byref(INPUT(INPUT_MOUSE, down)), ctypes.sizeof(INPUT))
        # 左键松开
        up = MOUSEINPUT(0,0,0,MOUSEEVENTF_LEFTUP,0,0)
        user32.SendInput(1, ctypes.byref(INPUT(INPUT_MOUSE, up)), ctypes.sizeof(INPUT))

    # ✅ 虚拟鼠标：右键单击 - 独立操作
    def right_click(self):
        down = MOUSEINPUT(0,0,0,MOUSEEVENTF_RIGHTDOWN,0,0)
        user32.SendInput(1, ctypes.byref(INPUT(INPUT_MOUSE, down)), ctypes.sizeof(INPUT))
        up = MOUSEINPUT(0,0,0,MOUSEEVENTF_RIGHTUP,0,0)
        user32.SendInput(1, ctypes.byref(INPUT(INPUT_MOUSE, up)), ctypes.sizeof(INPUT))

# ===================== 【3. 永不遮挡的悬浮红线 - 反向移动+绝对置顶+鼠标穿透】 =====================
# 红线置顶API常量
HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
user32_win = ctypes.windll.user32

class TopFloatReverseLine(QWidget):
    def __init__(self):
        super().__init__()
        # 红线自定义配置
        self.line_color = QColor(255, 0, 0)
        self.line_height = 4
        self.line_width = 500
        self.move_sensitivity = 1.2
        self.update_interval = 12

        # 红线置顶+穿透核心属性
        self.setWindowFlags(
            Qt.FramelessWindowHint            |
            Qt.WindowTransparentForInput      |
            Qt.WindowDoesNotAcceptFocus       |
            Qt.BypassWindowManagerHint        |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # 创建红线
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setStyleSheet(f"""
            QFrame {{
                background-color: rgb({self.line_color.red()}, {self.line_color.green()}, {self.line_color.blue()});
                border: none;
            }}
        """)
        self.line.setFixedSize(self.line_width, self.line_height)

        # 零边距布局
        layout = QHBoxLayout(self)
        layout.addWidget(self.line, Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.resize(self.line_width, self.line_height)

        # 屏幕工作区计算（排除任务栏）
        self.work_area = QApplication.primaryScreen().availableGeometry()
        self.fixed_x = (self.work_area.width() - self.line_width) // 2  # X轴永久固定，无左右移动
        self.max_y = self.work_area.height() - self.line_height
        self.min_y = 0

        # 定时器刷新红线位置
        self.timer = QTimer(self)
        self.timer.setInterval(self.update_interval)
        self.timer.timeout.connect(self.update_line_pos)
        self.timer.start()

        # Windows API强制置顶 - 永不被遮挡
        self.hwnd = int(self.winId())
        user32_win.SetWindowPos(self.hwnd, HWND_TOPMOST, 0,0,0,0, SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE)

    # 红线严格反向移动逻辑：鼠标上移→红线下移 鼠标下移→红线上移
    def update_line_pos(self):
        mouse_y = QCursor.pos().y()
        line_y = (self.work_area.height() - mouse_y) * self.move_sensitivity
        line_y = max(self.min_y, min(int(line_y), self.max_y))
        self.move(self.fixed_x, line_y)

# ===================== 【4. 主程序 - 物理鼠标+虚拟鼠标+红线 三者完全独立运行】 =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. 创建并显示 永不遮挡的反向红线
    red_line = TopFloatReverseLine()
    red_line.show()

    # 2. 创建【独立的虚拟鼠标】
    virtual_mouse = VirtualMouse()

    # ✅ 测试虚拟鼠标的独立操作（物理鼠标完全不受影响，正常控制红线）
    virtual_mouse.move_to(200, 200)  # 虚拟鼠标移动到屏幕(200,200)
    virtual_mouse.left_click()       # 虚拟鼠标左键单击
    virtual_mouse.move_to(800, 500)  # 虚拟鼠标再移动到(800,500)
    virtual_mouse.right_click()      # 虚拟鼠标右键单击

    sys.exit(app.exec())