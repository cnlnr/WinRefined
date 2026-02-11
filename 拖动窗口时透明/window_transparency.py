import ctypes
import time

# Windows API 常量
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002

# 加载 user32.dll
user32 = ctypes.windll.user32


class WindowTransparency:
    """
    窗口透明度控制器
    
    Args:
        hwnd: 窗口句柄
        alpha: 默认透明度 0-255，默认200
        interval: 动画间隔（秒），0为无动画直接设置，默认0
    """
    
    def __init__(self, hwnd: int, alpha: int = 200, interval: float = 0.002):
        self.hwnd = hwnd
        self.alpha = alpha          # 默认透明度
        self.interval = interval    # 动画间隔（秒）
        self._current_alpha = 255   # 当前透明度
        self._original_alpha = 255  # 记录原始透明度
        
        self._ensure_layered()
    
    def _ensure_layered(self) -> None:
        """确保窗口有 WS_EX_LAYERED 样式"""
        ex_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        if not (ex_style & WS_EX_LAYERED):
            user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
    
    def _animate(self, start: int, end: int, interval: float = None) -> None:
        """内部动画方法"""
        iv = interval if interval is not None else self.interval
        
        # 无动画，直接设置
        if iv <= 0:
            user32.SetLayeredWindowAttributes(self.hwnd, 0, end, LWA_ALPHA)
            self._current_alpha = end
            return
        
        # 计算步数：每步变化至少1，确保平滑
        diff = abs(end - start)
        steps = max(diff, 1)  # 至少1步
        
        for i in range(1, steps + 1):
            progress = i / steps
            current = int(start + (end - start) * progress)
            user32.SetLayeredWindowAttributes(self.hwnd, 0, current, LWA_ALPHA)
            time.sleep(iv)
        
        self._current_alpha = end
    
    def fade_to(self, target_alpha: int = None, interval: float = None) -> None:
        """
        渐变到指定透明度
        
        Args:
            target_alpha: 目标透明度，默认使用初始化时的alpha
            interval: 动画间隔，默认使用初始化时的interval（0为无动画）
        """
        target = target_alpha if target_alpha is not None else self.alpha
        
        # 首次设置透明度时记录原始值
        if self._original_alpha == 255 and self._current_alpha == 255:
            self._original_alpha = 255
        
        self._animate(self._current_alpha, target, interval)
    
    def fade_in(self, interval: float = None) -> None:
        """淡入（透明->不透明）"""
        self._animate(self._current_alpha, 255, interval)
    
    def fade_out(self, interval: float = None) -> None:
        """淡出（不透明->透明）"""
        self._animate(self._current_alpha, 0, interval)
    
    def fade_reset(self, interval: float = None) -> None:
        """渐变回默认透明度"""
        self._animate(self._current_alpha, self.alpha, interval)
    
    def fade_restore(self, interval: float = None) -> None:
        """渐变恢复原始透明度"""
        self._animate(self._current_alpha, self._original_alpha, interval)
    
    def set_transparent(self, alpha: int = None) -> None:
        """直接设置透明度（无动画，无视interval）"""
        target = alpha if alpha is not None else self.alpha
        user32.SetLayeredWindowAttributes(self.hwnd, 0, target, LWA_ALPHA)
        self._current_alpha = target

if __name__ == "__main__":
    import win32gui

    # 示例：对记事本窗口进行透明度控制
    hwnd = win32gui.FindWindow("Notepad", "无标题 - Notepad")
    if not hwnd:
        print("未找到记事本窗口，请先打开记事本。")
    else:
        controller = WindowTransparency(hwnd, alpha=150, interval=0.002)
        
        print("淡入到默认透明度...")
        controller.fade_to()
        time.sleep(1)
        
        print("淡入到不透明...")
        controller.fade_in()
        time.sleep(1)
        
        print("恢复到原始透明度...")
        controller.fade_restore()
        time.sleep(1)
        
        print("完成。")