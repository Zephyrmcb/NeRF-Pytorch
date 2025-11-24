
import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import subprocess
import threading
from queue import Queue
import time
import cv2


class NeRFGUI:
    def __init__(self, master):
        self.master = master
        self.config_file = ''
        master.title("NeRF Training Pipeline")
        master.geometry("1000x800")

        self.video_playing = False
        self.current_video = None
        self.video_thread = None

        # 创建主容器
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.main_frame.columnconfigure(0, weight=1)
        for i in range(4):
            self.main_frame.rowconfigure(i, weight=1)

        # 文件上传部分
        self.create_upload_section()
        # 图片转换部分
        self.create_conversion_section()
        # 训练配置部分
        self.create_training_section()
        # 实时监测部分
        self.create_monitor_section()

        # 日志队列
        self.log_queue = Queue()
        self.video_files = []

        # 启动日志监测
        self.monitor_running = True
        threading.Thread(target=self.monitor_logs, daemon=True).start()
        self.update_ui()

    def create_upload_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="文件上传")
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        frame.columnconfigure(0, weight=1)

        self.upload_btn = ttk.Button(frame, text="选择上传文件夹", command=self.select_folder)
        self.upload_btn.grid(row=0, column=0, pady=5, sticky="ew")

        self.upload_label = ttk.Label(frame, text="未选择文件夹")
        self.upload_label.grid(row=1, column=0, pady=5, sticky="ew")

        # self.process_btn = ttk.Button(frame, text="处理图片", command=self.process_images)
        # self.process_btn.grid(row=2, column=0, pady=5, sticky="ew")


    # def process_images(self):
    #     if not hasattr(self, 'input_folder'):
    #         self.log_queue.put("请先选择上传文件夹！")
    #         return
        
    #     threading.Thread(target=self.run_processing_commands).start()

    # def run_processing_commands(self):
    #     rt = (self.input_folder).split('/')[-1]
    #     lt = rt.split('//')[0]
    #     commands = [
    #         "cd LLFF-master",
    #         "conda activate tensorflow",
    #         f"python imgs2poses.py {rt}",
    #         "conda deactivate tensorflow",
    #         "cd ..",
    #         "conda activate nerf"
    #     ]

    #     try:
    #         self.log_queue.put("开始处理图片...")
            
    #         for cmd in commands:
    #             self.log_queue.put(f"执行命令: {cmd}")
                
    #             if cmd.startswith("cd "):
    #                 # 处理目录切换
    #                 os.chdir(cmd[3:])
    #                 self.log_queue.put(f"切换到目录: {os.getcwd()}")
    #             elif cmd.startswith("conda "):
    #                 # 处理conda命令
    #                 process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #                 while True:
    #                     output = process.stdout.readline()
    #                     if not output and process.poll() is not None:
    #                         break
    #                     if output:
    #                         self.log_queue.put(output.strip().decode('utf-8', errors='replace'))
    #                 if process.returncode != 0:
    #                     raise Exception(f"命令执行失败: {cmd}")
    #             else:
    #                 # 处理其他命令
    #                 process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #                 while True:
    #                     output = process.stdout.readline()
    #                     if not output and process.poll() is not None:
    #                         break
    #                     if output:
    #                         self.log_queue.put(output.strip().decode('utf-8', errors='replace'))
    #                 if process.returncode != 0:
    #                     raise Exception(f"命令执行失败: {cmd}")
                
    #             self.log_queue.put(f"命令 {cmd} 执行完成")
            
    #         self.log_queue.put("所有命令执行完成！")
    #     except Exception as e:
    #         self.log_queue.put(f"处理错误: {str(e)}")

    def create_conversion_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="图片转化")
        frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        frame.columnconfigure(0, weight=1)

        self.convert_btn = ttk.Button(frame, text="开始转换", command=self.start_conversion)
        self.convert_btn.grid(row=0, column=0, pady=5, sticky="ew")

        self.convert_status = ttk.Label(frame, text="等待转换")
        self.convert_status.grid(row=1, column=0, pady=5, sticky="ew")

    def create_training_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="训练配置")
        frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="配置文件:").grid(row=0, column=0, sticky="w")
        self.config_entry = ttk.Entry(frame)
        self.config_entry.grid(row=0, column=1, padx=5, sticky="ew")

        self.train_btn = ttk.Button(frame, text="开始训练", command=self.start_training)
        self.train_btn.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        self.train_status = ttk.Label(frame, text="准备训练")
        self.train_status.grid(row=2, column=0, columnspan=2, sticky="ew")

    def create_monitor_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="实时监测")
        frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # 视频显示区域
        self.video_canvas = tk.Canvas(frame, bg='black')
        self.video_canvas.grid(row=0, column=0, sticky="nsew", pady=5)

        # 控制按钮
        control_frame = ttk.Frame(frame)
        control_frame.grid(row=1, column=0, sticky="ew")

        self.play_btn = ttk.Button(control_frame, text="播放", command=self.toggle_video)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        self.video_label = ttk.Label(control_frame, text="当前无视频")
        self.video_label.pack(side=tk.LEFT, expand=True)

        # 日志显示区域
        self.log_text = tk.Text(frame, height=8)
        self.log_text.grid(row=2, column=0, sticky="nsew", pady=5)

        # 配置权重
        frame.rowconfigure(0, weight=3)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

    def toggle_video(self):
        if self.video_playing:
            self.video_playing = False
            self.play_btn.config(text="播放")
        else:
            if self.current_video:
                self.video_playing = True
                self.play_btn.config(text="暂停")
                self.video_thread = threading.Thread(target=self.update_video_frame, daemon=True)
                self.video_thread.start()

    def update_video_frame(self):
        print(f"尝试打开视频文件: {self.current_video}")  # 输出视频文件路径
        cap = cv2.VideoCapture(self.current_video)
        if not cap.isOpened():
            print(f"无法打开视频文件: {self.current_video}")  # 输出无法打开的提示
        fps = cap.get(cv2.CAP_PROP_FPS)

        while self.video_playing and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 转换颜色空间并调整大小
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = self.resize_image(img, self.video_canvas.winfo_width(),
                                    self.video_canvas.winfo_height())

            # 更新Canvas显示
            self.video_canvas.delete("all")
            self.video_img = ImageTk.PhotoImage(image=img)
            self.video_canvas.create_image(
                self.video_canvas.winfo_width() / 2,
                self.video_canvas.winfo_height() / 2,
                image=self.video_img,
                anchor=tk.CENTER
            )

            time.sleep(1 / fps)

        cap.release()
        self.video_playing = False
        self.play_btn.config(text="播放")

    def resize_image(self, img, max_width, max_height):
        original_width, original_height = img.size
        ratio = min(max_width / original_width, max_height / original_height)
        return img.resize((int(original_width * ratio), int(original_height * ratio)), Image.ANTIALIAS)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.upload_label.config(text=folder_path)
            self.input_folder = os.path.join(folder_path, "images")
            self.output_folder = os.path.join(folder_path, "images_8")

    def start_conversion(self):
        if not hasattr(self, 'input_folder'):
            self.log_queue.put("请先选择上传文件夹！")
            return

        threading.Thread(target=self.convert_images).start()

    def convert_images(self):
        try:
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            image_files = [f for f in os.listdir(self.input_folder)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

            for img_file in image_files:
                img_path = os.path.join(self.input_folder, img_file)
                output_path = os.path.join(self.output_folder, img_file)

                with Image.open(img_path) as img:
                    w, h = img.size
                    img.resize((w // 8, h // 8), Image.ANTIALIAS).save(output_path)

                self.log_queue.put(f"转换完成: {img_file}")

            self.log_queue.put("全部图片转换完成！")
        except Exception as e:
            self.log_queue.put(f"转换错误: {str(e)}")

    def start_training(self):
        config_file = self.config_entry.get()
        if not config_file:
            self.log_queue.put("请输入配置文件名称！")
            return
        self.config_file = config_file
        cmd = f"python -u run_nerf.py --config configs/{config_file}.txt"
        threading.Thread(target=self.run_training, args=(cmd,)).start()


    def run_training(self, cmd):
        try:
            self.log_queue.put("开始训练...")
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            while True:
                output = process.stdout.readline()
                if not output and process.poll() is not None:
                    break
                if output:
                    try:
                        # 尝试UTF-8解码
                        decoded_output = output.strip().decode('utf-8')
                    except UnicodeDecodeError:
                        # 使用替代编码处理错误字节
                        decoded_output = output.strip().decode('latin-1', errors='replace')
                    self.log_queue.put(decoded_output)

            self.log_queue.put("训练完成！")
        except Exception as e:
            self.log_queue.put(f"训练错误: {str(e)}")

    def monitor_logs(self):
        while self.monitor_running:
            if not self.config_file:  # 确保配置文件已设置
                time.sleep(1)
                continue
            log_dir = os.path.join("logs", self.config_file)
            if os.path.exists(log_dir):
                new_files = [os.path.join(log_dir, f) 
                            for f in os.listdir(log_dir) if f.endswith('.mp4')]
                if new_files != self.video_files:
                    self.video_files = new_files
                    self.current_video = new_files[-1] if new_files else None
                    # 使用 after 在主线程更新界面
                    self.master.after(0, self.update_video_label)
            time.sleep(1)
    def update_video_label(self):
        if self.current_video:
            self.video_label.config(text=f"当前视频: {os.path.basename(self.current_video)}")
        else:
            self.video_label.config(text="当前无视频")

    def update_ui(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
        self.master.after(100, self.update_ui)

    def on_close(self):
        self.monitor_running = False
        self.master.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    app = NeRFGUI(root)

    # 窗口自适应配置
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()