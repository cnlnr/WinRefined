import ctypes
import os
from ctypes import wintypes
from refresh_desktop import refresh_desktop

# -----------------------------
# GUID 定义，用于桌面路径修改
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]

FOLDERID_Desktop = GUID(
    0xB4BFCC3A,
    0xDB2C,
    0x424C,
    (wintypes.BYTE * 8)(
        0xB0, 0x29, 0x7F, 0xE9,
        0x9A, 0x87, 0xC6, 0x41
    )
)

# -----------------------------
# 修改桌面路径并刷新桌面
def switch_desktop_path(new_path: str) -> bool:
    """
    修改 Windows 桌面路径并刷新桌面
    返回 True 表示成功，False 表示失败
    """
    # 1️⃣ 检查目录是否存在
    if not os.path.isdir(new_path):
        return False

    shell32 = ctypes.windll.shell32

    # 2️⃣ 修改桌面路径
    hr = shell32.SHSetKnownFolderPath(
        ctypes.byref(FOLDERID_Desktop),
        0,
        None,
        ctypes.c_wchar_p(new_path)
    )
    if hr != 0:
        return False

    # 3️⃣ 刷新桌面（快速刷新）
    refresh_desktop()
    return True

# -----------------------------
# 脚本直接运行示例
if __name__ == "__main__":
    new_path = r"C:\Users\lqvsy\Desktop"

    if switch_desktop_path(new_path):
        print("✅ 桌面切换完成并刷新")
    else:
        print("❌ 桌面切换失败（目录不存在或设置失败）")
