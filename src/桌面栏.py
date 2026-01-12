# appbar_top_demo.py
import sys
from PySide6.QtWidgets import QApplication
from appbar import DebugAppBarLeft, ABEdge

def main():
    print("=" * 70)
    print("AppBar 顶部注册示例")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    
    # 创建顶部应用栏
    window = DebugAppBarLeft(edge=ABEdge.TOP)
    
    # 测试坐标转换方法
    print(f"📊 逻辑高度 40px → 物理高度: {window.logical_to_physical(40)}px")
    print(f"📊 物理高度 80px → 逻辑高度: {window.physical_to_logical(80)}px")
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()