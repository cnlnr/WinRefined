import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction, QIcon, QPixmap, QCursor
from PySide6.QtCore import Qt, QObject, Signal, QTimer
import keyboard

class HotkeyBridge(QObject):
    """✅ 用于跨线程通信的桥接（避免timer警告）"""
    hotkey_pressed = Signal()

class MouseMenuTray:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # ✅ 创建桥接（必须在主线程）
        self.hotkey_bridge = HotkeyBridge()
        self.hotkey_bridge.hotkey_pressed.connect(self._on_hotkey_safe)
        
        # 创建菜单
        self.setup_menu()
        
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("❌ 系统托盘不可用")
            sys.exit(1)
        
        self.tray_icon = QSystemTrayIcon(self.app)
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.blue)
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("右键菜单 - 按 Ctrl+Shift+M")
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        
        # ✅ 注册热键：只触发信号，不直接操作Qt
        keyboard.add_hotkey('ctrl+shift+m', 
                          self._hotkey_cb, 
                          suppress=False)
        
        print("="*60)
        print("✅ 程序已启动（修复线程警告）")
        print("按 Ctrl+Shift+M 或右键托盘图标测试")
        print("="*60)
        
    def _hotkey_cb(self):
        """✅ keyboard回调：只发信号，不操作Qt"""
        self.hotkey_bridge.hotkey_pressed.emit()
        
    def _on_hotkey_safe(self):
        """✅ 在主线程处理热键"""
        # 延迟10ms确保事件循环就绪
        QTimer.singleShot(10, self.show_menu_at_cursor)
        
    def setup_menu(self):
        self.menu = QMenu()
        
        self.menu.addAction("🖥️ 测试功能 1", lambda: self.execute_action("功能1"))
        self.menu.addAction("📋 测试功能 2", lambda: self.execute_action("功能2"))
        self.menu.addSeparator()
        self.menu.addAction("❌ 退出程序", self.exit_app)
        
        self.menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
            }
            QMenu::item {
                padding: 6px 24px 6px 8px;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        
    def show_menu_at_cursor(self):
        cursor_pos = QCursor.pos()
        print(f"\n[显示] Qt菜单 at ({cursor_pos.x()}, {cursor_pos.y()})")
        self.menu.exec(cursor_pos)
        
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Context:
            print(f"\n[托盘] 右键点击")
            self.menu.exec(QCursor.pos())
    
    def execute_action(self, action):
        print(f"\n[执行] {action}")
    
    def exit_app(self):
        print("\n🛑 正在退出...")
        keyboard.unhook_all()
        self.tray_icon.hide()
        self.app.quit()
    
    def run(self):
        sys.exit(self.app.exec())

if __name__ == '__main__':
    tray = MouseMenuTray()
    tray.run()