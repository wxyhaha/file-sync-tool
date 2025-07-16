#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件同步工具 - 打包脚本

使用PyInstaller将Python程序打包成Windows可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            return True
        except subprocess.CalledProcessError:
            print("安装PyInstaller失败")
            return False

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('sync_config.json', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'pystray._win32',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SyncTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    version='version_info.txt'
)
'''
    
    with open('SyncTool.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建PyInstaller规格文件: SyncTool.spec")

def create_version_info():
    """创建版本信息文件"""
    version_info = '''
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'SyncTool Development'),
        StringStruct(u'FileDescription', u'文件同步工具'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'SyncTool'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024'),
        StringStruct(u'OriginalFilename', u'SyncTool.exe'),
        StringStruct(u'ProductName', u'文件同步工具'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    print("已创建版本信息文件: version_info.txt")

def convert_svg_to_ico():
    """将SVG图标转换为ICO格式"""
    try:
        from PIL import Image
        import cairosvg
        
        # 将SVG转换为PNG
        cairosvg.svg2png(url='assets/icon.svg', write_to='assets/icon.png', output_width=256, output_height=256)
        
        # 将PNG转换为ICO
        img = Image.open('assets/icon.png')
        img.save('assets/icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        
        # 清理临时PNG文件
        os.remove('assets/icon.png')
        
        print("已创建ICO图标文件: assets/icon.ico")
        return True
    except ImportError:
        print("警告: 缺少cairosvg或PIL库，无法转换SVG图标")
        print("将使用默认图标或跳过图标设置")
        return False
    except Exception as e:
        print(f"转换图标失败: {e}")
        return False

def create_default_ico():
    """创建默认的ICO图标"""
    try:
        from PIL import Image, ImageDraw
        
        # 创建一个简单的图标
        img = Image.new('RGBA', (64, 64), (74, 144, 226, 255))
        draw = ImageDraw.Draw(img)
        
        # 绘制简单的同步图标
        draw.ellipse([4, 4, 60, 60], fill=(74, 144, 226, 255), outline=(46, 92, 138, 255), width=2)
        draw.text((20, 25), "SYNC", fill=(255, 255, 255, 255))
        
        # 保存为ICO
        img.save('assets/icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
        print("已创建默认ICO图标文件: assets/icon.ico")
        return True
    except Exception as e:
        print(f"创建默认图标失败: {e}")
        return False

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    try:
        # 运行PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "SyncTool.spec"]
        
        # 使用更安全的编码处理方式
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            print("构建成功!")
            print(f"可执行文件位置: {os.path.abspath('dist/SyncTool.exe')}")
            return True
        else:
            print("构建失败!")
            print("错误输出:")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print("标准输出:")
                print(result.stdout)
            return False
            
    except UnicodeDecodeError as e:
        print(f"编码错误: {e}")
        print("尝试使用系统默认编码重新运行...")
        try:
            # 如果UTF-8失败，尝试不指定编码
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0:
                print("构建成功!")
                print(f"可执行文件位置: {os.path.abspath('dist/SyncTool.exe')}")
                return True
            else:
                print("构建失败!")
                print("错误输出:")
                print(result.stderr.decode('utf-8', errors='replace') if result.stderr else "无错误信息")
                return False
        except Exception as e2:
            print(f"重试失败: {e2}")
            return False
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        return False

def clean_build_files():
    """清理构建文件"""
    print("清理构建文件...")
    
    dirs_to_remove = ['build', '__pycache__']
    files_to_remove = ['SyncTool.spec', 'version_info.txt']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除目录: {dir_name}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"已删除文件: {file_name}")
    
    # 清理Python缓存
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
                dirs.remove(dir_name)

def create_installer_script():
    """创建安装脚本"""
    installer_content = '''
@echo off
echo 文件同步工具安装程序
echo.

set INSTALL_DIR=%USERPROFILE%\\SyncTool

echo 正在创建安装目录...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 正在复制文件...
copy "SyncTool.exe" "%INSTALL_DIR%\\"
copy "README.md" "%INSTALL_DIR%\\" 2>nul

echo 正在创建桌面快捷方式...
set DESKTOP=%USERPROFILE%\\Desktop
echo [InternetShortcut] > "%DESKTOP%\\文件同步工具.url"
echo URL=file:///%INSTALL_DIR%\\SyncTool.exe >> "%DESKTOP%\\文件同步工具.url"
echo IconFile=%INSTALL_DIR%\\SyncTool.exe >> "%DESKTOP%\\文件同步工具.url"
echo IconIndex=0 >> "%DESKTOP%\\文件同步工具.url"

echo.
echo 安装完成!
echo 程序已安装到: %INSTALL_DIR%
echo 桌面快捷方式已创建
echo.
pause
'''
    
    with open('dist/install.bat', 'w', encoding='gbk') as f:
        f.write(installer_content)
    print("已创建安装脚本: dist/install.bat")

def main():
    """主函数"""
    print("文件同步工具 - 打包脚本")
    print("=" * 40)
    
    # 检查当前目录
    if not os.path.exists('main.py'):
        print("错误: 请在项目根目录运行此脚本")
        return 1
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return 1
    
    # 创建图标
    if not os.path.exists('assets/icon.ico'):
        if not convert_svg_to_ico():
            create_default_ico()
    
    # 创建构建文件
    create_spec_file()
    create_version_info()
    
    # 构建可执行文件
    if build_executable():
        # 创建安装脚本
        create_installer_script()
        
        print("\n构建完成!")
        print(f"可执行文件: {os.path.abspath('dist/SyncTool.exe')}")
        print(f"安装脚本: {os.path.abspath('dist/install.bat')}")
        
        # 默认清理构建文件
        print("\n正在清理构建文件...")
        clean_build_files()
        
        return 0
    else:
        print("\n构建失败!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\n按回车键退出...")
    sys.exit(exit_code)