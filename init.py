# setup_helper.py
import urllib.request
from pathlib import Path

VIRTUAL_DESKTOP_URL = "https://github.com/MScholtes/VirtualDesktop/releases/download/V1.21/VirtualDesktop11-24H2.exe"
BIN_DIR = Path(__file__).parent / "bin"  # 项目根目录/bin

def download_virtual_desktop():
    """下载 VirtualDesktop11-24H2.exe 到项目根目录的 bin/ 文件夹"""
    print("=" * 70)
    print("开始下载 VirtualDesktop 工具...")
    print(f"目标路径: {BIN_DIR}")
    print("=" * 70)
    
    # 确保 bin 目录存在
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    
    # 从 URL 中提取原始文件名（不更改文件名！）
    from urllib.parse import urlparse
    original_filename = urlparse(VIRTUAL_DESKTOP_URL).path.split('/')[-1]
    
    # 完整文件路径（保持原文件名）
    exe_path = BIN_DIR / original_filename
    
    # 检查是否已存在
    if exe_path.exists():
        print(f"⚠️  {exe_path} 已存在，跳过下载")
        return exe_path
    
    try:
        # 下载文件（文件名保持为 VirtualDesktop11-24H2.exe）
        print(f"📥 正在下载 {original_filename}...")
        urllib.request.urlretrieve(VIRTUAL_DESKTOP_URL, exe_path)
        
        print(f"✅ 下载成功: {exe_path}")
        print(f"文件大小: {exe_path.stat().st_size:,} bytes")
        return exe_path
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        raise

if __name__ == "__main__":
    download_virtual_desktop()
    print("\n下载完成！")