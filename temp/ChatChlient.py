import socket
from multiprocessing import Process, freeze_support
import time


def recv_message(s):
    s.setblocking(False)
    s.settimeout(0.0)
    while True:
        try:
            data = s.recv(1024)
            print(data.decode('gbk'))
        except:
            pass
    s.close()


def chatClient(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('正在尝试连接到聊天频道...')
    s.connect((host, port))
    p = Process(target=recv_message, args=(s,))
    p.start()
    time.sleep(0.5)
    while True:
        message = input()
        s.send(message.encode('gbk'))
    # s.close()


if __name__ == '__main__':
    freeze_support()
    chatClient(port=47357, host='frp-fan.top')
    # chatClient(host='127.0.0.1', port=7711)

