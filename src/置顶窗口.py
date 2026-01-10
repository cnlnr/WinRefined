import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen

class TopmostWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowMinMaxButtonsHint |
            Qt.WindowCloseButtonHint
        )
        
        # 设置背景色为半透明
        self.setStyleSheet("background-color: rgba(255, 0, 0, 128);")
        
        # 设置空图标，隐藏标题栏图标
        from PySide6.QtGui import QIcon
        self.setWindowIcon(QIcon())
        
        # 设置空标题文本
        self.setWindowTitle("")
        
        # 获取屏幕信息
        screen = QApplication.primaryScreen()
        # 使用整个屏幕几何信息，包括任务栏
        screen_geometry = screen.geometry()
        
        # 计算窗口尺寸：宽度为屏幕宽度的1/10，高度充满整个屏幕
        width = screen_geometry.width() // 10
        height = screen_geometry.height()
        
        # 设置窗口位置：贴合屏幕最左侧边缘，上下无空白
        x = screen_geometry.left()
        y = screen_geometry.top()
        
        # 设置窗口尺寸和位置
        self.setFixedSize(width, height)
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TopmostWindow()
    window.show()
    sys.exit(app.exec())