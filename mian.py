import ctypes
from ctypes import wintypes
import time
import win32gui

# ---------------- WinEventHook ----------------
user32 = ctypes.windll.user32

EVENT_SYSTEM_MOVESIZESTART = 0x000A
EVENT_SYSTEM_MOVESIZEEND = 0x000B
WINEVENT_OUTOFCONTEXT = 0x0000

# 回调类型
WinEventProcType = ctypes.WINFUNCTYPE(
    None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
    wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD
)

def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
    # 不再过滤窗口可见性
    title = win32gui.GetWindowText(hwnd)
    if event == EVENT_SYSTEM_MOVESIZESTART:
        print(f"Window started moving: HWND={hwnd}, Title='{title}'")
    elif event == EVENT_SYSTEM_MOVESIZEEND:
        print(f"Window finished moving: HWND={hwnd}, Title='{title}'")

# 转成 C 风格回调
proc = WinEventProcType(callback)

# 注册系统范围的事件钩子
hook = user32.SetWinEventHook(
    EVENT_SYSTEM_MOVESIZESTART,
    EVENT_SYSTEM_MOVESIZEEND,
    0,
    proc,
    0, 0,
    WINEVENT_OUTOFCONTEXT
)

if not hook:
    print("Failed to set WinEventHook.")
    exit()

print("Listening for all window drag events. Press Ctrl+C to stop.")

# 消息循环
try:
    msg = wintypes.MSG()
    while True:
        while user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.01)
except KeyboardInterrupt:
    user32.UnhookWinEvent(hook)
    print("Stopped listening.")
