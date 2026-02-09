import sys
from functools import partial

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout,
    QPushButton, QFrame, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor

from switch_desktop import switch_desktop_path

class DesktopWidget(QWidget):
    def __init__(self, entries):
        super().__init__()

        # 不进任务栏 / 不进 Win+Tab
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.entries = entries
        self.buttons = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 背景
        self.background = QWidget()
        self.background.setStyleSheet("""
            background-color: rgba(50, 50, 50, 220);
            border-radius: 15px;
        """)
        main_layout.addWidget(self.background)

        layout = QHBoxLayout(self.background)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 左侧拖动条
        self.drag_frame = QFrame()
        self.drag_frame.setFixedWidth(25)
        self.drag_frame.setStyleSheet("""
            background-color: rgba(80, 80, 80, 200);
            border-radius: 10px;
        """)
        self.drag_frame.setCursor(QCursor(Qt.SizeAllCursor))
        layout.addWidget(self.drag_frame)

        button_height = 35

        # 添加按钮
        for entry in entries:
            btn = QPushButton(entry["name"])
            btn.setFixedHeight(button_height)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(80, 80, 80, 220);
                    color: white;
                    border-radius: 10px;
                    border: none;
                    font-size: 14px;
                    padding-left: 10px;
                    padding-right: 10px;
                }
                QPushButton:hover {
                    background-color: rgba(100, 100, 100, 220);
                }
                QPushButton:checked {
                    background-color: rgba(60, 160, 90, 230);
                }
            """)
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
            # 切换失败，恢复状态
            btn.setChecked(False)
            return

        # 切换成功，保持当前按钮选中，其他按钮取消
        for b in self.buttons:
            b.setChecked(b is btn)

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

            # 限制在屏幕内
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

    app = QApplication(sys.argv)

    entries = get_dirs()

    # 桌面没有任何可用目录 → 弹窗提示 + 退出
    if not entries:
        QMessageBox.information(
            None,
            "提示",
            "请在 用户\\桌面 目录创建你要分类的文件夹，也可以是快捷方式"
        )
        sys.exit(0)

    widget = DesktopWidget(entries)

    # 获取当前桌面对应按钮索引
    index = find_index_matching_current_dir(entries)
    if index is not None and 0 <= index < len(widget.buttons):
        # 初始高亮
        widget.buttons[index].setChecked(True)
    # 否则不高亮，但组件仍显示

    widget.show()

    hwnd = int(widget.winId())
    if attach_window_to_desktop_only(hwnd):
        print("已挂到桌面 ✅")
        import ctypes
        user32 = ctypes.windll.user32
        # 仅保留必需的常量和核心操作
        ex_style = user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE = -20 直接写值，少定义变量
        ex_style &= ~0x00080000  # WS_EX_LAYERED = 0x00080000 直接写值，移除该样式
        user32.SetWindowLongW(hwnd, -20, ex_style)
    else:
        print("挂到桌面失败 ❌")

    sys.exit(app.exec())
