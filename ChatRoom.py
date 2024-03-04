import tkinter as tk
import sys
from win11toast import toast
from icon import Icon
import base64
import os
import pyaudio
import threading
from Web.client import Client
import configparser
from Web.audioTool import amplify_audio, create_head


class ChatRoom:
    def __init__(self):
        # 创建管理对象
        self.config = configparser.ConfigParser()  # 实例化一个对象
        # 读ini文件
        self.config.read('./config.ini', encoding="utf-8")  # python3
        items = self.config.items('login')

        self.init_user_name = items[0][1]
        self.init_ip = items[1][1]
        self.init_text_port = int(items[2][1])
        self.init_voice_port = int(items[3][1])
        self.init_track = items[4][1]

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

        with open('tmp.ico', 'wb') as tmp:
            tmp.write(base64.b64decode(Icon().img))
        self.root.iconbitmap('tmp.ico')
        os.remove('tmp.ico')

        self.event = threading.Event()

        # 顶部菜单栏
        self.menu = tk.Menu(self.root)

        self.menu_file = tk.Menu(self.menu, tearoff=0)
        self.menu_file.add_command(label='保存配置', command=self.save_config)
        self.menu_file.add_command(label='读取配置', command=self.import_config)

        # 设置菜单栏
        self.menu.add_cascade(label='文件', menu=self.menu_file)
        self.root.config(menu=self.menu)

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
        self.close_client_button = tk.Button(self.root, text="Close", command=self.close_button)

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
        # tk.Label(self.root, text='端口号：', anchor="w").place(x=20, y=204, width=75, height=30)
        # self.client_port_field.place(x=20, y=234, width=130, height=30)
        self.connect_button.place(x=20, y=283, width=66, height=30)
        self.close_client_button.place(x=98, y=283, width=50, height=30)
        # self.open_voice_channel_button.place(x=51, y=353)

        # 设置初始值
        self.user_name_field.insert(0, self.init_user_name)
        self.client_field.insert(0, self.init_ip)
        self.client_port_field.insert(0, self.init_text_port)

        # 音量变量
        self.volumeVar = tk.StringVar()

        # 创建连接按钮
        self.micro_state = tk.BooleanVar()
        self.micro_button = tk.Checkbutton(self.root, text="语音",
                                           variable=self.micro_state,
                                           command=self.micro_button_func)


        # 创建音轨输入框
        self.device_idx_entry = tk.Entry(self.root, bd=1)

        self.state = tk.StringVar()
        self.state.set("语音未连接")
        state_label = tk.Label(self.root, textvariable=self.state, anchor="center")
        state_label.place(x=5, y=17, width=150, height=30)

        self.micro_button.place(x=90, y=340, width=60, height=60)

        tk.Label(self.root, text='音轨编号', anchor="w").place(x=20, y=204, width=75, height=30)
        self.device_idx_entry.place(x=20, y=234, width=130, height=30)

        tk.Scale(self.root, label='音量',
                 from_=20, to=-20,
                 resolution=0.5, show=0,
                 variable=self.volumeVar
                 ).place(x=29, y=350)

        # 设置初始值
        # self.server_ip_entry.insert(0, self.init_ip)

        self.device_idx_entry.insert(0, self.init_track)

    def save_config(self):
        config = configparser.ConfigParser()
        config['login'] = {
            'user': self.user_name_field.get(),
            'ip': self.client_field.get(),
            'text_port': '7711',
            'voice_port': '7712',
            'track': self.device_idx_entry.get()
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def import_config(self):
        # 读ini文件
        self.config.read('./config.ini', encoding="utf-8")  # python3
        items = self.config.items('login')

        self.init_user_name = items[0][1]
        self.init_ip = items[1][1]
        self.init_text_port = items[2][1]
        self.init_voice_port = items[3][1]
        self.init_track = items[4][1]

    def voice_channel_connect(self):
        self.state.set('正在尝试连接到语音频道')
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

        self.voice_client.connect(self.client_field.get(), self.init_voice_port)
        self.state.set('语音频道已连接')
        self.is_voice_open = True
        self.client_field.config(state='readonly')
        self.device_idx_entry.config(state='readonly')
        self.input_t = threading.Thread(target=self.recv_stream, args=(self.event,))
        self.input_t.daemon = True  # 守护线程
        self.output_t = threading.Thread(target=self.send_stream, args=(self.event,))
        self.output_t.daemon = True  # 守护线程
        self.input_t.start()
        self.output_t.start()

    def voice_channel_close(self):
        self.client_field.config(state='normal')
        self.device_idx_entry.config(state='normal')
        try:
            self.voice_client.send_data('quit'.encode("gb18030"))
        except:
            pass
        self.voice_client.close()
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.output_stream.stop_stream()
        self.output_stream.close()
        self.state.set('语音未连接')

    def recv_stream(self, event):
        while self.is_voice_open:
            if event.is_set():
                break
            data = self.voice_client.listener()
            if data:
                wmv_data = create_head(data)
                wmv_data = amplify_audio(wmv_data, self.volumeVar.get())
                data = wmv_data[44:]
                self.output_stream.write(data)

    def send_stream(self, event):
        while self.is_voice_open:
            try:
                data = self.input_stream.read(1024)
                self.voice_client.send_data(data)
            except:
                if event.is_set():
                    break

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

    def close_button(self):
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
        except:
            pass
    def connect_server(self):
        if self.user_name_field.get() != '':
            self.client_field.config(state='readonly')
            self.client_port_field.config(state='readonly')
            self.user_name_field.config(state='readonly')
            self.root.after(3000, self.receive_message)
            self.chat_client.connect(ip=self.client_field.get(), port=int(self.client_port_field.get()))
            self.chat_client.send_data(str(self.user_name_field.get()).encode("gb18030"))

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
            if ':' in received_msg and self.root.state() == 'iconic':
                sender = received_msg[:received_msg.find(': ')]
                message = received_msg[received_msg.find(': ') + 1:]
                self.send_notice(sender, message)
            self._add_message(received_msg)
        self.root.after(200, self.receive_message)



    def micro_button_func(self):
        if self.micro_state.get():
            self.event.clear()
            self.voice_channel_connect()
        else:
            self.event.set()
            self.voice_channel_close()

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
