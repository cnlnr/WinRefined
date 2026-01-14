# -*- coding: utf-8 -*-
import ctypes
import ctypes.wintypes as wintypes
from enum import IntEnum
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer

# ===================== 全局DPI高分屏适配初始化 =====================
# 功能：开启Windows系统的DPI感知，解决高分屏下Qt窗口尺寸/坐标错位、模糊问题
# 执行时机：必须在创建QApplication实例前调用，否则DPI适配失效
# 适配优先级(从高到低)：Win10 1703+最优方案 → Win8.1兼容方案 → Win7兜底方案
def _enable_dpi_awareness():
    try:
        # Win10 1703及以上版本推荐方案，值-4 = DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        # 效果：每个显示器独立DPI缩放，最精准的高分屏适配，无模糊无错位
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except AttributeError:
        # 兼容Win8.1系统，2 = PROCESS_PER_MONITOR_DPI_AWARE 每显示器DPI感知
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            # Win7及更早系统兜底方案，仅全局DPI感知，适配效果一般
            ctypes.windll.user32.SetProcessDPIAware()

# 立即执行DPI适配配置
_enable_dpi_awareness()

# ===================== Windows API 常量与枚举定义 =====================
# SHAppBarMessage 函数的消息指令枚举，控制AppBar的核心行为
class ABMsg(IntEnum):
    NEW = 0       # 注册窗口为系统AppBar，注册后系统会为窗口预留显示区域
    REMOVE = 1    # 注销AppBar注册，释放系统预留的区域，恢复窗口普通属性
    QUERY_POS = 2 # 查询系统推荐的AppBar位置，避免与系统任务栏等控件重叠
    SET_POS = 3   # 向系统提交并设置AppBar的最终显示位置和尺寸

# AppBar 停靠屏幕边缘的枚举，指定窗口吸附的位置
class ABEdge(IntEnum):
    LEFT = 0      # 停靠屏幕左侧
    TOP = 1       # 停靠屏幕顶部
    RIGHT = 2     # 停靠屏幕右侧
    BOTTOM = 3    # 停靠屏幕底部

# Windows系统消息基础值：自定义消息ID必须大于该值，防止与系统内置消息冲突
WM_USER = 0x0400
# 自定义AppBar回调消息ID，系统会通过该消息通知窗口：位置变更、分辨率变化等事件
APPBAR_CALLBACK = WM_USER + 0x01
# GetDeviceCaps的查询常量：获取屏幕水平方向的DPI像素密度值
LOGPIXELSX = 88

# ===================== Windows API 核心结构体定义 =====================
# APPBARDATA 是 Shell32.dll 中 SHAppBarMessage 函数的专用参数结构体
# 作用：传递AppBar的窗口句柄、停靠边缘、显示区域、回调消息等核心数据
# 注意：结构体的cbSize字段必须赋值，否则Windows API调用必定失败
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),       # 必填：结构体的字节大小，固定写法 ctypes.sizeof(APPBARDATA)
        ('hWnd', wintypes.HWND),          # 必填：要注册为AppBar的窗口句柄
        ('uCallbackMessage', wintypes.UINT), # 注册时填：自定义回调消息ID，接收系统通知
        ('uEdge', wintypes.UINT),         # 布局时填：窗口停靠的边缘，对应ABEdge枚举值
        ('rc', wintypes.RECT),            # 核心：窗口的物理像素矩形区域 (left,top,right,bottom)
        ('lParam', wintypes.LPARAM),      # 附加参数：根据不同消息指令传递对应数据
    ]

# ===================== 加载Windows系统DLL并绑定函数签名 =====================
# ctypes调用Windows原生API，必须严格定义【参数类型argtypes】和【返回值类型restype】
# 不定义签名会导致内存错误、调用失败、返回值异常等问题，这是ctypes的硬性要求
_shell32 = ctypes.WinDLL('shell32')    # 提供SHAppBarMessage核心AppBar功能
_user32 = ctypes.WinDLL('user32')      # 提供窗口句柄、设备上下文、屏幕信息相关API
_gdi32 = ctypes.WinDLL('gdi32')        # 提供设备DPI像素密度查询功能

