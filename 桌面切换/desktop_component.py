import ctypes

user32 = ctypes.windll.user32

GWL_STYLE = -16
WS_CHILD = 0x40000000
WS_VISIBLE = 0x10000000

def get_desktop_listview_hwnd():
    """
    获取桌面图标列表窗口的句柄 (SysListView32)
    返回句柄，找不到返回 None
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
    return listview

def attach_window_to_desktop_only(hwnd):
    """
    只将指定窗口挂到桌面图标窗口上，不修改窗口样式
    hwnd: 目标窗口句柄
    返回 True/False
    """
    if not hwnd:
        return False

    # 获取桌面图标窗口句柄
    desktop = get_desktop_listview_hwnd()
    if not desktop:
        return False

    # 只设置父窗口为桌面图标窗口
    user32.SetParent(hwnd, desktop)

    return True


# -------------------------
if __name__ == "__main__":
    import win32gui
    
    # 直接用 Notepad 窗口的 NativeWindowHandle
    hwnd = win32gui.FindWindow("Notepad", "无标题 - Notepad")

    if attach_window_to_desktop_only(hwnd):
        print("Notepad 窗口已挂到桌面 ✅")
    else:
        print("挂载失败 ❌")
