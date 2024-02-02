import tkinter as tk
import sys
from win11toast import toast
from icon import Icon
import base64
import os
import pyaudio
import threading
from Web.client import Client

class ChatRoom:
    def __init__(self):
        self.chat_client = Client()
        self.voice_client = Client()

        self.is_voice_open = False

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("Chatting Room")

        self.root.protocol("WM_DELETE_WINDOW", self.delete_window)

        width = 600
        height = 500
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)

        self.root.geometry(geometry)

        self.root.resizable(width=False, height=False)
        # self.root.iconphoto(True, tk.PhotoImage(file='ico.png'))

        with open('tmp.ico', 'wb') as tmp:
            tmp.write(base64.b64decode(Icon().img))
        self.root.iconbitmap('tmp.ico')
        os.remove('tmp.ico')


        # 创建聊天记录框
        self.chat_log = tk.Text(self.root, bd=1, height=20, width=50)
        self.chat_log.config(state=tk.DISABLED)

        # 创建文本输入框
        self.entry_field = tk.Text(self.root, bd=1, wrap=tk.WORD)
        self.entry_field.bind("<Return>", lambda event: self.send_message())

        # 创建发送按钮
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)

        # 创建连接按钮
        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_server)

        # 创建关闭连接按钮
        self.close_client_button = tk.Button(self.root, text="Close", command=self.close_connect)

        # 创建语音连接频道
        self.open_voice_channel_button = tk.Button(self.root, text='Voice\nChannel',
                                                   command=self.open_voice_channel_window)

        # 创建用户名输入框
        self.user_name_field = tk.Entry(self.root, bd=1)

        # 创建接收端ip地址
        self.client_field = tk.Entry(self.root, bd=1)
        self.client_port_field = tk.Entry(self.root, bd=1)

        # 设置布局
        self.chat_log.place(x=167, y=10, width=426, height=339)
        self.entry_field.place(x=167, y=373, width=353, height=100)
        self.send_button.place(x=536, y=372, width=57, height=102)
        tk.Label(self.root, text='用户名：', anchor="w").place(x=20, y=50, width=66, height=30)
        self.user_name_field.place(x=19, y=83, width=130, height=30)
        tk.Label(self.root, text='服务器IP：', anchor="w").place(x=20, y=127, width=66, height=30)
        self.client_field.place(x=19, y=160, width=130, height=30)
        tk.Label(self.root, text='端口号：', anchor="w").place(x=20, y=204, width=75, height=30)
        self.client_port_field.place(x=20, y=234, width=130, height=30)
        self.connect_button.place(x=20, y=283, width=66, height=30)
        self.close_client_button.place(x=98, y=283, width=50, height=30)
        self.open_voice_channel_button.place(x=51, y=353)

        # 设置初始值
        self.client_field.insert(0, '118.178.134.221')
        # self.client_field.insert(0, '127.0.0.1')
        self.client_port_field.insert(0, '7711')

    def open_voice_channel_window(self):
        self.voice_window = tk.Toplevel(self.root)
        self.voice_window.title("MusicStreaming")

        self.voice_window.protocol("WM_DELETE_WINDOW", self.voice_channel_delete_window)

        width = 367
        height = 222
        screenwidth = self.voice_window.winfo_screenwidth()
        screenheight = self.voice_window.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.voice_window.geometry(geometry)

        self.voice_window.resizable(width=False, height=False)

        # 创建连接按钮
        self.connect_button = tk.Button(self.voice_window, text="Connect",
                                        command=self.voice_channel_connect)

        # 创建断开连接按钮
        self.close_button = tk.Button(self.voice_window, text="Close",
                                      command=self.voice_channel_close)

        # 创建服务器ip输入框
        self.server_ip_entry = tk.Entry(self.voice_window, bd=1)
        # 创建服务器端口输入框
        self.server_port_entry = tk.Entry(self.voice_window, bd=1)
        # 创建音轨输入框
        self.device_idx_entry = tk.Entry(self.voice_window, bd=1)

        self.state = tk.StringVar()
        self.state.set("未连接")
        state_label = tk.Label(self.voice_window, textvariable=self.state, anchor="center")
        state_label.place(x=183, y=17, width=200, height=30)

        self.connect_button.place(x=220, y=61, width=60, height=39)
        self.close_button.place(x=290, y=61, width=60, height=39)

        tk.Label(self.voice_window, text='服务器IP', anchor="w").place(x=36, y=0, width=50, height=30)
        self.server_ip_entry.place(x=36, y=30, width=150, height=30)
        tk.Label(self.voice_window, text='服务器端口', anchor="w").place(x=36, y=60, width=100, height=30)
        self.server_port_entry.place(x=36, y=90, width=150, height=30)
        tk.Label(self.voice_window, text='音轨编号', anchor="w").place(x=36, y=120, width=50, height=30)
        self.device_idx_entry.place(x=36, y=150, width=150, height=30)

        # 设置初始值
        self.server_ip_entry.insert(0, '118.178.134.221')
        # self.server_ip_entry.insert(0, '127.0.0.1')
        self.server_port_entry.insert(0, '7712')
        self.device_idx_entry.insert(0, '3')

    def voice_channel_delete_window(self):
        try:
            self.voice_client.close()
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.output_stream.stop_stream()
            self.output_stream.close()
        except:
            pass
        self.is_voice_open = False

        self.voice_window.destroy()

    def voice_channel_connect(self):
        self.state.set('正在尝试连接到音乐频道')
        self.p = pyaudio.PyAudio()
        self.input_stream = self.p.open(format=pyaudio.paInt16,
                                        input_device_index=int(self.device_idx_entry.get()),
                                        channels=2,
                                        rate=44100,
                                        input=True,
                                        frames_per_buffer=1024)
        self.output_stream = self.p.open(format=pyaudio.paInt16,
                                         channels=2,
                                         rate=44100,
                                         output=True,
                                         frames_per_buffer=1024)

        self.voice_client.connect(self.server_ip_entry.get(), int(self.server_port_entry.get()))
        self.state.set('音乐频道已连接')
        self.is_voice_open = True
        self.server_ip_entry.config(state='readonly')
        self.server_port_entry.config(state='readonly')

        input_t = threading.Thread(target=self.recv_stream)
        input_t.daemon = True  # 守护线程
        output_t = threading.Thread(target=self.send_stream)
        output_t.daemon = True  # 守护线程

        input_t.start()
        output_t.start()

    def voice_channel_close(self):
        try:
            self.voice_client.send_data('quit'.encode("gb18030"))
        except:
            pass
        self.connect_button.config(state='normal')
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.output_stream.stop_stream()
        self.output_stream.close()

    def recv_stream(self):
        while self.is_voice_open:
            data = self.voice_client.listener()
            if data:
                self.output_stream.write(data)

    def send_stream(self):
        while self.is_voice_open:
            data = self.input_stream.read(1024)
            self.voice_client.send_data(data)


    def delete_window(self):
        try:
            try:
                try:
                    self.voice_client.send_data('quit'.encode("gb18030"))
                    self.voice_client.close()
                except:
                    pass
                self.is_voice_open = False
                self.input_stream.stop_stream()
                self.input_stream.close()
                self.output_stream.stop_stream()
                self.output_stream.close()
                self.voice_window.destroy()
            except:
                pass
            self.chat_client.send_data(''.encode("gb18030"))
            self.chat_client.close()
            self.root.destroy()
            sys.exit(0)
        except:
            sys.exit(0)



    def connect_server(self):
        if self.user_name_field.get() != '':
            self.client_field.config(state='readonly')
            self.client_port_field.config(state='readonly')
            self.user_name_field.config(state='readonly')
            self.root.after(3000, self.receive_message)
            self.chat_client.connect(ip=self.client_field.get(), port=int(self.client_port_field.get()))
            self.chat_client.send_data(str(self.user_name_field.get()).encode("gb18030"))

    def close_connect(self):
        self.chat_client.send_data(''.encode("gb18030"))

    def send_message(self):
        msg = self.entry_field.get('0.0', 'end')
        message = self.user_name_field.get() + ': ' + msg
        self.entry_field.delete(0.0, tk.END)
        if msg:
            self.chat_client.send_data(message.encode("gb18030"))
            self._add_message(message)
        return 'break'

    def receive_message(self):
        received_msg = self.chat_client.listener()
        if received_msg:
            received_msg = received_msg.decode('gb18030')
            # print(self.root.state())
            if ':' in received_msg and self.root.state() == 'iconic':
                sender = received_msg[:received_msg.find(': ')]
                message = received_msg[received_msg.find(': ')+1:]
                self.send_notice(sender, message)
            self._add_message(received_msg)
        self.root.after(200, self.receive_message)

    def _add_message(self, message):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, str(message))
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def send_notice(self, title, msg):
        toast(title, msg)

    def mainloop(self):
        # 运行主循环
        self.root.mainloop()


if __name__ == '__main__':
    root = ChatRoom()
    root.mainloop()
