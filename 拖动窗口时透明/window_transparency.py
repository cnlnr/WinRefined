import ctypes
import time
import threading

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002

user32 = ctypes.windll.user32


import ctypes
import time
import threading

# ===== Windows API 常量 =====
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002

user32 = ctypes.windll.user32


class WindowTransparency:
    """
    窗口透明度控制器

    interval 语义：
        每改变 1 个 alpha 值所等待的时间（秒）
        例如 interval=0.005：
            255 -> 254 -> 253 ... 每步间隔 0.005 秒
    """

    def __init__(self, hwnd: int, alpha: int = 200, interval: float = 0.005):
        # === 被控制窗口句柄 ===
        self.hwnd = hwnd

        # === 默认目标透明度（配置项） ===
        self.alpha = alpha

        # === 每 1 个 alpha 的过渡间隔 ===
        self.interval = interval

        # === 当前透明度（唯一真实状态） ===
        self._current_alpha = 255

        # === 动画线程与中断信号 ===
        self._anim_thread = None
        self._stop_flag = threading.Event()

        # === 初始化窗口样式 ===
        self._ensure_layered()

    def _ensure_layered(self):
        """
        确保窗口具有 WS_EX_LAYERED 样式
        否则透明度 API 不生效
        """
        ex = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        if not (ex & WS_EX_LAYERED):
            user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, ex | WS_EX_LAYERED)

    def _set_alpha(self, alpha: int):
        """
        立即设置窗口透明度（无动画）
        """
        user32.SetLayeredWindowAttributes(
            self.hwnd, 0, int(alpha), LWA_ALPHA
        )
        self._current_alpha = int(alpha)

    def _animate(self, target: int):
        """
        动画执行体（运行在独立线程）

        从当前透明度逐步过渡到 target
        每次变化 1 个 alpha，sleep interval
        """
        start = self._current_alpha
        diff = target - start

        if diff == 0:
            return

        step = 1 if diff > 0 else -1

        for alpha in range(start + step, target + step, step):
            if self._stop_flag.is_set():
                return

            self._set_alpha(alpha)
            time.sleep(self.interval)

        # 保证最终值精确
        self._set_alpha(target)

    def _start_animation(self, target: int):
        """
        动画调度器

        - 中断旧动画
        - 启动新动画
        - 保证只有一个动画在运行
        """
        self._stop_flag.set()

        if self._anim_thread and self._anim_thread.is_alive():
            self._anim_thread.join()

        self._stop_flag.clear()
        self._anim_thread = threading.Thread(
            target=self._animate,
            args=(int(target),),
            daemon=True
        )
        self._anim_thread.start()

    # ===== 对外 API =====

    def fade_to(self, target_alpha: int = None):
        """
        渐变到指定透明度
        未指定时使用默认 alpha
        """
        self._start_animation(
            target_alpha if target_alpha is not None else self.alpha
        )

    def fade_in(self):
        """
        渐变到完全不透明（255）
        """
        self._start_animation(255)

    def fade_out(self):
        """
        渐变到完全透明（0）
        """
        self._start_animation(0)

    def set_transparent(self, alpha: int):
        """
        立即设置透明度（无动画）
        会中断当前动画
        """
        self._stop_flag.set()
        self._set_alpha(alpha)



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