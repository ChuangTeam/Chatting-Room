from pydub import AudioSegment
import struct
import io


AudioSegment.ffmpeg = r"ffmpeg\bin"  # 替换为你的ffmpeg路径
def create_head(byte):
    head = b'RIFF$'
    head += struct.pack('<L', len(byte) + 44)[1:]   # 这里的[1:]是因为打包完的数据第一个字符不知道为什么是逗号
    head += b'WAVE'
    head += b'fmt '
    head += b'\x10\x00\x00\x00\x01\x00\x02\x00\x80>\x00\x00\x00\xfa\x00\x00\x04\x00\x10\x00'
    head += b'data'
    head += struct.pack('<L', len(byte))
    return head + byte

def amplify_audio(audio_bytes, amplification_factor):





    # 将bytes格式的音频转换为AudioSegment对象
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format='wav')
    # 放大音量
    amplified_audio_segment = audio_segment + amplification_factor
    # 将AudioSegment对象转换回bytes格式
    amplified_audio_bytes = amplified_audio_segment.raw_data
    return amplified_audio_bytes
