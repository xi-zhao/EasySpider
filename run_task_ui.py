import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# 任务目录
TASK_DIR = os.path.join(os.path.dirname(__file__), 'ElectronJS', 'execution_instances')

# Windows下EasySpider主目录
WORK_DIR = r'D:\Program Files\EasySpider_Windows_x64'
# exe路径
EXE_PATH = os.path.join(WORK_DIR, r'EasySpider\resources\app\chrome_win64\easyspider_executestage.exe')


def list_json_files():
    if not os.path.exists(TASK_DIR):
        return []
    return [f for f in os.listdir(TASK_DIR) if f.endswith('.json')]

def run_task(task_file, log_widget, btn):
    btn.config(state=tk.DISABLED)
    log_widget.delete(1.0, tk.END)
    # 提取 id
    task_id = os.path.splitext(task_file)[0]
    # 拼接命令
    cmd = [
        EXE_PATH,
        '--ids', f'[{task_id}]',
        '--user_data', '1',
        '--server_address', 'http://localhost:8074',
        '--config_folder', WORK_DIR,
        '--headless', '0',
        '--read_type', 'local',
        '--config_file_name', 'config.json',
        '--saved_file_name',
        '--keyboard', '0'
    ]
    process = subprocess.Popen(
        cmd,
        cwd=WORK_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True
    )
    def read_log():
        for line in process.stdout:
            log_widget.insert(tk.END, line)
            log_widget.see(tk.END)
        process.wait()
        btn.config(state=tk.NORMAL)
        messagebox.showinfo("完成", "任务执行完成！")
    threading.Thread(target=read_log, daemon=True).start()

def main():
    root = tk.Tk()
    root.title("EasySpider 任务执行器（Windows专用）")
    root.geometry("700x500")

    tk.Label(root, text="选择任务文件：", font=("Arial", 12)).pack(pady=10)
    task_var = tk.StringVar()
    task_list = list_json_files()
    combo = ttk.Combobox(root, textvariable=task_var, values=task_list, state="readonly", width=60)
    combo.pack()
    if task_list:
        combo.current(0)

    log = scrolledtext.ScrolledText(root, width=80, height=20, font=("Consolas", 10))
    log.pack(pady=10)

    btn = tk.Button(root, text="执行", font=("Arial", 12), width=10,
                    command=lambda: run_task(task_var.get(), log, btn))
    btn.pack()

    root.mainloop()

if __name__ == '__main__':
    main() 