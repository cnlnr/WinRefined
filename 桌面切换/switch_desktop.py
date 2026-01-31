import ctypes
import os
from ctypes import wintypes

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

def switch_desktop_path(new_path: str) -> bool:
    # 1️⃣ 先检测目录是否存在
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

    # 3️⃣ 刷新桌面
    shell32.SHChangeNotify(
        0x8000000,  # SHCNE_ASSOCCHANGED
        0x0000,
        None,
        None
    )

    return True


if __name__ == "__main__":
    new_path = r"C:\Users\lqvsy\Desktop"

    if switch_desktop_path(new_path):
        print("✅ 桌面切换完成，右键新建文件夹可用")
    else:
        print("❌ 桌面切换失败（目录不存在或设置失败）")
