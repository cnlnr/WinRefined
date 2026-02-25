import comtypes.client
import win32gui
import win32process
import win32api
import psutil

def get_taskbar_app_process():
    uia = comtypes.client.CreateObject("UIAutomationClient.CUIAutomation")
    x, y = win32api.GetCursorPos()

    element = uia.ElementFromPoint((x, y))
    if not element:
        return None

    name = element.CurrentName
    if not name:
        return None

    # 枚举所有顶级窗口，匹配标题
    result = []
    def enum(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if name in title:
            result.append(hwnd)
    win32gui.EnumWindows(enum, None)

    return result

print(get_taskbar_app_process())