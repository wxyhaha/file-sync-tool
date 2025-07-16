import os
import shutil
import hashlib
import time
from pathlib import Path
import fnmatch
from datetime import datetime
from utils import Utils

class SyncCore:
    def __init__(self):
        self.utils = Utils()
        self.stop_flag = False
        self.max_retries = 5
        
    def sync_directories(self, config):
        """同步目录"""
        self.stop_flag = False
        source_path = config['source_path']
        target_path = config['target_path']
        sync_mode = config['sync_mode']
        filter_rules = config.get('filter_rules', '')
        progress_callback = config.get('progress_callback')
        log_callback = config.get('log_callback')
        
        try:
            # 解析过滤规则
            include_patterns, exclude_patterns = self._parse_filter_rules(filter_rules)
            
            # 获取文件列表
            log_callback("正在扫描文件...")
            source_files = self._get_file_list(source_path, include_patterns, exclude_patterns)
            target_files = self._get_file_list(target_path, include_patterns, exclude_patterns)
            
            log_callback(f"源目录文件数: {len(source_files)}")
            log_callback(f"目标目录文件数: {len(target_files)}")
            
            # 比较文件
            sync_actions = self._compare_files(source_path, target_path, source_files, target_files, sync_mode)
            
            total_actions = len(sync_actions)
            if total_actions == 0:
                log_callback("没有需要同步的文件")
                return "同步完成，没有文件需要更新"
                
            log_callback(f"需要同步的文件数: {total_actions}")
            
            # 执行同步
            completed = 0
            for action in sync_actions:
                if self.stop_flag:
                    log_callback("同步已停止")
                    break
                    
                success = self._execute_sync_action(action, log_callback)
                if success:
                    completed += 1
                    
                # 更新进度
                if progress_callback:
                    progress = (completed / total_actions) * 100
                    progress_callback(progress)
                    
            result = f"同步完成，成功处理 {completed}/{total_actions} 个文件"
            log_callback(result)
            return result
            
        except Exception as e:
            error_msg = f"同步过程中发生错误: {str(e)}"
            log_callback(error_msg)
            raise Exception(error_msg)
            
    def _parse_filter_rules(self, filter_rules):
        """解析过滤规则"""
        include_patterns = []
        exclude_patterns = []
        
        if not filter_rules.strip():
            return include_patterns, exclude_patterns
            
        rules = [rule.strip() for rule in filter_rules.split(';') if rule.strip()]
        
        for rule in rules:
            if rule.startswith('!'):
                # 排除规则
                exclude_patterns.append(rule[1:])
            else:
                # 包含规则
                include_patterns.append(rule)
                
        return include_patterns, exclude_patterns
        
    def _get_file_list(self, directory, include_patterns, exclude_patterns):
        """获取目录下的文件列表"""
        file_list = {}
        
        if not os.path.exists(directory):
            return file_list
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                
                # 应用过滤规则
                if self._should_include_file(relative_path, include_patterns, exclude_patterns):
                    file_info = {
                        'path': file_path,
                        'relative_path': relative_path,
                        'size': os.path.getsize(file_path),
                        'mtime': os.path.getmtime(file_path),
                        'hash': None  # 延迟计算
                    }
                    file_list[relative_path] = file_info
                    
        return file_list
        
    def _should_include_file(self, relative_path, include_patterns, exclude_patterns):
        """判断文件是否应该包含在同步中"""
        # 检查排除规则
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(os.path.basename(relative_path), pattern):
                return False
                
        # 如果没有包含规则，默认包含所有文件
        if not include_patterns:
            return True
            
        # 检查包含规则
        for pattern in include_patterns:
            if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(os.path.basename(relative_path), pattern):
                return True
                
        return False
        
    def _compare_files(self, source_path, target_path, source_files, target_files, sync_mode):
        """比较文件并生成同步动作"""
        sync_actions = []
        
        # 处理源目录中的文件
        for relative_path, source_info in source_files.items():
            if relative_path in target_files:
                target_info = target_files[relative_path]
                
                # 文件存在于两个目录中，检查是否需要更新
                if self._need_update(source_info, target_info):
                    sync_actions.append({
                        'action': 'update',
                        'source': source_info['path'],
                        'target': os.path.join(target_path, relative_path),
                        'relative_path': relative_path,
                        'direction': 'source_to_target'
                    })
            else:
                # 文件只存在于源目录中
                sync_actions.append({
                    'action': 'copy',
                    'source': source_info['path'],
                    'target': os.path.join(target_path, relative_path),
                    'relative_path': relative_path,
                    'direction': 'source_to_target'
                })
                
        # 双向同步：处理目标目录中的文件
        if sync_mode == "双向同步":
            for relative_path, target_info in target_files.items():
                if relative_path not in source_files:
                    # 文件只存在于目标目录中
                    sync_actions.append({
                        'action': 'copy',
                        'source': target_info['path'],
                        'target': os.path.join(source_path, relative_path),
                        'relative_path': relative_path,
                        'direction': 'target_to_source'
                    })
                else:
                    # 文件存在于两个目录中，检查反向更新
                    source_info = source_files[relative_path]
                    if self._need_update(target_info, source_info):
                        sync_actions.append({
                            'action': 'update',
                            'source': target_info['path'],
                            'target': os.path.join(source_path, relative_path),
                            'relative_path': relative_path,
                            'direction': 'target_to_source'
                        })
                        
        return sync_actions
        
    def _need_update(self, source_info, target_info):
        """判断是否需要更新文件"""
        # 首先比较修改时间
        if abs(source_info['mtime'] - target_info['mtime']) > 1:  # 允许1秒误差
            return source_info['mtime'] > target_info['mtime']
            
        # 如果修改时间相近，比较文件大小
        if source_info['size'] != target_info['size']:
            return True
            
        # 如果大小相同，比较哈希值
        source_hash = self._get_file_hash(source_info['path'])
        target_hash = self._get_file_hash(target_info['path'])
        
        return source_hash != target_hash
        
    def _get_file_hash(self, file_path):
        """计算文件哈希值"""
        return self.utils.calculate_md5(file_path)
        
    def _execute_sync_action(self, action, log_callback):
        """执行同步动作"""
        source = action['source']
        target = action['target']
        relative_path = action['relative_path']
        action_type = action['action']
        direction = action['direction']
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                # 确保目标目录存在
                target_dir = os.path.dirname(target)
                os.makedirs(target_dir, exist_ok=True)
                
                # 执行复制
                if action_type in ['copy', 'update']:
                    shutil.copy2(source, target)
                    
                    # 验证复制结果
                    if self._verify_copy(source, target):
                        direction_text = "→" if direction == 'source_to_target' else "←"
                        log_callback(f"{action_type.upper()} {direction_text} {relative_path}")
                        return True
                    else:
                        raise Exception("文件校验失败")
                        
            except Exception as e:
                if attempt < self.max_retries - 1:
                    log_callback(f"重试 {attempt + 1}/{self.max_retries}: {relative_path} - {str(e)}")
                    time.sleep(1)  # 等待1秒后重试
                else:
                    log_callback(f"失败: {relative_path} - {str(e)}")
                    return False
                    
        return False
        
    def _verify_copy(self, source, target):
        """验证复制结果"""
        if not os.path.exists(target):
            return False
            
        # 比较文件大小
        if os.path.getsize(source) != os.path.getsize(target):
            return False
            
        # 比较哈希值
        source_hash = self._get_file_hash(source)
        target_hash = self._get_file_hash(target)
        
        return source_hash == target_hash
        
    def stop_sync(self):
        """停止同步"""
        self.stop_flag = True
        
    def get_directory_info(self, directory):
        """获取目录信息"""
        if not os.path.exists(directory):
            return None
            
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_files += 1
                    total_size += os.path.getsize(file_path)
                except OSError:
                    continue
                    
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
        
    def preview_sync(self, config):
        """预览同步操作（不实际执行）"""
        source_path = config['source_path']
        target_path = config['target_path']
        sync_mode = config['sync_mode']
        filter_rules = config.get('filter_rules', '')
        
        # 解析过滤规则
        include_patterns, exclude_patterns = self._parse_filter_rules(filter_rules)
        
        # 获取文件列表
        source_files = self._get_file_list(source_path, include_patterns, exclude_patterns)
        target_files = self._get_file_list(target_path, include_patterns, exclude_patterns)
        
        # 比较文件
        sync_actions = self._compare_files(source_path, target_path, source_files, target_files, sync_mode)
        
        # 统计信息
        stats = {
            'total_actions': len(sync_actions),
            'copy_actions': len([a for a in sync_actions if a['action'] == 'copy']),
            'update_actions': len([a for a in sync_actions if a['action'] == 'update']),
            'source_to_target': len([a for a in sync_actions if a['direction'] == 'source_to_target']),
            'target_to_source': len([a for a in sync_actions if a['direction'] == 'target_to_source'])
        }
        
        return {
            'actions': sync_actions,
            'stats': stats
        }