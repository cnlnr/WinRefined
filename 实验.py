import ctypes

# 常量
WM_KEYDOWN = 0x0100
WM_KEYUP   = 0x0101
VK_F5      = 0x74

user32 = ctypes.windll.user32

# 找 Progman（桌面顶层窗口）
progman = user32.FindWindowW("Progman", None)

# 找桌面 DefView
defview = user32.FindWindowExW(progman, None, "SHELLDLL_DefView", None)

# Win10/11 有时 DefView 在 WorkerW 下
if not defview:
    worker = None
    while True:
        worker = user32.FindWindowExW(None, worker, "WorkerW", None)
        if not worker:
            break
        defview = user32.FindWindowExW(worker, None, "SHELLDLL_DefView", None)
        if defview:
            break

# 找桌面图标列表窗口
listview = user32.FindWindowExW(defview, None, "SysListView32", None)

if listview:
    # 发送 F5 消息刷新桌面
    user32.PostMessageW(listview, WM_KEYDOWN, VK_F5, 0)
    user32.PostMessageW(listview, WM_KEYUP,   VK_F5, 0)
    print("桌面已刷新 ✅")
else:
    print("找不到桌面图标窗口 ❌")
