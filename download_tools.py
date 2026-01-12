# setup_helper.py（项目根目录）
import os
import requests
from pathlib import Path

# 下载配置
VIRTUAL_DESKTOP_URL = "https://github.com/MScholtes/VirtualDesktop/releases/download/V1.21/VirtualDesktop11-24H2.exe"
BIN_DIR = Path(__file__).parent / "src/bin"
EXE_NAME = "VirtualDesktop.exe"

def download_virtual_desktop():
    """手动调用：下载 VirtualDesktop.exe 到 bin 目录"""
    print("=" * 70)
    print("开始下载 VirtualDesktop 工具...")
    print(f"目标路径: {BIN_DIR}")
    print(f"下载地址: {VIRTUAL_DESKTOP_URL}")
    print("=" * 70)
    
    # 确保 bin 目录存在
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    
    # 完整文件路径
    exe_path = BIN_DIR / EXE_NAME
    
    # 检查是否已存在
    if exe_path.exists():
        print(f"⚠️ {exe_path} 已存在，跳过下载")
        return exe_path
    
    try:
        # 下载文件
        response = requests.get(VIRTUAL_DESKTOP_URL, stream=True)
        response.raise_for_status()
        
        # 写入文件
        with open(exe_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 下载成功: {exe_path}")
        print(f"文件大小: {exe_path.stat().st_size} bytes")
        return exe_path
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        raise

if __name__ == "__main__":
    # 直接运行脚本
    download_virtual_desktop()
    print("\n下载完成！")