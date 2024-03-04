import socket
import time
from threading import Thread


class MusicServerProcess:
    def __init__(self, ipaddr, port, num):
        self.ipaddr = ipaddr
        self.port = port
        self.num = num
        self.conn_list = []
        self.addr_list = []
        self.name_dict = {}

    # 服务端的数据接收，在调用时使用多进程
    def server_link(self, conn, addr):
        while True:
            try:
                message = conn.recv(1024)
                try:
                    m = message.decode("gb18030")
                    if m == 'quit':
                        break
                except:
                    try:
                        self.forward_message(conn, addr, message)
                    except:
                        pass
            except:
                break
        print(addr, '离开了语音频道')
        self.forward_message(conn, addr, f'{addr}离开了语音频道\n')
        self.addr_list.remove(addr)
        self.conn_list.remove(conn)

        conn.close()

    def forward_message(self, sender, addr, message):
        addr_index = -1

        for i, v in enumerate(self.addr_list):
            if v == addr:
                addr_index = i
        for i in range(len(self.addr_list)):
            if i != addr_index:
                conn = self.conn_list[i]
                conn.send(message)
                # print('from', self.addr_list[addr_index], 'to', self.addr_list[i])

    # 服务端的启动程序
    def server_start(self):
        s_pro = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 操作系统会在服务器socket被关闭或服务器进程终止后马上释放该服务器的端口
        s_pro.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_pro.bind((self.ipaddr, self.port))
        s_pro.listen(self.num)
        print('语音频道等待连接...')
        while True:
            conn, addr = s_pro.accept()

            self.addr_list.append(addr)
            self.conn_list.append(conn)

            print("语音频道连接到", addr)
            # 启动多进程实现多连接
            p = Thread(target=self.server_link, args=(conn, addr))
            p.start()


class ChatServerProcess:
    def __init__(self, ipaddr, port, num):

        self.conn_list = []
        self.addr_list = []

        self.ipaddr = ipaddr
        self.port = port
        self.num = num

    def forward_message(self, sender, addr, message):
        addr_index = -1
        for i, v in enumerate(self.addr_list):
            if v == addr:
                addr_index = i

        for i in range(len(self.addr_list)):
            if i != addr_index:
                conn = self.conn_list[i]
                conn.send(message.encode('gb18030'))
                # print('from', self.addr_list[addr_index], 'to', self.addr_list[i])

    # 服务端的数据接收，在调用时使用多进程
    def server_link(self, conn, addr):
        while True:
            try:
                message = conn.recv(1024).decode('gb18030')
                if message == '':
                    break
                # print(addr, message)
                with open('history.txt', 'a+') as history:
                    history.write(message)
                    history.write(time.ctime())
                    history.write('\n')
                self.forward_message(conn, addr, message)
            except Exception:
                pass
        print(addr, '断开了连接')
        self.forward_message(conn, addr, f'{self.name_dict[addr]}断开了连接\n')
        self.conn_list.remove(conn)
        self.addr_list.remove(addr)
        conn.close()

    # 服务端的启动程序
    def server_start(self):
        s_pro = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 操作系统会在服务器socket被关闭或服务器进程终止后马上释放该服务器的端口
        s_pro.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_pro.bind((self.ipaddr, self.port))
        s_pro.listen(self.num)
        print('聊天频道等待连接...')
        while True:
            conn, addr = s_pro.accept()
            conn.send('成功连接到聊天频道！\n'.encode("gb18030"))
            print("聊天频道连接到", addr)
            with open('history.txt', 'a+') as history:
                history.write(str(addr) + 'Connect' + '\n')
                history.write(time.ctime())
                history.write('\n')

            user_name = conn.recv(1024)
            user_name = user_name.decode('gb18030', errors='ignore')
            # print(user_name)
            # 启动多进程实现多连接
            self.conn_list.append(conn)
            self.addr_list.append(addr)
            print(f'{user_name}进入频道了\n')
            self.forward_message(conn, addr, f'{user_name}进入频道了\n')
            self.name_dict[addr] = user_name
            # print(self.addr_list)
            p = Thread(target=self.server_link, args=(conn, addr))
            p.start()
