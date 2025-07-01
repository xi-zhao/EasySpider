import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json

# ...existing code...
# 任务目录
TASK_DIR = os.path.join(os.path.dirname(__file__), 'execution_instances')
# ...existing code...

# Windows下EasySpider主目录
WORK_DIR = r'D:\Program Files\EasySpider_Windows_x64'
# exe路径
EXE_PATH = os.path.join(WORK_DIR, r'EasySpider\resources\app\chrome_win64\easyspider_executestage.exe')

def list_json_files():
    if not os.path.exists(TASK_DIR):
        return []
    return [f for f in os.listdir(TASK_DIR) if f.endswith('.json')]

def show_graph_id1_links(task_file, label_widget, links_widget):
    try:
        with open(os.path.join(TASK_DIR, task_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        node1 = None
        for node in data.get('graph', []):
            if node.get('id') == 1:
                node1 = node
                break
        if node1:
            label_widget.config(text=f"graph中id=1节点: {node1.get('title', '')}")
            links = node1.get('parameters', {}).get('links', '')
            links_widget.config(state=tk.NORMAL)
            links_widget.delete(1.0, tk.END)
            links_widget.insert(tk.END, links)
            links_widget.config(state=tk.NORMAL)
        else:
            label_widget.config(text="未找到graph中id=1的节点")
            links_widget.config(state=tk.NORMAL)
            links_widget.delete(1.0, tk.END)
            links_widget.config(state=tk.NORMAL)
    except Exception as e:
        label_widget.config(text=f"解析出错: {e}")
        links_widget.config(state=tk.NORMAL)
        links_widget.delete(1.0, tk.END)
        links_widget.config(state=tk.NORMAL)

def save_links_to_json(task_file, links_widget, label_widget):
    try:
        json_path = os.path.join(TASK_DIR, task_file)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        node1 = None
        for node in data.get('graph', []):
            if node.get('id') == 1:
                node1 = node
                break
        if node1:
            new_links = links_widget.get(1.0, tk.END).strip()
            node1.setdefault('parameters', {})['links'] = new_links
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            label_widget.config(text="保存成功！")
        else:
            label_widget.config(text="未找到graph中id=1的节点，无法保存")
    except Exception as e:
        label_widget.config(text=f"保存出错: {e}")

def run_task(task_file, log_widget, btn):
    btn.config(state=tk.DISABLED)
    log_widget.delete(1.0, tk.END)
    # 提取 id
    task_id = os.path.splitext(task_file)[0]
    # 构造 exe 路径和参数列表
    exe_path = os.path.join(WORK_DIR, r'EasySpider\resources\app\chrome_win64\easyspider_executestage.exe')
    exe_path = exe_path.replace('/', '\\')
    cmd = [
        exe_path,
        '--ids', f'[{task_id}]',
        '--user_data', '1',
        '--server_address', 'http://localhost:8074',
        '--config_folder', WORK_DIR + '\\',
        '--headless', '0',
        '--read_type', 'local',
        '--config_file_name', 'config.json',
        '--saved_file_name',  # 无参 flag
        '--keyboard', '0'
    ]
    print('CMD参数：', cmd)
    try:
        result = subprocess.run(
            cmd,
            cwd=WORK_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print('STDOUT:', result.stdout)
        print('STDERR:', result.stderr)
        log_widget.insert(tk.END, result.stdout)
        log_widget.see(tk.END)
        messagebox.showinfo('完成', '任务执行完成！')
    except Exception as e:
        log_widget.insert(tk.END, f'执行出错: {e}\n')
    btn.config(state=tk.NORMAL)

def on_task_select(event, label_widget, links_widget, combo):
    task_file = combo.get()
    show_graph_id1_links(task_file, label_widget, links_widget)

def main():
    root = tk.Tk()
    root.title("标讯助手")
    root.geometry("800x600")

    tk.Label(root, text="选择任务文件：", font=("Arial", 12)).pack(pady=10)
    task_var = tk.StringVar()
    task_list = list_json_files()
    combo = ttk.Combobox(root, textvariable=task_var, values=task_list, state="readonly", width=60)
    combo.pack()
    if task_list:
        combo.current(0)

    # graph id=1 节点标题
    node1_label = tk.Label(root, text="", font=("Arial", 11, "bold"))
    node1_label.pack(pady=5)
    # links内容（可编辑）
    links_text = tk.Text(root, width=90, height=4, font=("Consolas", 10), state=tk.NORMAL)
    links_text.pack(pady=2)
    # 保存按钮
    save_btn = tk.Button(root, text="保存links", font=("Arial", 10),
                         command=lambda: save_links_to_json(combo.get(), links_text, node1_label))
    save_btn.pack(pady=2)

    # 任务选择事件
    combo.bind('<<ComboboxSelected>>', lambda e: on_task_select(e, node1_label, links_text, combo))
    # 初始显示
    if task_list:
        show_graph_id1_links(task_list[0], node1_label, links_text)

    log = scrolledtext.ScrolledText(root, width=100, height=20, font=("Consolas", 10))
    log.pack(pady=10)

    btn = tk.Button(root, text="执行", font=("Arial", 12), width=10,
                    command=lambda: run_task(task_var.get(), log, btn))
    btn.pack()

    root.mainloop()

if __name__ == '__main__':
    main() 