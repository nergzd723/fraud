import pyaudio
import numpy as np
import wave


class AudioIO:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.byteorder = 'big' # BIG ENDIAN: SIGNIFICANT BYTE FIRST
        self.speed = 0.29 # 100ms
        self.volume = 1
        self.fs = 44100
        self.freqhigh = 1800
        self.freqlow = 2100
        self.freqStop = 1000
        self.freqStart = 660
        self.freqBYTE = 860
        self.freqEND = 3600
        self.samplehigh = self.CreateSample(self.freqhigh, self.fs, self.speed)
        self.samplelow = self.CreateSample(self.freqlow, self.fs, self.speed)
        self.samplestop = self.CreateSample(self.freqStop, self.fs, self.speed)
        self.sampleEND = self.CreateSample(self.freqEND, self.fs, self.speed)
        self.streaminput = self.p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=self.fs,
                output=True,
                input=True)
        self.streamout = self.p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=self.fs,
                output=True)
        self.frames = []
        self.chunks = 1024
    def Record(self, speed, fs=44100):
        for _ in range(0, int(fs / self.chunks * speed+0.05)):
            data = self.streaminput.read(self.chunks)
            self.frames.append(data)
        wav = wave.open("temp.wav", "wb")
        wav.setnchannels(2)
        wav.setsampwidth(self.p.get_sample_size(pyaudio.paFloat32))
        wav.setframerate(self.fs)
        wav.writeframes(b''.join(self.frames))
        wav.close()
    def CreateSample(self, freq, fs, speed):
        return (np.sin(2*np.pi*np.arange(fs*speed)*freq/fs)).astype(np.float32)
    def EncodeAndTransmit(self, data):
        for _ in range(10):
            self.streamout.write(self.volume*self.CreateSample(self.freqStart, self.fs, 0.1))
            self.streamout.write(0*self.CreateSample(self.freqStart, self.fs, self.speed+0.1))
        r = open(data, "r")
        bdata = r.read()
        bita = self.tobits(bdata)
        ctr = 0
        for bit in bita:
            if ctr == 8:
                ctr = 0
                #self.streamout.write(self.volume*self.CreateSample(self.freqBYTE, self.fs, 0.25)) not supported YET
            ctr += 1
            self.Transmit(bit)
        for _ in range(10):
            self.streamout.write(self.volume*self.CreateSample(self.freqEND, self.fs, self.speed+0.3))
            self.streamout.write(0*self.CreateSample(self.freqStop, self.fs, 0.1))
    def tobits(self, s):
        ords = (ord(c) for c in s)
        shifts = (7, 6, 5, 4, 3, 2, 1, 0)
        return [(o >> shift) & 1 for o in ords for shift in shifts]
    def Transmit(self, bit):
        if bit:
            self.streamout.write(self.volume*self.samplehigh)
            self.streamout.write(self.volume*self.samplestop)
            return
        self.streamout.write(self.volume*self.samplelow)
        self.streamout.write(self.volume*self.samplestop)
if __name__ == "__main__":
    sender = AudioIO()
    sender.EncodeAndTransmit("lat.txt")