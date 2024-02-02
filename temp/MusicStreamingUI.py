import tkinter as tk
import sys
import socket
import pyaudio
import threading


class MusicStreaming:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True, frames_per_buffer=1024)

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("MusicStreaming")

        self.root.protocol("WM_DELETE_WINDOW", self.delete_window)

        width = 367
        height = 222
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(geometry)

        self.root.resizable(width=False, height=False)

        # 创建连接按钮
        self.connect_button = tk.Button(self.root, text="Connect",
                                        command=self.connect)

        # 创建断开连接按钮
        self.close_button = tk.Button(self.root, text="Close",
                                      command=self.close)

        # 创建服务器ip输入框
        self.server_ip_entry = tk.Entry(self.root, bd=1)
        # 创建服务器端口地址
        self.server_port_entry = tk.Entry(self.root, bd=1)

        self.state = tk.StringVar()
        self.state.set("未连接")
        self.state_label = tk.Label(self.root, textvariable=self.state, anchor="center")

        self.connect_button.place(x=254, y=61, width=60, height=39)
        self.close_button.place(x=254, y=119, width=60, height=39)

        self.state_label.place(x=183, y=17, width=200, height=30)

        tk.Label(self.root, text='服务器IP', anchor="w").place(x=36, y=23, width=50, height=30)
        self.server_ip_entry.place(x=36, y=63, width=150, height=30)
        tk.Label(self.root, text='服务器端口', anchor="w").place(x=36, y=109, width=50, height=30)
        self.server_port_entry.place(x=36, y=149, width=150, height=30)

        # 设置初始值
        self.server_ip_entry.insert(0, 'frp-fan.top')
        self.server_port_entry.insert(0, '47359')

    def delete_window(self):
        self.stream.stop_stream()
        self.stream.close()
        self.s.close()
        self.root.destroy()
        sys.exit(0)

    def mainloop(self):
        # 运行主循环
        self.root.mainloop()

    def close(self):
        self.connect_button.config(state='normal')
        self.stream.stop_stream()
        self.stream.close()
        self.s.close()

    def connect(self):
        self.state.set('正在尝试连接到音乐频道')
        self.s.connect((self.server_ip_entry.get(), int(self.server_port_entry.get())))
        self.state.set('音乐频道已连接')
        self.server_ip_entry.config(state='readonly')
        self.server_port_entry.config(state='readonly')

        th = threading.Thread(target=self.music_streaming)
        th.daemon = True  # 守护线程
        th.start()

    def music_streaming(self):
        while True:
            data = self.s.recv(1024)
            self.stream.write(data)




