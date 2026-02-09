import sys
import ctypes
from functools import partial

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout,
    QPushButton, QFrame, QVBoxLayout, QMessageBox,
    QStyleFactory  # 导入样式工厂
)
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QCursor

from switch_desktop import switch_desktop_path

class DesktopWidget(QWidget):
    def __init__(self, entries):
        super().__init__()

        # 兼容的窗口属性设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WA_PaintOnScreen, False)

        self.entries = entries
        self.buttons = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 背景容器
        self.background = QFrame()
        self.background.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 50, 220);
                border-radius: 15px;
            }
        """)
        main_layout.addWidget(self.background)

        layout = QHBoxLayout(self.background)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 左侧拖动条
        self.drag_frame = QFrame()
        self.drag_frame.setFixedWidth(25)
        self.drag_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(80, 80, 80, 200);
                border-radius: 10px;
            }
        """)
        self.drag_frame.setCursor(QCursor(Qt.SizeAllCursor))
        layout.addWidget(self.drag_frame)

        button_height = 35

        # 添加按钮
        for entry in entries:
            btn = QPushButton(entry["name"])
            btn.setFixedHeight(button_height)
            btn.setCheckable(True)
            # 简化且高优先级的样式表
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgb(80, 80, 80);
                    color: white;
                    border-radius: 10px;
                    border: none;
                    font-size: 14px;
                    padding-left: 10px;
                    padding-right: 10px;
                    opacity: 0.85;
                }
                QPushButton:hover {
                    background-color: rgb(100, 100, 100);
                    opacity: 0.9;
                }
                QPushButton:checked {
                    background-color: rgb(60, 160, 90);
                    opacity: 0.9;
                }
            """)
            # 强制使用Fusion样式，避免系统干扰
            btn.setStyle(QStyleFactory.create("Fusion"))
            btn.setAttribute(Qt.WA_StyledBackground, True)
            layout.addWidget(btn)
            self.buttons.append(btn)
            btn.clicked.connect(partial(self.on_button_clicked, entry["path"], btn))

        # 初始位置
        self.move(300, 10)

        # 拖动状态
        self._drag_active = False
        self._drag_position = QPoint()

    # ---------------- 点击按钮 ----------------
    def on_button_clicked(self, path: str, btn: QPushButton):
        success = switch_desktop_path(path)

        if not success:
            btn.setChecked(False)
            return

        # 安全设置按钮选中状态
        for b in self.buttons:
            b.blockSignals(True)
            b.setChecked(b is btn)
            b.blockSignals(False)
        
        # 延迟刷新确保状态生效
        QTimer.singleShot(5, self.refresh_ui)

    # ---------------- 界面刷新 ----------------
    def refresh_ui(self):
        # 只刷新按钮和背景，避免触发系统API错误
        for btn in self.buttons:
            btn.update()
        self.background.update()
        self.update()

    # ---------------- 拖动 ----------------
    def mousePressEvent(self, event):
        if (
            event.button() == Qt.LeftButton
            and event.position().x() <= self.drag_frame.width()
        ):
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            screen = QApplication.primaryScreen().availableGeometry()
            pos = event.globalPosition().toPoint() - self._drag_position

            x = max(screen.left(), min(pos.x(), screen.right() - self.width()))
            y = max(screen.top(), min(pos.y(), screen.bottom() - self.height()))

            self.move(x, y)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False


# ---------------------------- 程序入口 ----------------------------
if __name__ == "__main__":
    from desktop_dirs import get_dirs, find_index_matching_current_dir
    from desktop_component import attach_window_to_desktop_only

    # 全局设置（仅保留必要属性）
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))  # 强制Fusion样式
    app.setAttribute(Qt.AA_UseSoftwareOpenGL)     # 软件渲染避免硬件冲突

    entries = get_dirs()

    if not entries:
        QMessageBox.information(
            None,
            "提示",
            "请在 用户\\桌面 目录创建你要分类的文件夹，也可以是快捷方式"
        )
        sys.exit(0)

    widget = DesktopWidget(entries)

    # 初始选中对应按钮
    index = find_index_matching_current_dir(entries)
    if index is not None and 0 <= index < len(widget.buttons):
        widget.buttons[index].setChecked(True)
        widget.refresh_ui()

    widget.show()

    # 获取句柄并挂载到桌面
    hwnd = int(widget.winId())
    if attach_window_to_desktop_only(hwnd):
        print("已挂到桌面 ✅")
        # 修复窗口扩展样式，解决UpdateLayeredWindowIndirect错误
        user32 = ctypes.windll.user32
        GWL_EXSTYLE = -20
        WS_EX_TRANSPARENT = 0x00000020
        WS_EX_LAYERED = 0x00080000
        WS_EX_COMPOSITED = 0x02000000
        
        # 移除冲突的分层/透明样式，保留复合渲染
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ex_style = ex_style & ~(WS_EX_LAYERED | WS_EX_TRANSPARENT) | WS_EX_COMPOSITED
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
        
        # 挂载后刷新界面
        widget.refresh_ui()
    else:
        print("挂到桌面失败 ❌")

    sys.exit(app.exec())