# import pyaudio
# import wave
# import pydub
#
# pa = pyaudio.PyAudio()
# stream = pa.open(format=pyaudio.paInt16, channels=2, rate=16000, input=True, frames_per_buffer=2048)
#
# count = 0
# record_buf = []
# while count < 8 * 5:
#     audio_data = stream.read(1024)  # 读出声卡缓冲区的音频数据
#     record_buf.append(audio_data)  # 将读出的音频数据追加到record_buf列表
#     count += 1
#     print('*')
#
# wf = wave.open('01.wav', 'wb')  # 创建一个音频文件，名字为“01.wav"
# wf.setnchannels(2)  # 设置声道数为2
# wf.setsampwidth(2)  # 设置采样深度为
# wf.setframerate(16000)  # 设置采样率为16000
# # 将数据写入创建的音频文件
# wf.writeframes("".encode().join(record_buf))
# # 写完后将文件关闭
#
#
# # 停止声卡
# stream.stop_stream()
# # 关闭声卡
# stream.close()
# # 终止pyaudio
# pa.terminate()
#
# print(type(record_buf[0]))
#
# song = pydub.AudioSegment.from_wav("01.wav")
#
# print(str(song))
# wf.close()

import pyaudio
import struct as st
import matplotlib.pyplot as plt
import pydub


CHUNK = 1000
FORMAT = pyaudio.paInt16  # 一帧占两字节
CHANNELS = 1
RATE = 1000
RECORD_SECONDS = 2
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                # input_device_index = 0, #选择声音设备
                frames_per_buffer=CHUNK)
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames += data

patch = st.unpack('<2000h', bytes(frames))  # 核心，解析声音强度
print(patch)
stream.stop_stream()
stream.close()
p.terminate()

x = list(range(0, 2000))
y = patch

plt.plot(x, y)
plt.show()

pydub.AudioSegment.