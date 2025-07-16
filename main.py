#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件同步工具 - 主程序入口

功能特性:
- 支持单向和双向文件同步
- 文件内容校验（MD5哈希）
- 自定义过滤规则
- 进度显示和日志记录
- 失败重试机制
- 系统托盘驻留
- 配置文件支持

作者: AI Assistant
版本: 1.0.0
"""

import sys
import os
import traceback
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from sync_gui import SyncToolGUI
    from logger import Logger
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖已正确安装")
    print("运行: pip install -r requirements.txt")
    sys.exit(1)

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_modules = [
        'tkinter',
        'PIL',
        'pystray',
        'threading',
        'json',
        'hashlib',
        'shutil',
        'pathlib'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("缺少以下必要模块:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def setup_environment():
    """设置运行环境"""
    # 创建必要的目录
    directories = ['logs', 'assets', 'temp']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # 设置日志
    logger = Logger()
    logger.info("文件同步工具启动")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    
    return logger

def main():
    """主函数"""
    try:
        # 检查依赖
        if not check_dependencies():
            input("按回车键退出...")
            return 1
        
        # 设置环境
        logger = setup_environment()
        
        # 检查Python版本
        if sys.version_info < (3, 7):
            error_msg = f"需要Python 3.7或更高版本，当前版本: {sys.version}"
            logger.error(error_msg)
            print(error_msg)
            input("按回车键退出...")
            return 1
        
        # 启动GUI应用
        logger.info("启动GUI界面")
        app = SyncToolGUI()
        app.run()
        
        logger.info("应用程序正常退出")
        return 0
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
        return 0
    except Exception as e:
        error_msg = f"程序运行时发生未处理的异常: {str(e)}"
        print(error_msg)
        print("详细错误信息:")
        traceback.print_exc()
        
        # 尝试记录到日志
        try:
            logger = Logger()
            logger.log_error_with_traceback("程序异常退出", e)
        except:
            pass
        
        input("按回车键退出...")
        return 1

def show_help():
    """显示帮助信息"""
    help_text = """
文件同步工具 v1.0.0

使用方法:
  python main.py              # 启动GUI界面
  python main.py --help       # 显示此帮助信息
  python main.py --version    # 显示版本信息

功能特性:
  ✓ 单向/双向文件同步
  ✓ 文件内容校验（MD5）
  ✓ 自定义过滤规则
  ✓ 进度显示和日志记录
  ✓ 失败重试机制（最多5次）
  ✓ 系统托盘驻留
  ✓ 配置文件支持
  ✓ 子目录结构同步

系统要求:
  - Windows 10/11
  - Python 3.7+
  - 所需依赖包（见requirements.txt）

更多信息请参考README.md文件。
"""
    print(help_text)

def show_version():
    """显示版本信息"""
    version_text = """
文件同步工具 v1.0.0

构建信息:
  - Python版本: {python_version}
  - 平台: {platform}
  - 架构: {architecture}

作者: AI Assistant
许可: MIT License
""".format(
        python_version=sys.version.split()[0],
        platform=sys.platform,
        architecture=" ".join([sys.platform, "64bit" if sys.maxsize > 2**32 else "32bit"])
    )
    print(version_text)

if __name__ == "__main__":
    # 处理命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--help', '-h', 'help']:
            show_help()
            sys.exit(0)
        elif arg in ['--version', '-v', 'version']:
            show_version()
            sys.exit(0)
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("使用 --help 查看帮助信息")
            sys.exit(1)
    
    # 运行主程序
    exit_code = main()
    sys.exit(exit_code)