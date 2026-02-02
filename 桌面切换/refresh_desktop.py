import ctypes

WM_KEYDOWN = 0x0100
WM_KEYUP   = 0x0101
VK_F5      = 0x74

user32 = ctypes.windll.user32

def refresh_desktop():
    """
    刷新 Windows 桌面（模拟 F5）。
    返回 True 表示刷新成功，False 表示未找到桌面窗口。
    """
    defview = None
    worker = None
    while True:
        worker = user32.FindWindowExW(None, worker, "WorkerW", None)
        if not worker:
            break
        defview = user32.FindWindowExW(worker, None, "SHELLDLL_DefView", None)
        if defview:
            break

    listview = user32.FindWindowExW(defview, None, "SysListView32", None) if defview else None

    if listview:
        user32.PostMessageW(listview, WM_KEYDOWN, VK_F5, 0)
        user32.PostMessageW(listview, WM_KEYUP,   VK_F5, 0)
        return True
    else:
        return False

# ---------------------------------
if __name__ == "__main__":
    if refresh_desktop():
        print("桌面已刷新 ✅")
    else:
        print("找不到桌面图标窗口 ❌")
