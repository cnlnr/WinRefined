import sys
import subprocess
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QEvent
from appbar import DebugAppBarLeft, ABEdge

# 纯函数结构 不变 + 完美宽度自适应UI（核心优化版）
def create_appbar_button_list(edge=ABEdge.LEFT, button_texts=None):
    # 处理默认按钮文本
    if button_texts is None:
        button_texts = ["桌面1", "桌面2", "桌面3"]
    
    # 创建根控件
    app_bar = DebugAppBarLeft(edge=edge)

    # ========== 新增：桌面切换核心函数 - 仅新增，无修改其他内容 ==========
    def switch_desktop(desktop_num):
        """调用指定工具切换桌面，禁用动画，桌面编号对应 /Switch:数字"""
        # 工具绝对路径：上级目录的bin文件夹下的VirtualDesktop11-24H2.exe
        tool_path = str(Path(__file__).parent.parent / "bin" / "VirtualDesktop11-24H2.exe")
        # 严格按照你的示例命令：禁用动画 + 切换指定桌面
        cmd = [tool_path, "/Animation:Off", f"/Switch:{desktop_num}"]
        # 静默执行命令，不弹窗黑框、不阻塞UI
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

    # ========== 1. 创建所有UI控件 ==========
    # 标题【内部测试】- 核心适配目标1
    title_label = QLabel("内部测试", app_bar)
    title_label.setAlignment(Qt.AlignCenter) # 居中不变
    
    # 下划线分割线
    line = QFrame(app_bar)
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Plain)
    
    # 按钮列表
    buttons = []

    def on_button_hovered(hovered_button):
        """处理按钮悬停时的高亮效果 + 新增：悬停切换对应桌面"""
        # 取消所有按钮的高亮状态
        for btn in buttons:
            btn.setChecked(False)
        # 设置当前悬停按钮为选中状态
        hovered_button.setChecked(True)
        
        # ========== 新增：核心切换逻辑 ==========
        # 按钮索引 = 桌面编号 （桌面1=索引0 → /Switch:0，桌面2=索引1 → /Switch:1，完全对应）
        desktop_index = buttons.index(hovered_button)
        switch_desktop(desktop_index)

    for text in button_texts:
        btn = QPushButton(text, app_bar)
        btn.setCheckable(True)  # 设置按钮为可选择的
        # 设置按钮悬停事件
        btn.installEventFilter(app_bar)  # 为每个按钮安装事件过滤器
        btn.setAttribute(Qt.WA_Hover)  # 启用按钮的悬停事件
        buttons.append(btn)

    # ========== 2. 布局设置 ==========
    def setup_layout():
        # 清除旧布局
        if app_bar.layout():
            while app_bar.layout().count():
                child = app_bar.layout().takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
            QWidget().setLayout(app_bar.layout())
        
        # 主布局 无边距无间距 紧凑贴合侧边栏
        main_layout = QVBoxLayout(app_bar)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题容器
        title_container = QWidget(app_bar)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_layout.addWidget(title_label)
        title_layout.addWidget(line)
        main_layout.addWidget(title_container)
        
        # 添加所有按钮
        for btn in buttons:
            main_layout.addWidget(btn)
        
        main_layout.addStretch()

    # ========== 3. 核心【完美自适应】样式更新函数 【全部重写优化】 ==========
    def update_dynamic_styles():
        """所有UI元素 完全根据侧边栏宽度 自动等比调整大小"""
        bar_width = app_bar.width()  # 获取当前侧边栏的宽度
        
        # ===== 【所有尺寸都基于宽度动态计算，无固定值，核心！】 =====
        # 标题相关 自适应配置（内部测试）
        title_font_size = max(8, int(bar_width * 0.18))  # 标题字号：宽度占比18%，最小8px
        title_padding = max(4, int(bar_width * 0.06))     # 标题内边距：宽度占比6%，最小4px
        title_min_height = max(20, int(bar_width * 0.25)) # 标题栏高度：宽度占比25%，最小20px
        
        # 分割线下划线 自适应配置
        line_height = max(2, int(bar_width * 0.03))       # 分割线粗细：宽度占比3%，最小2px
        
        # 按钮相关 自适应配置（核心适配目标2）
        btn_font_size = max(7, int(bar_width * 0.3))     # 按钮字号：宽度占比15%，最小7px
        btn_padding_left = max(6, int(bar_width * 0.1))  # 按钮文字左内边距：宽度占比8%，最小6px
        btn_min_height = max(25, int(bar_width * 0.80))   # 按钮高度：宽度占比22%，最小25px

        # 更新标题样式 + 自适应
        title_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {title_font_size}px;
                font-weight: bold;
                padding: {title_padding}px; /* 上下左右都有内边距，跟随宽度缩放 */
            }}
        """)
        title_label.setMinimumHeight(title_min_height)

        # 更新分割线样式 + 自适应粗细 + 修复颜色不生效bug
        line.setFixedHeight(line_height)
        line.setStyleSheet(f"QFrame {{ border-top: {line_height}px solid white; }}")

        # 更新按钮样式 + 全维度自适应
        for btn in buttons:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2d2d30;
                    color: white;
                    border: none;
                    font-size: {btn_font_size}px;
                    text-align: left;
                    padding-left: {btn_padding_left}px; /* 按钮内边距跟随宽度缩放 */
                }}
                QPushButton:hover {{
                    background-color: #3e3e42;
                    border-left: 2px solid #ffffff; /* 悬浮加左侧白线，更美观 */
                }}
                QPushButton:pressed {{
                    background-color: #4f4f54; /* 点击按下加深，体验更好 */
                }}
                QPushButton:checked {{
                    background-color: #3e3e42; /* 按钮选中后保持高亮 */
                }}
            """)
            btn.setMinimumHeight(btn_min_height)

    # ========== 4. 监听尺寸变化，实时自适应 ==========
    def event_filter(watched, event):
        if isinstance(watched, QPushButton):
            if event.type() == QEvent.Enter:
                on_button_hovered(watched)  # 鼠标悬停时触发按钮的高亮显示
        if watched == app_bar and event.type() == QEvent.Resize:
            update_dynamic_styles()  # 宽度一变，立刻更新所有样式尺寸
        return DebugAppBarLeft.eventFilter(app_bar, watched, event)
    
    app_bar.installEventFilter(app_bar)
    app_bar.eventFilter = event_filter

    # ========== 初始化 ==========
    setup_layout()
    update_dynamic_styles()
    
    return app_bar

# 主程序运行
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = create_appbar_button_list(edge=ABEdge.LEFT, button_texts=["AI", "Work", "Edge","Docs"])
    window.show()
    sys.exit(app.exec())