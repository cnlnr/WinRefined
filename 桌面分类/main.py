import sys
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

        # ----------------------------
        # 窗口标志修改：
        # - FramelessWindowHint: 无边框
        # - Tool: 避免任务栏图标
        # - WindowStaysOnTopHint: 保持置顶
        # 属性 WA_ShowWithoutActivating: 不获取焦点，Win+Tab 不显示
        # ----------------------------
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
        # 按钮自适应宽度 + 左右内边距
        # ----------------------------
        for entry in entries:
            btn = QPushButton(entry["name"])
            btn.setFixedHeight(button_height)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # 自动分配宽度
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(80, 80, 80, 220);
                    color: white;
                    border-radius: 10px;
                    border: none;
                    font-size: 14px;
                    padding-left: 10px;   /* 左内边距 */
                    padding-right: 10px;  /* 右内边距 */
                }
                QPushButton:hover {
                    background-color: rgba(100, 100, 100, 220);
                }
            """)
            layout.addWidget(btn)
            btn.clicked.connect(lambda checked, p=entry["path"]: print(p))

        # 窗口初始位置
        self.move(300, 10)

        # 拖动状态
        self._drag_active = False
        self._drag_position = QPoint()

    # ----------------------------
    # 拖动逻辑
    # ----------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().x() <= self.drag_frame.width():
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self._drag_active:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False

# ----------------------------
# 运行程序
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    dir_list = get_dirs()  # 默认扫描桌面，也可以传入路径参数
    widget = DesktopWidget(dir_list)
    widget.show()

    sys.exit(app.exec())
