import os
import win32com.client

def get_dirs(path=None):
    """
    获取指定路径下的所有文件夹和指向文件夹的快捷方式（Windows）。
    
    参数:
        path: 要扫描的目录路径，默认 None 表示用户桌面

    返回:
        列表，每个元素是字典：
        {
            "name": 文件夹名或快捷方式名（去掉 .lnk）,
            "path": 对应的实际路径
        }
    """
    if path is None:
        path = os.path.join(os.path.expanduser("~"), "桌面")
    os.makedirs(path, exist_ok=True)

    dirs = []

    # 如果 win32com 不可用，则只能扫描普通文件夹
    if win32com:
        shell = win32com.client.Dispatch("WScript.Shell")
    else:
        shell = None

    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        # 普通文件夹
        if os.path.isdir(full_path):
            dirs.append({"name": item, "path": full_path})

        # 快捷方式
        elif shell and item.lower().endswith(".lnk"):
            try:
                shortcut = shell.CreateShortcut(full_path)
                target = shortcut.Targetpath
                if os.path.isdir(target):
                    name_without_ext = os.path.splitext(item)[0]
                    dirs.append({"name": name_without_ext, "path": target})
            except Exception:
                continue

    return dirs

# 直接运行库文件时打印结果
if __name__ == "__main__":
    result = get_dirs()
    for entry in result:
        print(f"名称: {entry['name']}, 路径: {entry['path']}")
    
    print(50 * "=")
    print("C盘根目录下的文件夹：")
    result = get_dirs(r"C:\\")
    for entry in result:
        print(f"名称: {entry['name']}, 路径: {entry['path']}")

