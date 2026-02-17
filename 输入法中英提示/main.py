import sys
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QCursor

app = QApplication(sys.argv)

# 创建窗口（气泡）
tip = QWidget()
tip.setWindowFlags(
    Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
)
tip.setAttribute(Qt.WA_TransparentForMouseEvents)
tip.setAttribute(Qt.WA_TranslucentBackground)  # 窗口透明

# 在窗口里放 QLabel
label = QLabel("中", tip)
label.setStyleSheet("""
    background-color: rgba(0, 0, 0, 180);
    color: white;
    padding: 8px 12px;
    border-radius: 10px;
    font-size: 12pt;
""")
label.adjustSize()  # 自动适应文本大小

tip.resize(label.size())  # 窗口大小和 label 一致
tip.show()

# 鼠标跟随
timer = QTimer()
timer.timeout.connect(lambda: tip.move(QCursor.pos() + QPoint(16, 16)))
timer.start(16)

sys.exit(app.exec())
