# 文件同步工具 (SyncTool)

**Language / 语言**: [English](README.md) | [中文](#中文)

---

## 中文

一个基于 Python 和 Tkinter 开发的跨平台文件同步工具，支持多配置管理、实时同步、托盘模式运行，提供直观的图形界面和一键打包功能。

## 🚀 主要功能

### 核心功能
- **双模式同步**: 支持单向同步和双向同步
- **智能比较**: 基于文件大小、修改时间和MD5哈希值的文件比较
- **进度显示**: 实时显示同步进度和状态信息
- **日志记录**: 详细的同步日志，支持日志轮转和导出
- **失败重试**: 自动重试机制，最多重试5次
- **子目录同步**: 完整保持目录结构

### 高级功能
- **文件过滤**: 自定义包含/排除规则，支持通配符
- **文件校验**: MD5哈希值验证确保文件完整性
- **托盘驻留**: 最小化到系统托盘，支持后台运行
- **配置管理**: 自动保存和加载同步配置
- **错误处理**: 完善的错误处理和用户提示
- **多配置支持**: 创建和管理多个同步配置文件

## 📋 系统要求

### 运行环境
- **操作系统**: Windows 10/11, macOS, Linux
- **Python版本**: Python 3.7 或更高版本
- **内存**: 至少 512MB RAM
- **磁盘空间**: 至少 100MB 可用空间

### 依赖库
主要依赖包括：
- `tkinter` - GUI界面
- `Pillow` - 图像处理
- `pystray` - 系统托盘支持
- `watchdog` - 文件监控
- `pyinstaller` - 打包工具

完整依赖列表请参考 `requirements.txt`

## 🛠️ 安装和部署

### 方法一：从源码运行

1. **克隆或下载项目**
   ```bash
   git clone https://github.com/wxyhaha/file-sync-tool.git
   cd sync-tool
   ```

2. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python main.py
   ```

### 方法二：打包成可执行文件

1. **安装打包依赖**
   ```bash
   pip install pyinstaller
   ```

2. **运行打包脚本**
   ```bash
   python build.py
   ```

3. **获取可执行文件**
   - 打包完成后，可执行文件位于 `dist/SyncTool.exe`
   - 可以直接运行，无需安装Python环境

### 打包环境配置详解

#### 环境准备
1. **Python环境**
   - 推荐使用 Python 3.8-3.11 版本
   - 确保pip已更新到最新版本：`python -m pip install --upgrade pip`

2. **虚拟环境（推荐）**
   ```bash
   # 创建虚拟环境
   python -m venv sync_tool_env
   
   # 激活虚拟环境
   # Windows:
   sync_tool_env\Scripts\activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **系统依赖**
   - Windows SDK（用于某些系统调用）
   - Visual C++ Redistributable（如果需要）

#### 打包步骤详解

1. **准备打包环境**
   ```bash
   # 确保所有依赖已安装
   pip install -r requirements.txt
   
   # 安装打包工具
   pip install pyinstaller
   ```

2. **运行自动打包脚本**
   ```bash
   python build.py
   ```
   
   脚本会自动执行以下操作：
   - 检查PyInstaller安装状态
   - 创建图标文件（SVG转ICO）
   - 生成PyInstaller配置文件
   - 创建版本信息文件
   - 执行打包过程
   - 生成安装脚本

3. **手动打包（可选）**
   ```bash
   # 基本打包命令
   pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
   
   # 高级打包命令（包含资源文件）
   pyinstaller --onefile --windowed \
     --icon=assets/icon.ico \
     --add-data "assets;assets" \
     --add-data "sync_config.json;." \
     --hidden-import="PIL._tkinter_finder" \
     --hidden-import="pystray._win32" \
     main.py
   ```

#### 打包优化建议

1. **减小文件大小**
   - 使用 `--exclude-module` 排除不需要的模块
   - 使用 UPX 压缩（在build.py中已启用）
   - 清理不必要的依赖

2. **提高兼容性**
   - 在目标系统相似的环境中打包
   - 测试不同Windows版本的兼容性
   - 包含必要的运行时库

3. **解决常见问题**
   - 如果遇到模块导入错误，添加到 `hiddenimports`
   - 如果缺少DLL，使用 `--add-binary` 包含
   - 如果图标不显示，检查ICO文件格式

## 📖 使用指南

### 基本使用

1. **启动程序**
   - 双击 `SyncTool.exe` 或运行 `python main.py`

2. **配置同步路径**
   - 点击"浏览"按钮选择源目录和目标目录
   - 或直接在文本框中输入路径

3. **选择同步模式**
   - **单向同步**: 只从源目录同步到目标目录
   - **双向同步**: 两个目录相互同步最新文件

4. **设置过滤规则（可选）**
   - 点击"?"按钮查看过滤规则帮助
   - 示例：`*.txt;*.doc` 只同步txt和doc文件
   - 示例：`!*.tmp;!*.log` 排除tmp和log文件

5. **开始同步**
   - 点击"开始同步"按钮
   - 观察进度条和日志信息

### 过滤规则详解

过滤规则使用分号(;)分隔，支持以下格式：

#### 包含规则
- `*.txt` - 只同步txt文件
- `*.{jpg,png,gif}` - 只同步图片文件
- `documents/*` - 只同步documents文件夹内容
- `important.*` - 只同步以important开头的文件

#### 排除规则（以!开头）
- `!*.tmp` - 排除临时文件
- `!*.log` - 排除日志文件
- `!cache/*` - 排除cache文件夹
- `!.*` - 排除隐藏文件

#### 组合使用
```
*.doc;*.pdf;!*temp*;!backup/*
```
只同步doc和pdf文件，但排除包含temp的文件和backup文件夹

### 高级功能

#### 托盘模式
1. 点击"最小化到托盘"按钮
2. 程序将在系统托盘中显示图标
3. 右键托盘图标可以：
   - 显示主窗口
   - 开始同步
   - 退出程序

#### 配置管理
1. 设置好同步参数后点击"保存配置"
2. 下次启动程序会自动加载配置
3. 配置文件位于 `sync_config.json`
4. 支持多个配置文件管理

#### 日志查看
- 程序界面下方显示实时日志
- 详细日志保存在 `logs/sync_tool.log`
- 支持日志轮转，避免文件过大

## 🏗️ 项目结构

```
SyncTool/
├── main.py              # 程序入口
├── sync_gui.py          # GUI主界面
├── sync_core.py         # 同步核心逻辑
├── logger.py            # 日志管理模块
├── utils.py             # 工具函数
├── build.py             # 打包脚本
├── requirements.txt     # Python依赖
├── README.md            # 项目文档（英文）
├── README_CN.md         # 项目文档（中文）
├── assets/              # 资源文件
│   ├── icon.svg         # SVG图标
│   └── icon.ico         # ICO图标（自动生成）
├── logs/                # 日志目录（自动创建）
├── dist/                # 打包输出目录
└── build/               # 打包临时目录
```

### 模块说明

- **main.py**: 程序入口，处理命令行参数和异常
- **sync_gui.py**: 图形用户界面，基于tkinter
- **sync_core.py**: 同步逻辑核心，包含文件比较、复制、验证
- **logger.py**: 日志系统，支持文件和控制台输出
- **utils.py**: 工具函数，包含MD5计算、路径处理等
- **build.py**: 自动化打包脚本

## 🔧 配置选项

### 基本配置
- `source_path`: 源目录路径
- `target_path`: 目标目录路径
- `sync_mode`: 同步模式（单向/双向）
- `filter_rules`: 过滤规则

### 高级配置
- `max_retries`: 最大重试次数（默认5）
- `verify_hash`: 是否启用哈希验证（默认true）
- `log_level`: 日志级别（DEBUG/INFO/WARNING/ERROR）
- `auto_sync`: 是否启用自动同步
- `auto_sync_interval`: 自动同步间隔（秒）

## 🐛 故障排除

### 常见问题

1. **程序无法启动**
   - 检查Python版本是否为3.7+
   - 确认所有依赖已正确安装
   - 查看错误日志获取详细信息

2. **同步失败**
   - 检查源目录和目标目录是否存在
   - 确认有足够的磁盘空间
   - 检查文件权限
   - 查看日志了解具体错误

3. **托盘图标不显示**
   - 确认pystray库已正确安装
   - 检查系统托盘设置
   - 重启程序

4. **打包后程序无法运行**
   - 检查目标系统是否有必要的运行时库
   - 确认所有资源文件已正确包含
   - 在相似环境中重新打包

### 日志分析

程序会在以下位置生成日志：
- 控制台输出：实时显示重要信息
- 界面日志：GUI中的日志显示区域
- 文件日志：`logs/sync_tool.log`

日志级别说明：
- **DEBUG**: 详细的调试信息
- **INFO**: 一般操作信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

## 🤝 贡献指南

欢迎提交问题报告和功能建议！

### 开发环境设置
1. Fork项目仓库
2. 创建开发分支
3. 安装开发依赖：`pip install -r requirements.txt`
4. 进行开发和测试
5. 提交Pull Request

### 代码规范
- 使用Python PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试
- 确保代码通过所有测试

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 🔄 版本历史

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持单向和双向同步
- 图形用户界面
- 文件过滤和校验
- 托盘驻留功能
- 配置文件支持
- 完整的日志系统
- 多配置管理功能

## 📞 支持和反馈

如果您在使用过程中遇到问题或有改进建议，请：

1. 查看本文档的故障排除部分
2. 检查日志文件获取详细错误信息
3. 在项目仓库中提交Issue
4. 发送邮件至开发团队

---

**感谢使用文件同步工具！** 🎉
