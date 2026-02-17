from pywinauto import Desktop

# 1️⃣ UIA Desktop
desktop = Desktop(backend="uia")

# 2️⃣ 任务栏（Win32 外壳）
taskbar = desktop.window(
    class_name="Shell_TrayWnd"
)

# 3️⃣ XAML InputSite Pane
xaml_pane = taskbar.child_window(
    class_name="Windows.UI.Input.InputSite.WindowClass",
    control_type="Pane"
)

# 4️⃣ 托盘输入法按钮
ime_btn = xaml_pane.child_window(
    automation_id="SystemTrayIcon",
    class_name="SystemTray.NormalButton",
    control_type="Button"
)

# 5️⃣ 读取 Name
ime_btn.wait("exists ready", timeout=2)
print(repr(ime_btn.window_text()))
