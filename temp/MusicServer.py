import pyaudio
from Web.server import MusicServerProcess
import socket

def find_internal_recording_device(p):
    # 要找查的设备名称中的关键字
    target = '立体声混音'
    # 逐一查找声音设备
    for i in range(p.get_device_count()):
        devInfo = p.get_device_info_by_index(i)
        print(devInfo)
        if devInfo['name'].find(target) >= 0 and devInfo['hostApi'] == 0:
            print('已找到内录设备,序号是 ', i)
            # return i
    print('无法找到内录设备!')
    return -1


if __name__ == '__main__':
    # pyaudio实例
    audio = pyaudio.PyAudio()
    # 获取设备总数
    device_count = audio.get_device_count()
    # 根据设备索引获取设备详细信息
    for i in range(audio.get_device_count()):
        devInfo = audio.get_device_info_by_index(i)
        print(devInfo)

    # audio = pyaudio.PyAudio()
    # dev_idx = find_internal_recording_device(audio)
    # stream = audio.open(input_device_index=1, format=pyaudio.paInt16, channels=2, rate=44100,
    #                     input=True,
    #                     frames_per_buffer=1024)

    # host = socket.gethostbyname(socket.gethostname())
    # host = '127.0.0.1'
    #
    # music_server = MusicServerProcess(host, 7712, 5, dev_idx)
    # music_server.server_start()




