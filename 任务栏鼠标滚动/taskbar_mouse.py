import ctypes
from ctypes import wintypes
import time
from threading import Thread, Event

user32 = ctypes.windll.user32

# ---------------- 判断鼠标是否在任务栏 ----------------
def get_hwnd_under_mouse():
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return user32.WindowFromPoint(pt)

def get_class_name(hwnd):
    if not hwnd:
        return ""
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value

def is_mouse_over_taskbar():
    """
    判断鼠标是否在任务栏的可见区域
    Returns:
        bool: True 在任务栏, False 不在
    """
    hwnd = get_hwnd_under_mouse()
    while hwnd:
        class_name = get_class_name(hwnd)
        if class_name == "Shell_TrayWnd":
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            if not user32.IsWindowVisible(hwnd):
                return False
            pt = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            return rect.left <= pt.x <= rect.right and rect.top <= pt.y <= rect.bottom
        hwnd = user32.GetParent(hwnd)
    return False

# ---------------- 任务栏监控类 ----------------
class TaskbarMonitor:
    def __init__(self, on_enter, on_exit, interval=0.1):
        """
        初始化任务栏监控
        Args:
            on_enter (callable): 鼠标进入任务栏时调用函数，接收一个 stop_event 参数
            on_exit (callable): 鼠标离开任务栏时调用函数
            interval (float): 检测间隔，单位秒
        """
        self.on_enter = on_enter
        self.on_exit = on_exit
        self.interval = interval
        self._over = False
        self._worker_thread = None
        self._stop_event = Event()
        self._running = False

    def _run_worker(self):
        self.on_enter(self._stop_event)

    def start(self):
        """启动任务栏监控"""
        self._running = True
        self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        try:
            while self._running:
                now_over = is_mouse_over_taskbar()
                if now_over and not self._over:
                    self._over = True
                    self._stop_event.clear()
                    self._worker_thread = Thread(target=self._run_worker, daemon=True)
                    self._worker_thread.start()
                elif not now_over and self._over:
                    self._over = False
                    self._stop_event.set()
                    if self._worker_thread:
                        self._worker_thread.join()
                    self.on_exit()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止任务栏监控"""
        self._running = False
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join()
