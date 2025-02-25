import io
import url_cache

from discord.player import AudioSource
# from discord.opus import Encoder as OpusEncoder

FRAME_SIZE = 3840 # bytes

class BGMStreamManager:
    def __init__(self) -> None:
        self.intro_stream: io.BufferedIOBase = None
        self.loop_stream: io.BufferedIOBase = None
        self.is_opening = False

    def open_files(self, intro_path: str, loop_path: str) -> None:
        if self.is_opening:
            self.close()
        self.intro_stream = open(intro_path, 'rb')
        self.loop_stream = open(loop_path, 'rb')
        self.is_opening = True

    async def open_urls(self, intro_url: str, loop_url: str) -> None:
        # todo: handle error
        if self.is_opening:
            self.close()

        self.intro_stream = await url_cache.get(intro_url)
        self.loop_stream = await url_cache.get(loop_url)
        self.is_opening = True

    def get_intro_stream(self) -> io.BufferedIOBase:
        if not self.is_opening:
            raise ValueError('Stream is not opened')
        return self.intro_stream

    def get_loop_stream(self) -> io.BufferedIOBase:
        if not self.is_opening:
            raise ValueError('Stream is not opened')
        return self.loop_stream

    def close(self) -> None:
        if not self.is_opening:
            return
        self.intro_stream.close()
        self.loop_stream.close()
        self.is_opening = False

    def __del__(self) -> None:
        self.close()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class BGMPlayer(AudioSource):
    def __init__(self, intro_stream: io.BufferedIOBase, loop_stream: io.BufferedIOBase) -> None:
        self.intro_stream: io.BufferedIOBase = intro_stream
        self.loop_stream: io.BufferedIOBase = loop_stream
        if not intro_stream.seekable() or not loop_stream.seekable():
            raise ValueError('Streams must be seekable')
        self.is_intro = intro_stream is not None

        if loop_stream is None:
            raise ValueError('Loop stream must be provided')

    def read(self) -> bytes:
        if self.is_intro:
            intro_read = self.intro_stream.read(FRAME_SIZE)
            if  0 < len(intro_read) < FRAME_SIZE:
                self.is_intro = False
                self.loop_stream.seek(0)
                intro_read += self.loop_stream.read(FRAME_SIZE - len(intro_read))
            return intro_read

        loop_read = self.loop_stream.read(FRAME_SIZE)
        if  0 < len(loop_read) < FRAME_SIZE:
            self.loop_stream.seek(0)
            loop_read += self.loop_stream.read(FRAME_SIZE - len(loop_read))
        return loop_read