import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction, QIcon, QPixmap, QCursor
from PySide6.QtCore import Qt, QObject, Signal, QTimer
import keyboard

class HotkeyBridge(QObject):
    hotkey_pressed = Signal()

class MouseMenuTray:
    def __init__(self):
        # ✅ 尝试设置样式（如果支持）
        try:
            QApplication.setStyle("windowsvista")
        except:
            pass
        
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # ✅ DPI设置
        self.app.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        self.hotkey_bridge = HotkeyBridge()
        self.hotkey_bridge.hotkey_pressed.connect(self._on_hotkey_safe)
        
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
        
        keyboard.add_hotkey('ctrl+shift+m', self._hotkey_cb, suppress=False)
        
        print("="*60)
        print("✅ Win11样式菜单已加载")
        print("按 Ctrl+Shift+M 或右键托盘图标")
        print("="*60)
        
    def _hotkey_cb(self):
        self.hotkey_bridge.hotkey_pressed.emit()
        
    def _on_hotkey_safe(self):
        QTimer.singleShot(10, self.show_menu_at_cursor)
        
    def setup_menu(self):
        self.menu = QMenu()
        
        # ✅ Win11 Fluent风格CSS（模拟）
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 4px 0px;
                font-family: "Segoe UI", "Microsoft YaHei";
                font-size: 14px;
                /* Mica效果模拟 */
                background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==);
            }
            QMenu::item {
                padding: 8px 24px 8px 12px;
                margin: 0px 4px;
                border-radius: 4px;
                min-width: 200px;
            }
            QMenu::item:selected {
                background-color: #f3f3f3;
                color: #000000;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 8px;
            }
            QMenu::indicator {
                width: 16px;
                height: 16px;
            }
            QMenu::right-arrow {
                image: url(none);
            }
        """)
        
        self.menu.addAction("🖥️ 测试功能 1", lambda: self.execute_action("功能1"))
        self.menu.addAction("📋 测试功能 2", lambda: self.execute_action("功能2"))
        self.menu.addSeparator()
        self.menu.addAction("❌ 退出程序", self.exit_app)
        
    def show_menu_at_cursor(self):
        cursor_pos = QCursor.pos()
        print(f"\n[显示] Win11样式菜单 at ({cursor_pos.x()}, {cursor_pos.y()})")
        self.menu.exec(cursor_pos)
        
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Context:
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