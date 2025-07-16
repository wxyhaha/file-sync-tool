# SyncTool - File Synchronization Tool

**Language / 语言**: [English](#english) | [中文](README_CN.md)

---

## English

A cross-platform file synchronization tool developed with Python and Tkinter, supporting multi-configuration management, real-time sync, system tray mode, intuitive GUI, and one-click packaging.

## 🚀 Key Features

### Core Features
- **Dual Sync Modes**: Support for both one-way and two-way synchronization
- **Smart Comparison**: File comparison based on size, modification time, and MD5 hash
- **Progress Display**: Real-time sync progress and status information
- **Logging System**: Detailed sync logs with rotation and export support
- **Retry Mechanism**: Automatic retry up to 5 times for failed operations
- **Subdirectory Sync**: Complete directory structure preservation

### Advanced Features
- **File Filtering**: Custom include/exclude rules with wildcard support
- **File Verification**: MD5 hash verification for file integrity
- **System Tray**: Minimize to system tray with background operation
- **Configuration Management**: Auto-save and load sync configurations
- **Error Handling**: Comprehensive error handling and user notifications
- **Multi-Configuration**: Create and manage multiple sync profiles

## 📋 System Requirements

### Runtime Environment
- **Operating System**: Windows 10/11, macOS, Linux
- **Python Version**: Python 3.7 or higher
- **Memory**: At least 512MB RAM
- **Disk Space**: At least 100MB available space

### Dependencies
Main dependencies include:
- `tkinter` - GUI framework
- `Pillow` - Image processing
- `pystray` - System tray support
- `watchdog` - File monitoring
- `pyinstaller` - Packaging tool

See `requirements.txt` for complete dependency list

## 🛠️ Installation and Deployment

### Method 1: Run from Source

1. **Clone or download the project**
   ```bash
   git clone https://github.com/wxyhaha/file-sync-tool.git
   cd sync-tool
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the program**
   ```bash
   python main.py
   ```

### Method 2: Build Executable

1. **Install packaging dependencies**
   ```bash
   pip install pyinstaller
   ```

2. **Run build script**
   ```bash
   python build.py
   ```

3. **Get executable file**
   - After building, executable is located at `dist/SyncTool.exe`
   - Can run directly without Python environment

### Build Environment Configuration

#### Environment Preparation
1. **Python Environment**
   - Recommended Python 3.8-3.11 versions
   - Ensure pip is updated: `python -m pip install --upgrade pip`

2. **Virtual Environment (Recommended)**
   ```bash
   # Create virtual environment
   python -m venv sync_tool_env
   
   # Activate virtual environment
   # Windows:
   sync_tool_env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **System Dependencies**
   - Windows SDK (for certain system calls)
   - Visual C++ Redistributable (if needed)

#### Build Process Details

1. **Prepare build environment**
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   
   # Install packaging tools
   pip install pyinstaller
   ```

2. **Run automated build script**
   ```bash
   python build.py
   ```
   
   The script automatically performs:
   - Check PyInstaller installation status
   - Create icon files (SVG to ICO conversion)
   - Generate PyInstaller configuration
   - Create version information file
   - Execute packaging process
   - Generate installation script

3. **Manual build (optional)**
   ```bash
   # Basic build command
   pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
   
   # Advanced build command (with resource files)
   pyinstaller --onefile --windowed \
     --icon=assets/icon.ico \
     --add-data "assets;assets" \
     --add-data "sync_config.json;." \
     --hidden-import="PIL._tkinter_finder" \
     --hidden-import="pystray._win32" \
     main.py
   ```

#### Build Optimization Tips

1. **Reduce file size**
   - Use `--exclude-module` to exclude unnecessary modules
   - Use UPX compression (enabled in build.py)
   - Clean unnecessary dependencies

2. **Improve compatibility**
   - Build in environment similar to target system
   - Test compatibility across different Windows versions
   - Include necessary runtime libraries

3. **Solve common issues**
   - Add missing modules to `hiddenimports` for import errors
   - Use `--add-binary` to include missing DLLs
   - Check ICO file format if icon doesn't display

## 📖 User Guide

### Basic Usage

1. **Start the program**
   - Double-click `SyncTool.exe` or run `python main.py`

2. **Configure sync paths**
   - Click "Browse" buttons to select source and target directories
   - Or directly input paths in text boxes

3. **Choose sync mode**
   - **One-way sync**: Only sync from source to target directory
   - **Two-way sync**: Mutual sync of latest files between directories

4. **Set filter rules (optional)**
   - Click "?" button for filter rules help
   - Example: `*.txt;*.doc` sync only txt and doc files
   - Example: `!*.tmp;!*.log` exclude tmp and log files

5. **Start synchronization**
   - Click "Start Sync" button
   - Monitor progress bar and log information

### Filter Rules Details

Filter rules use semicolon (;) separation, supporting:

#### Include Rules
- `*.txt` - Sync only txt files
- `*.{jpg,png,gif}` - Sync only image files
- `documents/*` - Sync only documents folder content
- `important.*` - Sync only files starting with "important"

#### Exclude Rules (starting with !)
- `!*.tmp` - Exclude temporary files
- `!*.log` - Exclude log files
- `!cache/*` - Exclude cache folder
- `!.*` - Exclude hidden files

#### Combined Usage
```
*.doc;*.pdf;!*temp*;!backup/*
```
Sync only doc and pdf files, but exclude files containing "temp" and backup folder

### Advanced Features

#### System Tray Mode
1. Click "Minimize to Tray" button
2. Program displays icon in system tray
3. Right-click tray icon to:
   - Show main window
   - Start synchronization
   - Exit program

#### Configuration Management
1. After setting sync parameters, click "Save Config"
2. Program auto-loads configuration on next startup
3. Configuration saved in `sync_config.json`
4. Support multiple configuration profiles

#### Log Viewing
- Real-time logs displayed at bottom of program interface
- Detailed logs saved in `logs/sync_tool.log`
- Support log rotation to prevent oversized files

## 🏗️ Project Structure

```
SyncTool/
├── main.py              # Program entry point
├── sync_gui.py          # Main GUI interface
├── sync_core.py         # Core sync logic
├── logger.py            # Logging module
├── utils.py             # Utility functions
├── build.py             # Build script
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation (English)
├── README_CN.md         # Project documentation (Chinese)
├── assets/              # Resource files
│   ├── icon.svg         # SVG icon
│   └── icon.ico         # ICO icon (auto-generated)
├── logs/                # Log directory (auto-created)
├── dist/                # Build output directory
└── build/               # Build temporary directory
```

### Module Description

- **main.py**: Program entry, handles command line args and exceptions
- **sync_gui.py**: Graphical user interface based on tkinter
- **sync_core.py**: Core sync logic including file comparison, copying, verification
- **logger.py**: Logging system supporting file and console output
- **utils.py**: Utility functions including MD5 calculation, path handling
- **build.py**: Automated build script

## 🔧 Configuration Options

### Basic Configuration
- `source_path`: Source directory path
- `target_path`: Target directory path
- `sync_mode`: Sync mode (one-way/two-way)
- `filter_rules`: Filter rules

### Advanced Configuration
- `max_retries`: Maximum retry count (default 5)
- `verify_hash`: Enable hash verification (default true)
- `log_level`: Log level (DEBUG/INFO/WARNING/ERROR)
- `auto_sync`: Enable automatic sync
- `auto_sync_interval`: Auto sync interval (seconds)

## 🐛 Troubleshooting

### Common Issues

1. **Program won't start**
   - Check Python version is 3.7+
   - Ensure all dependencies are correctly installed
   - Check error logs for detailed information

2. **Sync failure**
   - Check if source and target directories exist
   - Ensure sufficient disk space
   - Check file permissions
   - Review logs for specific errors

3. **Tray icon not showing**
   - Ensure pystray library is correctly installed
   - Check system tray settings
   - Restart program

4. **Packaged program won't run**
   - Check if target system has necessary runtime libraries
   - Ensure all resource files are correctly included
   - Rebuild in similar environment

### Log Analysis

Program generates logs in following locations:
- Console output: Real-time display of important information
- Interface logs: Log display area in GUI
- File logs: `logs/sync_tool.log`

Log level descriptions:
- **DEBUG**: Detailed debugging information
- **INFO**: General operation information
- **WARNING**: Warning information
- **ERROR**: Error information
- **CRITICAL**: Critical errors

## 🤝 Contributing

Welcome to submit issue reports and feature suggestions!

### Development Environment Setup
1. Fork the project repository
2. Create development branch
3. Install development dependencies: `pip install -r requirements.txt`
4. Develop and test
5. Submit Pull Request

### Code Standards
- Use Python PEP 8 code style
- Add appropriate comments and docstrings
- Write unit tests
- Ensure code passes all tests

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🔄 Version History

### v1.0.0 (2024-01-01)
- Initial release
- Support for one-way and two-way sync
- Graphical user interface
- File filtering and verification
- System tray functionality
- Configuration file support
- Complete logging system
- Multi-configuration management

## 📞 Support and Feedback

If you encounter issues or have improvement suggestions:

1. Check the troubleshooting section in this documentation
2. Review log files for detailed error information
3. Submit an Issue in the project repository
4. Contact the development team via email

---

**Thank you for using SyncTool!** 🎉
