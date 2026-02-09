import switch_desktop
import argparse

def main():
    parser = argparse.ArgumentParser(description="接收一个路径参数并切换桌面")
    parser.add_argument("path", help="输入的路径")
    args = parser.parse_args()

    # 直接打印参数
    print(args.path)

    # 切换桌面
    if switch_desktop.switch_desktop_path(args.path):
        print("✅ 桌面切换完成并刷新")
    else:
        print("❌ 桌面切换失败")

if __name__ == "__main__":
    main()
