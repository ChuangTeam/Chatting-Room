import socket


class Client:
    def __init__(self):
        # 1.创建socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def connect(self, ip='127.0.0.1', port=7788):
        # 2. 链接服务器
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = (ip, port)
        self.tcp_socket.connect(self.server_addr)
        self.tcp_socket.setblocking(False)
        self.tcp_socket.settimeout(0.0)

    def send_data(self, massage):
        # print(massage)
        self.tcp_socket.send(massage)

    def close(self):
        # 4. 关闭套接字
        self.tcp_socket.shutdown(socket.SHUT_RDWR)
        self.tcp_socket.close()
    def listener(self):
        # 接收对方发送过来的数据
        try:
            recv_data = self.tcp_socket.recv(1024)  # 接收1024个字节
            if recv_data:
                # print('接收到的数据为:', recv_data.decode('gb18030'))
                return recv_data
        except Exception as e:  # 无连接pass继续查询
            pass
