import ctypes
from ctypes import wintypes
import time

# 加载 user32.dll
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# ==================== 定义所有 Windows 结构体和常量 ====================

# 窗口类结构
class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HCURSOR),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]

# 工具提示信息结构
class TOOLINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("hwnd", wintypes.HWND),
        ("uId", wintypes.UINT),
        ("rect", wintypes.RECT),
        ("hinst", wintypes.HINSTANCE),
        ("lpszText", wintypes.LPWSTR),
        ("lParam", wintypes.LPARAM),
    ]

# 常量定义
WS_VISIBLE = 0x10000000
WS_CHILD = 0x40000000
WS_OVERLAPPEDWINDOW = 0xCF0000
WS_POPUP = 0x80000000
TTS_ALWAYSTIP = 0x01
TTF_SUBCLASS = 0x0010
TTF_IDISHWND = 0x0001
TTM_ADDTOOL = 0x432
TTM_SETDELAYTIME = 0x417
TTDT_AUTOPOP = 2
WM_DESTROY = 2
COLOR_WINDOW = 5

# ==================== 窗口过程函数 ====================

def WndProc(hwnd, msg, wparam, lparam):
    """窗口消息处理函数"""
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

# 创建函数指针类型
WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM)
wnd_proc = WNDPROC(WndProc)

# ==================== 主函数 ====================

def create_button_tooltip():
    """创建带工具提示的按钮窗口"""
    
    print("="*60)
    print("Windows 系统原生工具提示 - 按钮悬停测试")
    print("="*60)
    
    # 1. 注册窗口类
    print("1. 注册窗口类...")
    class_name = "TooltipTestWindow"
    wnd_class = WNDCLASS()
    wnd_class.style = 0
    wnd_class.lpfnWndProc = ctypes.cast(wnd_proc, ctypes.c_void_p)
    wnd_class.cbClsExtra = 0
    wnd_class.cbWndExtra = 0
    wnd_class.hInstance = kernel32.GetModuleHandleW(None)
    wnd_class.hIcon = None
    wnd_class.hCursor = user32.LoadCursorW(None, 32512)  # IDC_ARROW
    wnd_class.hbrBackground = ctypes.c_void_p(COLOR_WINDOW + 1)
    wnd_class.lpszMenuName = None
    wnd_class.lpszClassName = class_name
    
    if not user32.RegisterClassW(ctypes.byref(wnd_class)):
        print(f"❌ 注册窗口类失败，错误代码: {kernel32.GetLastError()}")
        return False
    
    print("✅ 窗口类注册成功")
    
    # 2. 创建主窗口
    print("2. 创建主窗口...")
    hwnd = user32.CreateWindowExW(
        0,  # 扩展样式
        class_name,
        "系统工具提示测试",
        WS_VISIBLE | WS_OVERLAPPEDWINDOW,
        100, 100, 500, 400,
        None, None, kernel32.GetModuleHandleW(None), None
    )
    
    if not hwnd:
        print(f"❌ 创建窗口失败，错误代码: {kernel32.GetLastError()}")
        return False
    
    print(f"✅ 主窗口创建成功，句柄: {hwnd}")
    
    # 3. 创建按钮
    print("3. 创建按钮...")
    button = user32.CreateWindowExW(
        0,
        "BUTTON",
        "👉 鼠标悬停查看提示",
        WS_VISIBLE | WS_CHILD,
        100, 150, 300, 50,
        hwnd,
        1001,  # 控件ID
        kernel32.GetModuleHandleW(None), None
    )
    
    if not button:
        print(f"❌ 创建按钮失败")
        return False
    
    print(f"✅ 按钮创建成功，句柄: {button}")
    
    # 4. 创建工具提示控件
    print("4. 创建工具提示控件...")
    tooltip = user32.CreateWindowExW(
        8,  # WS_EX_TOPMOST
        "tooltips_class32",
        None,
        WS_POPUP | TTS_ALWAYSTIP,
        0, 0, 0, 0,
        hwnd, None, kernel32.GetModuleHandleW(None), None
    )
    
    if not tooltip:
        print(f"❌ 创建工具提示失败")
        return False
    
    print(f"✅ 工具提示创建成功，句柄: {tooltip}")
    
    # 5. 配置工具提示
    print("5. 配置工具提示信息...")
    ti = TOOLINFO()
    ti.cbSize = ctypes.sizeof(TOOLINFO)
    ti.uFlags = TTF_SUBCLASS | TTF_IDISHWND
    ti.hwnd = hwnd
    ti.uId = button  # 关键：使用按钮句柄作为ID
    ti.lpszText = "🎉 系统原生提示工作正常！\n支持多行文本\n这是第三行"
    
    result = user32.SendMessageW(tooltip, TTM_ADDTOOL, 0, ctypes.byref(ti))
    if not result:
        print(f"⚠️ 添加工具警告: 返回 {result}")
    else:
        print("✅ 工具添加成功")
    
    # 6. 设置显示时长
    user32.SendMessageW(tooltip, TTM_SETDELAYTIME, TTDT_AUTOPOP, 5000)
    print("✅ 提示时长设置成功")
    
    print("\n" + "="*60)
    print("🎯 窗口创建完成！")
    print("请将鼠标移动到按钮上（大按钮，写着'鼠标悬停查看提示'）")
    print("如果正常，应该立即看到黄色提示框弹出")
    print("="*60 + "\n")
    
    # 7. 消息循环
    print("进入消息循环...")
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
    
    return True

if __name__ == "__main__":
    try:
        success = create_button_tooltip()
        if success:
            print("\n✅ 程序正常退出")
        else:
            print("\n❌ 程序执行失败")
    except Exception as e:
        print(f"\n❌ 严重错误: {e}")
        import traceback
        traceback.print_exc()
    
    time.sleep(1)
    input("按回车键退出...")