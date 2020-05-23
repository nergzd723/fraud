import pyaudio
import numpy as np
class AudioListener:
    def __init__(self):
        pass
    def toChar(self, bl):
        bi = iter(bl)
        bytes = zip(*(bi,) * 8)
        shifts = (7, 6, 5, 4, 3, 2, 1, 0)
        for byte in bytes:
            yield chr(sum(bit << s for bit, s in zip(byte, shifts)))
    def toS(self, bl):
        return ''.join(self.toChar(bl))
    def DecodeBA(self, byteArray):
        return self.toS(byteArray)
class AudioSender:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.speed = 0.01 # 10ms
        self.volume = 1
        self.fs = 44100
        self.freqhigh = 880
        self.freqlow = 720
        self.samplehigh = (np.sin(2*np.pi*np.arange(self.fs*self.speed)*self.freqhigh/self.fs)).astype(np.float32)
        self.samplelow = (np.sin(2*np.pi*np.arange(self.fs*self.speed)*self.freqhigh/self.fs)).astype(np.float32)
        self.stream = self.p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=self.fs,
                output=True)
    def EncodeAndTransmit(self, data):  
        r = open(data, "r")
        bdata = r.read()
        byte = self.tobits(bdata)
        for bit in byte:
            self.Transmit(bit)
    def tobits(self, s):
        ords = (ord(c) for c in s)
        shifts = (7, 6, 5, 4, 3, 2, 1, 0)
        return [(o >> shift) & 1 for o in ords for shift in shifts]
    def Transmit(self, bit):
        if bit:
            self.stream.write(self.volume*self.samplehigh)
            return
        self.stream.write(self.volume*self.samplelow)

if __name__ == "__main__":
    listener = AudioListener()
    sender = AudioSender()
    sender.EncodeAndTransmit("lat.txt")