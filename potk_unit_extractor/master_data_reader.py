import io
import struct


class MasterDataReader:
    """Reads serialized Master Data.
    Uses C# naming conventions to allow easy porting.
    TODO Make sense of this port.
    """
    buf: io.BytesIO
    n: int
    length: int
    charBuf: str

    def __init__(self, buf: bytes):
        self.buf = io.BytesIO(buf)
        self.endian = '<'
        self.ReadInt()
        self.length = self.ReadInt()
        self.ReadInt()

    def Length(self):
        return self.length

    def read(self, *args):
        return self.buf.read(*args)

    def ReadBool(self) -> bool:
        return struct.unpack(self.endian+"b", self.read(1))[0]

    def ReadBoolOrNull(self) -> bool:
        if not self.ReadBool():
            return False
        else:
            return self.ReadBool()

    def ReadInt(self) -> int:
        return struct.unpack(self.endian+"i", self.read(4))[0]

    def ReadIntOrNull(self) -> int:
        if not self.ReadBool():
            return 0
        else:
            return self.ReadInt()

    def ReadString(self, intern=False) -> str:
        length = self.ReadInt()
        if not length:
            return ''
        ret = self.read(length*2)
        if intern:
            return ret.decode('utf16')
        else:
            if ret[1] == 0:
                return ret[::2].decode()
            else:
                try:
                    return ret.decode()
                except:
                    return str(ret)

    def ReadStringOrNull(self, intern=False) -> str:
        if not self.ReadBool():
            return ''
        else:
            return self.ReadString(intern)

    def ReadFloat(self) -> float:
        return struct.unpack(self.endian+"f", self.read(4))[0]

    def ReadFloatOrNull(self) -> float:
        if not self.ReadBool():
            return 0.0
        else:
            return self.ReadFloat()

    def ReadDateTime(self):
        return self.ReadString(False)

    def ReadDateTimeOrNull(self):
        s = self.ReadStringOrNull(False)
        if not s:
            return ''
        else:
            return s
