import socket
import pyaudio

def musicClient(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True, frames_per_buffer=1024)
    print('正在尝试连接到音乐频道...')
    s.connect((host, port))
    print('音乐频道已连接')
    while True:
        data = s.recv(1024)
        stream.write(data)
    stream.stop_stream()
    stream.close()
    s.close()


if __name__ == '__main__':
    musicClient(port=7712, host='127.0.0.1')




