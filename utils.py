import hashlib
import os
import time
from datetime import datetime
import json

class Utils:
    def __init__(self):
        pass
        
    def calculate_md5(self, file_path, chunk_size=8192):
        """计算文件的MD5哈希值"""
        if not os.path.exists(file_path):
            return None
            
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"计算MD5失败: {file_path} - {e}")
            return None
            
    def calculate_sha256(self, file_path, chunk_size=8192):
        """计算文件的SHA256哈希值"""
        if not os.path.exists(file_path):
            return None
            
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"计算SHA256失败: {file_path} - {e}")
            return None
            
    def format_file_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.2f} {size_names[i]}"
        
    def format_timestamp(self, timestamp, format_str="%Y-%m-%d %H:%M:%S"):
        """格式化时间戳"""
        try:
            return datetime.fromtimestamp(timestamp).strftime(format_str)
        except Exception:
            return "未知时间"
            
    def get_current_timestamp(self):
        """获取当前时间戳"""
        return time.time()
        
    def get_current_datetime_str(self, format_str="%Y-%m-%d %H:%M:%S"):
        """获取当前时间字符串"""
        return datetime.now().strftime(format_str)
        
    def compare_file_times(self, file1_path, file2_path):
        """比较两个文件的修改时间"""
        try:
            mtime1 = os.path.getmtime(file1_path)
            mtime2 = os.path.getmtime(file2_path)
            
            if abs(mtime1 - mtime2) < 1:  # 允许1秒误差
                return 0  # 相等
            elif mtime1 > mtime2:
                return 1  # file1更新
            else:
                return -1  # file2更新
        except Exception:
            return None
            
    def is_file_locked(self, file_path):
        """检查文件是否被锁定"""
        try:
            with open(file_path, 'r+b') as f:
                return False
        except IOError:
            return True
        except Exception:
            return True
            
    def safe_create_directory(self, directory_path):
        """安全创建目录"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {directory_path} - {e}")
            return False
            
    def get_file_info(self, file_path):
        """获取文件详细信息"""
        if not os.path.exists(file_path):
            return None
            
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'size_formatted': self.format_file_size(stat.st_size),
                'mtime': stat.st_mtime,
                'mtime_formatted': self.format_timestamp(stat.st_mtime),
                'ctime': stat.st_ctime,
                'ctime_formatted': self.format_timestamp(stat.st_ctime),
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path),
                'extension': os.path.splitext(file_path)[1].lower()
            }
        except Exception as e:
            print(f"获取文件信息失败: {file_path} - {e}")
            return None
            
    def validate_path(self, path):
        """验证路径是否有效"""
        if not path or not isinstance(path, str):
            return False, "路径不能为空"
            
        # 检查路径长度
        if len(path) > 260:  # Windows路径长度限制
            return False, "路径长度超过限制"
            
        # 检查非法字符
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in illegal_chars:
            if char in os.path.basename(path):
                return False, f"路径包含非法字符: {char}"
                
        return True, "路径有效"
        
    def clean_filename(self, filename):
        """清理文件名中的非法字符"""
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        cleaned = filename
        for char in illegal_chars:
            cleaned = cleaned.replace(char, '_')
        return cleaned
        
    def get_relative_path(self, file_path, base_path):
        """获取相对路径"""
        try:
            return os.path.relpath(file_path, base_path)
        except Exception:
            return file_path
            
    def normalize_path(self, path):
        """标准化路径"""
        return os.path.normpath(os.path.abspath(path))
        
    def is_subdirectory(self, child_path, parent_path):
        """检查是否为子目录"""
        try:
            child_path = self.normalize_path(child_path)
            parent_path = self.normalize_path(parent_path)
            return child_path.startswith(parent_path + os.sep) or child_path == parent_path
        except Exception:
            return False
            
    def copy_file_metadata(self, source_path, target_path):
        """复制文件元数据（时间戳等）"""
        try:
            stat = os.stat(source_path)
            os.utime(target_path, (stat.st_atime, stat.st_mtime))
            return True
        except Exception as e:
            print(f"复制元数据失败: {source_path} -> {target_path} - {e}")
            return False
            
    def get_disk_usage(self, path):
        """获取磁盘使用情况"""
        try:
            if os.name == 'nt':  # Windows
                import shutil
                total, used, free = shutil.disk_usage(path)
            else:  # Unix/Linux
                statvfs = os.statvfs(path)
                total = statvfs.f_frsize * statvfs.f_blocks
                free = statvfs.f_frsize * statvfs.f_available
                used = total - free
                
            return {
                'total': total,
                'used': used,
                'free': free,
                'total_formatted': self.format_file_size(total),
                'used_formatted': self.format_file_size(used),
                'free_formatted': self.format_file_size(free),
                'usage_percent': round((used / total) * 100, 2) if total > 0 else 0
            }
        except Exception as e:
            print(f"获取磁盘使用情况失败: {path} - {e}")
            return None
            
    def load_json_config(self, config_path, default_config=None):
        """加载JSON配置文件"""
        if not os.path.exists(config_path):
            return default_config
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {config_path} - {e}")
            return default_config
            
    def save_json_config(self, config_path, config_data):
        """保存JSON配置文件"""
        try:
            # 确保目录存在
            config_dir = os.path.dirname(config_path)
            if config_dir:
                self.safe_create_directory(config_dir)
                
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {config_path} - {e}")
            return False
            
    def backup_file(self, file_path, backup_suffix=".bak"):
        """备份文件"""
        if not os.path.exists(file_path):
            return False
            
        backup_path = file_path + backup_suffix
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"备份文件失败: {file_path} - {e}")
            return False
            
    def get_file_count_in_directory(self, directory, recursive=True):
        """获取目录中的文件数量"""
        if not os.path.exists(directory):
            return 0
            
        count = 0
        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    count += len(files)
            else:
                count = len([f for f in os.listdir(directory) 
                           if os.path.isfile(os.path.join(directory, f))])
        except Exception as e:
            print(f"统计文件数量失败: {directory} - {e}")
            
        return count
        
    def calculate_directory_size(self, directory):
        """计算目录总大小"""
        if not os.path.exists(directory):
            return 0
            
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        continue
        except Exception as e:
            print(f"计算目录大小失败: {directory} - {e}")
            
        return total_size