import sys
from functools import partial
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QFrame, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor
from desktop_dirs import get_dirs  # 导入库

# ----------------------------
# PySide6 桌面组件
# ----------------------------
class DesktopWidget(QWidget):
    def __init__(self, entries):
        super().__init__()

        # 无边框 + 永远置顶 + 不显示任务栏 + Win+Tab 不显示
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # 内部圆角背景
        self.background = QWidget()
        self.background.setStyleSheet("""
            background-color: rgba(50, 50, 50, 220);
            border-radius: 15px;
        """)
        main_layout.addWidget(self.background)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.background.setLayout(layout)

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
        self.resize(450, button_height + 10)

        # ----------------------------
        # 按钮自适应宽度 + 左右内边距 + 点击高亮保留
        # ----------------------------
        self.buttons = []

        for entry in entries:
            btn = QPushButton(entry["name"])
            btn.setFixedHeight(button_height)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # 自动分配宽度
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
                    background-color: rgba(0, 200, 100, 220); /* 点击后绿色高亮 */
                }
            """)
            layout.addWidget(btn)
            self.buttons.append(btn)

            # 使用 partial 绑定当前路径和按钮，避免闭包问题
            def on_click(p, b):
                # 取消其他按钮选中
                for other in self.buttons:
                    if other != b:
                        other.setChecked(False)
                # 当前按钮选中
                b.setChecked(True)
                # 打印路径
                print(p)

            btn.clicked.connect(partial(on_click, entry["path"], btn))

        # 窗口初始位置
        self.move(300, 10)

        # 拖动状态
        self._drag_active = False
        self._drag_position = QPoint()

    # ----------------------------
    # 拖动逻辑 + 屏幕边界限制
    # ----------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().x() <= self.drag_frame.width():
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self._drag_active:
            new_pos = event.globalPosition().toPoint() - self._drag_position

            screen = QApplication.primaryScreen()
            if screen:
                geom = screen.availableGeometry()
                x = max(geom.left(), new_pos.x())
                y = max(geom.top(), new_pos.y())
                x = min(x, geom.right() - self.width())
                y = min(y, geom.bottom() - self.height())
                new_pos = QPoint(x, y)

            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False

# ----------------------------
# 运行程序
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    dir_list = get_dirs()  # 获取桌面文件夹列表
    widget = DesktopWidget(dir_list)
    widget.show()

    sys.exit(app.exec())
