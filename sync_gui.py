import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
import json
import os
import sys
from datetime import datetime
import pystray
from PIL import Image
from sync_core import SyncCore
from logger import Logger
from utils import Utils

class SyncToolGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文件同步工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 初始化组件
        self.sync_core = SyncCore()
        self.logger = Logger()
        self.utils = Utils()
        
        # 配置文件路径
        self.config_file = "sync_configs.json"  # 改为多配置文件
        self.default_config_file = "sync_config.json"  # 保持兼容性
        
        # 界面变量
        self.source_path = tk.StringVar()
        self.target_path = tk.StringVar()
        self.sync_mode = tk.StringVar(value="单向同步")
        self.filter_rules = tk.StringVar()
        self.current_config_name = tk.StringVar(value="默认配置")
        self.is_syncing = False
        
        # 配置管理
        self.configs = {}  # 存储所有配置
        self.load_all_configs()
        
        # 托盘相关
        self.tray_icon = None
        self.is_minimized_to_tray = False
        
        self.setup_ui()
        self.load_config()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 源目录选择
        ttk.Label(main_frame, text="源目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.source_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="浏览", command=self.select_source_dir).grid(row=0, column=2, padx=5)
        
        # 目标目录选择
        ttk.Label(main_frame, text="目标目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.target_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="浏览", command=self.select_target_dir).grid(row=1, column=2, padx=5)
        
        # 同步模式选择
        ttk.Label(main_frame, text="同步模式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Radiobutton(mode_frame, text="单向同步", variable=self.sync_mode, value="单向同步").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="双向同步", variable=self.sync_mode, value="双向同步").pack(side=tk.LEFT, padx=20)
        
        # 文件过滤规则
        ttk.Label(main_frame, text="过滤规则:").grid(row=3, column=0, sticky=tk.W, pady=5)
        filter_frame = ttk.Frame(main_frame)
        filter_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(filter_frame, textvariable=self.filter_rules, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(filter_frame, text="?", command=self.show_filter_help, width=3).pack(side=tk.RIGHT, padx=5)
        
        # 配置管理
        ttk.Label(main_frame, text="配置管理:").grid(row=4, column=0, sticky=tk.W, pady=5)
        config_frame = ttk.Frame(main_frame)
        config_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 配置选择下拉框
        self.config_combobox = ttk.Combobox(config_frame, textvariable=self.current_config_name, 
                                           state="readonly", width=20)
        self.config_combobox.pack(side=tk.LEFT, padx=5)
        self.config_combobox.bind('<<ComboboxSelected>>', self.on_config_selected)
        
        # 配置管理按钮
        ttk.Button(config_frame, text="加载配置", command=self.load_selected_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(config_frame, text="保存配置", command=self.save_current_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(config_frame, text="另存为", command=self.save_config_as).pack(side=tk.LEFT, padx=2)
        ttk.Button(config_frame, text="删除配置", command=self.delete_config).pack(side=tk.LEFT, padx=2)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        ttk.Button(button_frame, text="开始同步", command=self.start_sync).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="停止同步", command=self.stop_sync).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="最小化到托盘", command=self.minimize_to_tray).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        ttk.Label(main_frame, text="同步进度:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 状态显示
        ttk.Label(main_frame, text="状态信息:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # 日志显示
        ttk.Label(main_frame, text="同步日志:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 配置网格权重
        main_frame.rowconfigure(9, weight=1)
        
    def select_source_dir(self):
        """选择源目录"""
        directory = filedialog.askdirectory(title="选择源目录")
        if directory:
            self.source_path.set(directory)
            
    def select_target_dir(self):
        """选择目标目录"""
        directory = filedialog.askdirectory(title="选择目标目录")
        if directory:
            self.target_path.set(directory)
            
    def show_filter_help(self):
        """显示过滤规则帮助"""
        help_text = """文件过滤规则使用说明：

1. 使用分号(;)分隔多个规则
2. 支持通配符：
   * 匹配任意字符
   ? 匹配单个字符
3. 示例：
   *.txt;*.doc - 只同步txt和doc文件
   !*.tmp;!*.log - 排除tmp和log文件
   folder1/*;folder2/* - 只同步特定文件夹

注意：以!开头表示排除规则"""
        messagebox.showinfo("过滤规则帮助", help_text)
        
    def start_sync(self):
        """开始同步"""
        if self.is_syncing:
            messagebox.showwarning("警告", "同步正在进行中")
            return
            
        if not self.source_path.get() or not self.target_path.get():
            messagebox.showerror("错误", "请选择源目录和目标目录")
            return
            
        if not os.path.exists(self.source_path.get()):
            messagebox.showerror("错误", "源目录不存在")
            return
            
        self.is_syncing = True
        self.status_label.config(text="同步中...")
        self.progress['value'] = 0
        
        # 在新线程中执行同步
        sync_thread = threading.Thread(target=self._sync_worker)
        sync_thread.daemon = True
        sync_thread.start()
        
    def _sync_worker(self):
        """同步工作线程"""
        try:
            # 配置同步参数
            config = {
                'source_path': self.source_path.get(),
                'target_path': self.target_path.get(),
                'sync_mode': self.sync_mode.get(),
                'filter_rules': self.filter_rules.get(),
                'progress_callback': self.update_progress,
                'log_callback': self.add_log
            }
            
            # 执行同步
            result = self.sync_core.sync_directories(config)
            
            # 更新UI
            self.root.after(0, self._sync_completed, result)
            
        except Exception as e:
            self.root.after(0, self._sync_error, str(e))
            
    def _sync_completed(self, result):
        """同步完成回调"""
        self.is_syncing = False
        self.status_label.config(text="同步完成")
        self.progress['value'] = 100
        self.add_log(f"同步完成: {result}")
        
    def _sync_error(self, error_msg):
        """同步错误回调"""
        self.is_syncing = False
        self.status_label.config(text="同步失败")
        self.add_log(f"同步失败: {error_msg}")
        messagebox.showerror("同步失败", error_msg)
        
    def stop_sync(self):
        """停止同步"""
        if self.is_syncing:
            self.sync_core.stop_sync()
            self.is_syncing = False
            self.status_label.config(text="已停止")
            self.add_log("用户停止同步")
        
    def update_progress(self, value):
        """更新进度条"""
        self.root.after(0, lambda: setattr(self.progress, 'value', value))
        
    def add_log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # 更新UI日志
        self.root.after(0, lambda: self._append_log(log_entry))
        
        # 写入日志文件
        self.logger.log(message)
        
    def _append_log(self, log_entry):
        """追加日志到文本框"""
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def load_all_configs(self):
        """加载所有配置"""
        try:
            # 先尝试加载多配置文件
            configs = self.utils.load_json_config(self.config_file)
            if configs and isinstance(configs, dict):
                self.configs = configs
            else:
                self.configs = {}
            
            # 如果多配置文件为空，尝试从旧的单配置文件迁移
            if not self.configs:
                old_config = self.utils.load_json_config(self.default_config_file)
                if old_config:
                    self.configs["默认配置"] = old_config
                    self.save_all_configs()  # 保存到新格式
            
            # 如果还是没有配置，创建默认配置
            if not self.configs:
                self.configs["默认配置"] = {
                    'source_path': '',
                    'target_path': '',
                    'sync_mode': '单向同步',
                    'filter_rules': ''
                }
            
            # 更新下拉框
            self.update_config_combobox()
            
            # 加载第一个配置
            if self.configs:
                first_config = list(self.configs.keys())[0]
                self.current_config_name.set(first_config)
                self.load_config_by_name(first_config)
                
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            self.configs = {"默认配置": {
                'source_path': '',
                'target_path': '',
                'sync_mode': '单向同步',
                'filter_rules': ''
            }}
            self.update_config_combobox()
    
    def save_all_configs(self):
        """保存所有配置到文件"""
        try:
            self.utils.save_json_config(self.config_file, self.configs)
            self.logger.info("所有配置保存成功")
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            raise e
    
    def update_config_combobox(self):
        """更新配置下拉框"""
        if hasattr(self, 'config_combobox'):
            config_names = list(self.configs.keys())
            self.config_combobox['values'] = config_names
    
    def load_config_by_name(self, config_name):
        """根据配置名加载配置"""
        if config_name in self.configs:
            config = self.configs[config_name]
            self.source_path.set(config.get('source_path', ''))
            self.target_path.set(config.get('target_path', ''))
            self.sync_mode.set(config.get('sync_mode', '单向同步'))
            self.filter_rules.set(config.get('filter_rules', ''))
            self.logger.info(f"配置 '{config_name}' 加载成功")
    
    def on_config_selected(self, event=None):
        """配置选择事件"""
        selected_config = self.current_config_name.get()
        if selected_config and selected_config in self.configs:
            self.load_config_by_name(selected_config)
    
    def load_selected_config(self):
        """加载选中的配置"""
        selected_config = self.current_config_name.get()
        if selected_config:
            self.load_config_by_name(selected_config)
            self.add_log(f"配置 '{selected_config}' 加载成功")
            messagebox.showinfo("成功", f"配置 '{selected_config}' 加载成功")
    
    def save_current_config(self):
        """保存当前配置"""
        try:
            config_name = self.current_config_name.get()
            if not config_name:
                messagebox.showerror("错误", "请选择或输入配置名称")
                return
            
            config = {
                'source_path': self.source_path.get(),
                'target_path': self.target_path.get(),
                'sync_mode': self.sync_mode.get(),
                'filter_rules': self.filter_rules.get()
            }
            
            self.configs[config_name] = config
            self.save_all_configs()
            self.update_config_combobox()
            
            self.add_log(f"配置 '{config_name}' 保存成功")
            messagebox.showinfo("成功", f"配置 '{config_name}' 保存成功")
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            self.add_log(f"保存配置失败: {e}")
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def save_config_as(self):
        """另存为新配置"""
        # 弹出对话框让用户输入新配置名
        new_name = simpledialog.askstring("另存为", "请输入新配置名称:")
        if new_name:
            if new_name in self.configs:
                if not messagebox.askyesno("确认", f"配置 '{new_name}' 已存在，是否覆盖？"):
                    return
            
            config = {
                'source_path': self.source_path.get(),
                'target_path': self.target_path.get(),
                'sync_mode': self.sync_mode.get(),
                'filter_rules': self.filter_rules.get()
            }
            
            self.configs[new_name] = config
            self.current_config_name.set(new_name)
            
            try:
                self.save_all_configs()
                self.update_config_combobox()
                self.add_log(f"配置 '{new_name}' 另存为成功")
                messagebox.showinfo("成功", f"配置 '{new_name}' 保存成功")
            except Exception as e:
                self.logger.error(f"保存配置失败: {e}")
                self.add_log(f"另存为配置失败: {e}")
                messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def delete_config(self):
        """删除配置"""
        config_name = self.current_config_name.get()
        if not config_name:
            messagebox.showerror("错误", "请选择要删除的配置")
            return
        
        if len(self.configs) <= 1:
            messagebox.showerror("错误", "至少需要保留一个配置")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除配置 '{config_name}' 吗？"):
            try:
                del self.configs[config_name]
                self.save_all_configs()
                self.update_config_combobox()
                
                # 选择第一个可用配置
                if self.configs:
                    first_config = list(self.configs.keys())[0]
                    self.current_config_name.set(first_config)
                    self.load_config_by_name(first_config)
                
                self.add_log(f"配置 '{config_name}' 删除成功")
                messagebox.showinfo("成功", f"配置 '{config_name}' 删除成功")
            except Exception as e:
                self.logger.error(f"删除配置失败: {e}")
                self.add_log(f"删除配置失败: {e}")
                messagebox.showerror("错误", f"删除配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        self.save_current_config()
            
    def load_config(self):
        """加载配置"""
        # 这个方法现在由load_all_configs处理
        pass
                
    def minimize_to_tray(self):
        """最小化到托盘"""
        self.root.withdraw()
        self.is_minimized_to_tray = True
        self.create_tray_icon()
        
    def create_default_tray_icon(self):
        """创建默认托盘图标"""
        from PIL import ImageDraw, ImageFont
        
        # 创建32x32的图标
        image = Image.new('RGBA', (32, 32), (0, 0, 0, 0))  # 透明背景
        draw = ImageDraw.Draw(image)
        
        # 绘制蓝色圆形背景
        draw.ellipse([2, 2, 30, 30], fill=(0, 120, 215, 255), outline=(255, 255, 255, 255), width=1)
        
        # 绘制同步箭头图标
        # 上箭头
        draw.polygon([(16, 8), (12, 12), (14, 12), (14, 16), (18, 16), (18, 12), (20, 12)], fill=(255, 255, 255, 255))
        # 下箭头
        draw.polygon([(16, 24), (20, 20), (18, 20), (18, 16), (14, 16), (14, 20), (12, 20)], fill=(255, 255, 255, 255))
        
        return image
        
    def create_tray_icon(self):
        """创建托盘图标"""
        try:
            # 创建托盘图标
            image = self.create_default_tray_icon()
            
            # 如果在开发环境中，尝试加载自定义图标
            if not getattr(sys, 'frozen', False):
                icon_path = None
                possible_paths = ["assets/icon.ico", "assets/icon.png", "icon.ico"]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        try:
                            image = Image.open(path)
                            image = image.resize((32, 32), Image.Resampling.LANCZOS)
                            break
                        except Exception:
                            continue
                
            menu = pystray.Menu(
                pystray.MenuItem("显示窗口", self.show_window, default=True),
                pystray.MenuItem("开始同步", self.tray_start_sync),
                pystray.MenuItem("退出", self.quit_app)
            )
            
            # 创建托盘图标，设置左键点击事件
            self.tray_icon = pystray.Icon(
                "SyncTool", 
                image, 
                "文件同步工具", 
                menu,
                on_click=self.on_tray_click  # 添加左键点击事件
            )
            
            # 在新线程中运行托盘图标
            self.tray_thread = threading.Thread(target=self.tray_icon.run)
            self.tray_thread.daemon = True
            self.tray_thread.start()
            
            self.add_log("托盘图标创建成功")
            
        except Exception as e:
            self.add_log(f"创建托盘图标失败: {e}")
            print(f"托盘图标创建失败: {e}")  # 调试信息
            
    def on_tray_click(self, icon, button, time):
        """托盘图标点击事件"""
        if button == pystray.MouseButton.LEFT:
            # 左键点击直接显示窗口
            self.show_window()
    
    def show_window(self, icon=None, item=None):
        """显示窗口"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()  # 强制获取焦点
        self.is_minimized_to_tray = False
        
        # 停止托盘图标和线程
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        
        # 等待托盘线程结束
        if hasattr(self, 'tray_thread') and self.tray_thread and self.tray_thread.is_alive():
            try:
                self.tray_thread.join(timeout=1)  # 最多等待1秒
            except Exception:
                pass
            
    def tray_start_sync(self, icon=None, item=None):
        """从托盘启动同步"""
        if not self.is_syncing:
            self.start_sync()
            
    def quit_app(self, icon=None, item=None):
        """退出应用"""
        try:
            # 停止同步进程
            if hasattr(self, 'is_syncing') and self.is_syncing:
                self.is_syncing = False
            
            # 停止托盘图标
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.stop()
                self.tray_icon = None
            
            # 等待托盘线程结束
            if hasattr(self, 'tray_thread') and self.tray_thread and self.tray_thread.is_alive():
                try:
                    self.tray_thread.join(timeout=2)  # 最多等待2秒
                except Exception:
                    pass
            
            # 记录退出日志
            if hasattr(self, 'logger'):
                self.logger.info("程序正在退出...")
            
            # 强制退出主循环
            if hasattr(self, 'root') and self.root:
                self.root.quit()
                self.root.destroy()
            
            # 强制退出进程
            import sys
            sys.exit(0)
            
        except Exception as e:
            print(f"退出时发生错误: {e}")
            # 强制退出
            import os
            os._exit(0)
        
    def on_closing(self):
        """窗口关闭事件"""
        try:
            if messagebox.askokcancel("退出", "确定要退出程序吗？"):
                self.quit_app()
        except Exception:
            # 如果对话框失败，直接退出
            self.quit_app()
            
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SyncToolGUI()
    app.run()