# 绑定 SHAppBarMessage 函数签名：核心AppBar注册/布局函数
_shell32.SHAppBarMessage.argtypes = [wintypes.DWORD, ctypes.POINTER(APPBARDATA)]
_shell32.SHAppBarMessage.restype = wintypes.UINT

# 绑定 user32 相关函数签名：窗口句柄与设备上下文操作
_user32.GetDC.argtypes = [wintypes.HWND]
_user32.GetDC.restype = wintypes.HDC
_user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
_user32.ReleaseDC.restype = wintypes.INT
_user32.GetDesktopWindow.argtypes = []
_user32.GetDesktopWindow.restype = wintypes.HWND

# 绑定 gdi32 相关函数签名：DPI像素密度查询
_gdi32.GetDeviceCaps.argtypes = [wintypes.HDC, wintypes.INT]
_gdi32.GetDeviceCaps.restype = wintypes.INT

# ===================== 核心业务类：系统边缘停靠的AppBar窗口 =====================
class DebugAppBarLeft(QWidget):
    # 窗口的【逻辑像素】尺寸 - Qt默认使用逻辑像素，与DPI无关，适配高分屏的核心
    LOGICAL_WIDTH = 80    # 左右停靠时的宽度
    LOGICAL_HEIGHT = 40   # 上下停靠时的高度

    def __init__(self, edge=ABEdge.LEFT):
        super().__init__()
        self._edge = edge          # 窗口停靠的边缘方向
        self._registered = False   # AppBar注册状态：False未注册/True已注册
        self.dpi_scale = 1.0       # DPI缩放比例：物理像素 = 逻辑像素 * 缩放比例

        # 根据停靠边缘设置窗口的固定逻辑尺寸
        if edge in (ABEdge.LEFT, ABEdge.RIGHT):
            self.setFixedWidth(self.LOGICAL_WIDTH)
        else:
            self.setFixedHeight(self.LOGICAL_HEIGHT)

        # 窗口基础配置：标题、样式、窗口属性
        self.setWindowTitle(f"Debug AppBar - {edge.name}")
        self.setStyleSheet("""
            background-color: #2b2b2b; 
            color: white; 
            border: 3px solid red;
        """)
        # Qt窗口标志组合：无边框 + 置顶显示 + 基础窗口属性
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        # 初始化核心参数：获取当前屏幕的DPI缩放比例
        self.dpi_scale = self._get_dpi_scale()
        self.physical_width = self.logical_to_physical(self.LOGICAL_WIDTH)
        
        # 调试打印：基础信息
        print(f"🔍 DPI 缩放比例: {self.dpi_scale * 100:.0f}%")
        print(f"🔍 窗口停靠边缘: {edge.name}")
        
        # 强制生成窗口句柄：Qt的winId()懒加载，提前调用避免后续注册时句柄为0
        self.winId()

    # ===================== 像素单位转换核心方法 =====================
    def logical_to_physical(self, logical_pixels: int) -> int:
        """Qt逻辑像素 转 Windows物理像素 (核心适配方法)
        :param logical_pixels: Qt窗口的逻辑像素值，与DPI无关
        :return: 对应Windows系统的物理像素值，适配不同DPI屏幕
        """
        return int(logical_pixels * self.dpi_scale)

    def physical_to_logical(self, physical_pixels: int) -> int:
        """Windows物理像素 转 Qt逻辑像素 (核心适配方法)
        :param physical_pixels: Windows API返回的物理像素值
        :return: 对应Qt窗口的逻辑像素值，用于设置Qt控件尺寸/坐标
        """
        return int(physical_pixels / self.dpi_scale)

    # ===================== 内部方法：获取当前屏幕的DPI缩放比例 =====================
    def _get_dpi_scale(self):
        """通过Windows原生API获取屏幕真实DPI，计算缩放比例，默认基准96DPI"""
        try:
            hwnd_desktop = _user32.GetDesktopWindow()  # 获取桌面窗口句柄
            hdc = _user32.GetDC(hwnd_desktop)          # 获取桌面设备上下文句柄

            if hdc is None or hdc == 0:
                raise RuntimeError("获取设备上下文句柄 GetDC 失败")

            # 获取屏幕水平方向DPI值，Windows默认基准DPI=96
            dpi_x = _gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            _user32.ReleaseDC(hwnd_desktop, hdc)       # 释放设备上下文，避免内存泄漏

            scale = dpi_x / 96.0
            print(f"📊 WinAPI 获取屏幕DPI: {dpi_x} | DPI缩放比例: {scale:.2f}")
            return scale

        except Exception as e:
            # 异常兜底：DPI获取失败时，默认缩放比例1.0
            print(f"❌ DPI 检测失败: {e}，已回退到默认缩放比例 1.0")
            return 1.0

    # ===================== 重写Qt原生事件：处理Windows系统消息 =====================
    def nativeEvent(self, eventType, message):
        """Qt的nativeEvent是处理平台原生事件的入口，此处专用于处理Windows的MSG消息
        :param eventType: 事件类型，windows平台固定为 windows_generic_MSG
        :param message: Windows的MSG消息指针
        :return: (是否处理成功, 处理结果)
        """
        # 过滤非Windows平台的事件，交给父类处理
        if eventType != "windows_generic_MSG":
            return super().nativeEvent(eventType, message)

        # 将消息指针解析为Windows标准MSG结构体
        msg = ctypes.wintypes.MSG.from_address(message.__int__())

        # 处理自定义的AppBar回调消息：接收系统的位置变更通知
        if msg.message == APPBAR_CALLBACK:
            print(f"✅ 接收到AppBar回调消息 wParam: {msg.wParam}")
            if msg.wParam == 8:  # wParam=8 代表屏幕分辨率/任务栏位置变更
                print("📍 触发：屏幕位置/分辨率改变 → 更新AppBar窗口位置")
                self.update_appbar_pos()
            # 返回True表示事件已处理，不再向上传递
            return (True, 0)

        # 其他未处理的系统消息，交给父类处理
        return super().nativeEvent(eventType, message)

    # ===================== 核心方法：更新AppBar窗口的位置和尺寸 =====================
    def update_appbar_pos(self):
        """向系统查询并设置AppBar的最终显示位置，核心逻辑：
        1. 先查询系统推荐位置，避免与任务栏重叠
        2. 自定义窗口尺寸和位置
        3. 向系统提交最终位置，系统会为窗口预留区域
        4. 转换物理像素为Qt逻辑像素，设置窗口最终几何坐标
        """
        if not self._registered:
            print("⚠️ AppBar未注册，跳过位置更新")
            return

        # 获取当前窗口的Windows句柄
        hwnd = int(self.winId())
        # 初始化APPBARDATA结构体，必须先设置cbSize
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uEdge = int(self._edge)

        # 获取屏幕可用工作区：排除任务栏等系统控件的区域
        available_rect = QApplication.primaryScreen().availableGeometry()

        # 第一步：向系统发送【查询位置】指令，系统会返回推荐的显示区域
        _shell32.SHAppBarMessage(ABMsg.QUERY_POS, ctypes.byref(abd))

        # 第二步：根据停靠边缘，自定义窗口的物理像素矩形区域
        if self._edge == ABEdge.LEFT:
            abd.rc.left = 0
            abd.rc.right = self.physical_width
            abd.rc.top = available_rect.top()
            abd.rc.bottom = available_rect.bottom()
        elif self._edge == ABEdge.TOP:
            abd.rc.left = available_rect.left()
            abd.rc.right = available_rect.right()
            abd.rc.top = 0
            abd.rc.bottom = self.logical_to_physical(self.LOGICAL_HEIGHT)

        # 调试打印：请求的物理像素区域
        print(f"📐 向系统申请物理区域: {abd.rc.left},{abd.rc.top}-{abd.rc.right},{abd.rc.bottom}")

        # 第三步：向系统发送【设置位置】指令，提交最终窗口区域
        _shell32.SHAppBarMessage(ABMsg.SET_POS, ctypes.byref(abd))

        # 第四步：物理像素 → Qt逻辑像素，设置窗口最终显示位置和尺寸
        if self._edge == ABEdge.LEFT:
            self.setGeometry(
                abd.rc.left,
                abd.rc.top,
                self.physical_to_logical(abd.rc.right - abd.rc.left),
                abd.rc.bottom - abd.rc.top
            )
        else:
            self.setGeometry(
                abd.rc.left,
                abd.rc.top,
                abd.rc.right - abd.rc.left,
                self.physical_to_logical(abd.rc.bottom - abd.rc.top)
            )

        # 调试打印：Qt窗口最终的逻辑像素几何信息
        print(f"✅ 窗口最终显示区域: {self.geometry()}")

    # ===================== 核心方法：注册当前窗口为系统AppBar =====================
    def register_appbar(self):
        """向Windows系统注册AppBar，注册成功后：
        1. 系统会为窗口预留显示区域，不会被其他窗口覆盖
        2. 窗口会收到系统的位置变更回调通知
        3. 窗口具备系统级的边缘停靠属性
        :return: 注册成功返回True，失败返回False
        """
        hwnd = int(self.winId())
        # 调试打印：注册前的基础信息
        print(f"\n{'='*60}")
        print(f"🔍 窗口句柄: {hwnd} | 窗口可见性: {self.isVisible()} | DPI缩放: {self.dpi_scale * 100:.0f}%")
        print(f"🔍 停靠边缘: {self._edge.name}")
        print(f"{'='*60}")

        # 窗口句柄为0时，注册必定失败，直接返回
        if hwnd == 0:
            print("❌ 注册失败：窗口句柄为0，Qt窗口未完成初始化")
            return False

        # 初始化APPBARDATA结构体，配置注册参数
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        abd.uCallbackMessage = APPBAR_CALLBACK  # 设置自定义回调消息ID

        # 发送【注册AppBar】指令到系统
        print(f"📤 执行系统指令：ABM_NEW 注册AppBar...")
        result = _shell32.SHAppBarMessage(ABMsg.NEW, ctypes.byref(abd))
        print(f"📥 系统返回注册结果: {result}")

        # 注册成功/失败的处理逻辑
        if result:
            self._registered = True
            print("✅ AppBar 注册成功！")
            self.update_appbar_pos()  # 注册成功后立即更新窗口位置
            return True
        else:
            self._registered = False
            print("❌ AppBar 注册失败！")
            print(f"❌ Windows错误码: {ctypes.get_last_error()}")  # 打印错误码，便于排查问题
            return False

    # ===================== 核心方法：注销当前窗口的AppBar注册 =====================
    def unregister_appbar(self):
        """注销AppBar注册，恢复窗口为普通Qt窗口：
        1. 释放系统为窗口预留的显示区域
        2. 停止接收系统的AppBar回调通知
        3. 必须在窗口关闭时调用，否则会造成系统资源泄漏
        """
        if not self._registered:
            print("⚠️ AppBar未注册，无需注销")
            return

        hwnd = int(self.winId())
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd

        # 发送【注销AppBar】指令到系统
        print(f"📤 执行系统指令：ABM_REMOVE 注销AppBar...")
        _shell32.SHAppBarMessage(ABMsg.REMOVE, ctypes.byref(abd))

        self._registered = False
        print("✅ AppBar 已成功注销！")

    # ===================== 重写Qt窗口生命周期事件 =====================
    def showEvent(self, event):
        """窗口显示事件：窗口第一次显示时触发"""
        super().showEvent(event)
        print("\n🖼️ 触发窗口显示事件 showEvent")
        # 使用QTimer延迟500ms执行注册：Qt窗口显示后，句柄才完全就绪
        # 立即注册会导致句柄为0，注册失败，这是Qt+WinAPI的经典坑点
        QTimer.singleShot(500, self.register_appbar)

    def closeEvent(self, event):
        """窗口关闭事件：窗口关闭时触发，必须在此处注销AppBar"""
        print("\n🚪 触发窗口关闭事件 closeEvent")
        self.unregister_appbar()  # 注销AppBar，释放系统资源
        super().closeEvent(event)

# ===================== 程序入口 =====================
if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("AppBar 系统边缘停靠窗口 - 顶部停靠示例")
    print("=" * 70)
    
    # 创建Qt应用实例
    app = QApplication(sys.argv)
    
    # 创建AppBar窗口实例，指定停靠顶部
    window = DebugAppBarLeft(edge=ABEdge.TOP)
    
    # 测试：逻辑像素 ↔ 物理像素 转换方法
    print(f"📊 测试转换：逻辑高度 40px → 物理高度: {window.logical_to_physical(40)}px")
    print(f"📊 测试转换：物理高度 80px → 逻辑高度: {window.physical_to_logical(80)}px")
    
    # 显示窗口
    window.show()
    
    # 运行Qt应用主循环
    sys.exit(app.exec())