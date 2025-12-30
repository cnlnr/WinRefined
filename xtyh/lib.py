# 导入系统模块
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 删除系统模块，避免它们出现在__all__中
del sys, os

# 导入所需模块
import Lib.mouse as mouse
import Lib.key as key

# 使用切片法，只保留第八个元素以后的内容（索引从0开始）
__all__ = list(globals().keys())[8:]


# 打印导出的模块列表，方便调试
if __name__ == "__main__":
    print(f"自动导出的模块: {__all__}")
