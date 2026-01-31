import os
import win32com.client


def get_desktop_target_path():
    """
    获取当前系统桌面真实指向的目录
    （支持语言差异 / OneDrive / 重定向）

    返回:
        str: 桌面真实路径
    """
    wsh = win32com.client.Dispatch("WScript.Shell")
    desktop_path = wsh.SpecialFolders("Desktop")

    if not desktop_path:
        raise RuntimeError("无法获取系统桌面路径")

    return desktop_path


def get_dirs(path=None):
    """
    获取指定路径下的所有文件夹和指向文件夹的快捷方式（Windows）。
    """
    if path is None:
        path = os.path.join(os.path.expanduser("~"), "桌面")

    os.makedirs(path, exist_ok=True)

    dirs = []

    shell = win32com.client.Dispatch("WScript.Shell")

    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        # 普通文件夹
        if os.path.isdir(full_path):
            dirs.append({"name": item, "path": full_path})

        # 快捷方式
        elif item.lower().endswith(".lnk"):
            try:
                shortcut = shell.CreateShortcut(full_path)
                target = shortcut.Targetpath
                if os.path.isdir(target):
                    name_without_ext = os.path.splitext(item)[0]
                    dirs.append({"name": name_without_ext, "path": target})
            except Exception:
                continue

    return dirs


def find_index_matching_current_dir(dirs_list):
    """
    使用“桌面真实路径”对比列表中的目录，
    返回第一个匹配的索引
    """
    desktop_path = get_desktop_target_path()
    desktop_path = os.path.abspath(desktop_path)

    for i, entry in enumerate(dirs_list):
        if os.path.abspath(entry["path"]) == desktop_path:
            return i

    return None


# ======================
# 测试
# ======================
if __name__ == "__main__":
    print("桌面真实路径:", get_desktop_target_path())
    print("=" * 50)

    result = get_dirs()
    for entry in result:
        print(f"名称: {entry['name']}, 路径: {entry['path']}")

    print("=" * 50)
    idx = find_index_matching_current_dir(result)
    print("桌面在列表中的索引:", idx)