import win32com.client

shell = win32com.client.Dispatch("Shell.Application")
# 这个方法在某些Windows版本上可用
shell.WindowSwitcher()