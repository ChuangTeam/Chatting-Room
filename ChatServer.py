from Web.server import ChatServerProcess, MusicServerProcess
from threading import Thread


if __name__ == '__main__':
    host = '127.0.0.1'
    # host = gethostbyname(gethostname())

    chat_server = ChatServerProcess(host, 7711, 10)
    voice_stream_server = MusicServerProcess(host, 7712, 10)

    # voice_p = Process(target=voice_stream_server.server_start)
    # chat_p = Process(target=chat_server.server_start)
    # voice_p.start()
    # chat_p.start()

    voice_t = Thread(target=voice_stream_server.server_start)
    chat_t = Thread(target=chat_server.server_start)

    voice_t.start()
    chat_t.start()

