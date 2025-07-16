import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, log_dir="logs", log_file="sync_tool.log", max_size=10*1024*1024, backup_count=5):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志目录
            log_file: 日志文件名
            max_size: 单个日志文件最大大小（字节）
            backup_count: 保留的备份文件数量
        """
        self.log_dir = log_dir
        self.log_file = log_file
        self.max_size = max_size
        self.backup_count = backup_count
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置日志文件路径
        self.log_path = os.path.join(log_dir, log_file)
        
        # 初始化日志记录器
        self._setup_logger()
        
    def _setup_logger(self):
        """设置日志记录器"""
        # 创建日志记录器
        self.logger = logging.getLogger('SyncTool')
        self.logger.setLevel(logging.DEBUG)
        
        # 清除现有的处理器
        self.logger.handlers.clear()
        
        # 创建文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=self.max_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # 设置格式化器
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log(self, message, level='info'):
        """记录日志"""
        level = level.lower()
        if level == 'debug':
            self.logger.debug(message)
        elif level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'critical':
            self.logger.critical(message)
        else:
            self.logger.info(message)
            
    def debug(self, message):
        """记录调试信息"""
        self.logger.debug(message)
        
    def info(self, message):
        """记录一般信息"""
        self.logger.info(message)
        
    def warning(self, message):
        """记录警告信息"""
        self.logger.warning(message)
        
    def error(self, message):
        """记录错误信息"""
        self.logger.error(message)
        
    def critical(self, message):
        """记录严重错误信息"""
        self.logger.critical(message)
        
    def log_sync_start(self, source_path, target_path, sync_mode):
        """记录同步开始"""
        message = f"开始同步 - 源目录: {source_path}, 目标目录: {target_path}, 模式: {sync_mode}"
        self.info(message)
        
    def log_sync_end(self, success, message=""):
        """记录同步结束"""
        if success:
            self.info(f"同步完成 - {message}")
        else:
            self.error(f"同步失败 - {message}")
            
    def log_file_operation(self, operation, source, target, success, error_msg=""):
        """记录文件操作"""
        if success:
            self.info(f"{operation} 成功: {source} -> {target}")
        else:
            self.error(f"{operation} 失败: {source} -> {target} - {error_msg}")
            
    def log_error_with_traceback(self, message, exception):
        """记录带堆栈跟踪的错误"""
        import traceback
        error_msg = f"{message}\n异常信息: {str(exception)}\n堆栈跟踪:\n{traceback.format_exc()}"
        self.error(error_msg)
        
    def log_config_operation(self, operation, success, message=""):
        """记录配置操作"""
        if success:
            self.info(f"配置{operation}成功 - {message}")
        else:
            self.error(f"配置{operation}失败 - {message}")
            
    def log_filter_rules(self, include_patterns, exclude_patterns):
        """记录过滤规则"""
        if include_patterns:
            self.info(f"包含规则: {', '.join(include_patterns)}")
        if exclude_patterns:
            self.info(f"排除规则: {', '.join(exclude_patterns)}")
        if not include_patterns and not exclude_patterns:
            self.info("未设置过滤规则，将同步所有文件")
            
    def log_directory_scan(self, directory, file_count, total_size):
        """记录目录扫描结果"""
        size_mb = round(total_size / (1024 * 1024), 2)
        self.info(f"扫描目录: {directory} - 文件数: {file_count}, 总大小: {size_mb} MB")
        
    def log_retry_attempt(self, file_path, attempt, max_attempts, error):
        """记录重试尝试"""
        self.warning(f"重试 {attempt}/{max_attempts}: {file_path} - {error}")
        
    def log_hash_verification(self, file_path, success, source_hash="", target_hash=""):
        """记录哈希验证结果"""
        if success:
            self.debug(f"哈希验证成功: {file_path}")
        else:
            self.error(f"哈希验证失败: {file_path} - 源: {source_hash}, 目标: {target_hash}")
            
    def log_tray_operation(self, operation, success, message=""):
        """记录托盘操作"""
        if success:
            self.info(f"托盘{operation}成功 - {message}")
        else:
            self.error(f"托盘{operation}失败 - {message}")
            
    def get_log_file_path(self):
        """获取日志文件路径"""
        return self.log_path
        
    def get_log_files(self):
        """获取所有日志文件列表"""
        log_files = []
        try:
            for file in os.listdir(self.log_dir):
                if file.startswith(os.path.splitext(self.log_file)[0]):
                    log_files.append(os.path.join(self.log_dir, file))
            log_files.sort(key=os.path.getmtime, reverse=True)
        except Exception as e:
            self.error(f"获取日志文件列表失败: {e}")
        return log_files
        
    def clear_old_logs(self, days=30):
        """清理旧日志文件"""
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            cleared_count = 0
            for file in os.listdir(self.log_dir):
                file_path = os.path.join(self.log_dir, file)
                if os.path.isfile(file_path) and file.endswith('.log'):
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        cleared_count += 1
                        
            self.info(f"清理了 {cleared_count} 个旧日志文件（{days}天前）")
            return cleared_count
        except Exception as e:
            self.error(f"清理旧日志文件失败: {e}")
            return 0
            
    def get_log_statistics(self):
        """获取日志统计信息"""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'latest_file': None,
                'oldest_file': None
            }
            
            log_files = self.get_log_files()
            if not log_files:
                return stats
                
            stats['total_files'] = len(log_files)
            
            total_size = 0
            latest_time = 0
            oldest_time = float('inf')
            
            for file_path in log_files:
                file_size = os.path.getsize(file_path)
                file_time = os.path.getmtime(file_path)
                
                total_size += file_size
                
                if file_time > latest_time:
                    latest_time = file_time
                    stats['latest_file'] = file_path
                    
                if file_time < oldest_time:
                    oldest_time = file_time
                    stats['oldest_file'] = file_path
                    
            stats['total_size'] = total_size
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return stats
        except Exception as e:
            self.error(f"获取日志统计信息失败: {e}")
            return {}
            
    def export_logs(self, export_path, start_date=None, end_date=None):
        """导出日志到指定文件"""
        try:
            with open(export_path, 'w', encoding='utf-8') as export_file:
                export_file.write(f"# 同步工具日志导出\n")
                export_file.write(f"# 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                export_file.write(f"# 日期范围: {start_date or '全部'} - {end_date or '全部'}\n\n")
                
                log_files = self.get_log_files()
                for log_file in log_files:
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            export_file.write(f"\n=== {os.path.basename(log_file)} ===\n")
                            for line in f:
                                # 这里可以添加日期过滤逻辑
                                export_file.write(line)
                    except Exception as e:
                        export_file.write(f"读取日志文件失败: {log_file} - {e}\n")
                        
            self.info(f"日志导出成功: {export_path}")
            return True
        except Exception as e:
            self.error(f"日志导出失败: {export_path} - {e}")
            return False
            
    def set_log_level(self, level):
        """设置日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            self.info(f"日志级别已设置为: {level.upper()}")
        else:
            self.warning(f"无效的日志级别: {level}")