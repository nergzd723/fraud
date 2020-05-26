import pyaudio
import numpy as np

class AudioIn:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream=self.p.open(format=pyaudio.paInt16,channels=1,rate=44100,input=True, frames_per_buffer=1024)
    def bits2a(self, b):
        return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(b)]*8))
    def RealTime(self):
    
        bytelist = [0]
        while True:
            if len(bytelist) == 220:
                break
            data = np.fromstring(self.stream.read(1024),dtype=np.int16)
            data = data * np.hanning(len(data)) # smooth the FFT by windowing data
            fft = abs(np.fft.fft(data).real)
            fft = fft[:int(len(fft)/2)]
            freq = np.fft.fftfreq(1024,1.0/44100)
            freq = freq[:int(len(freq)/2)] # keep only first half
            val = fft[np.where(freq>500)[0][0]]
            freqPeak = freq[np.where(fft==np.max(fft))[0][0]]+1
            freqPeak = round(freqPeak, -2)
            if freqPeak == 0:
                continue # noise
            elif freqPeak == 500:
                print("START")
                if bytelist[len(bytelist)-1] == 3:
                    continue # dup
                bytelist.append(3)
            elif freqPeak == 6500:
                print("1")
                if bytelist[len(bytelist)-1] == 1:
                    continue # dupe
                bytelist.append(1)
            elif freqPeak == 2100:
                print("0")
                if bytelist[len(bytelist)-1] == 0:
                    continue # dupe
                bytelist.append(0)
            elif freqPeak == 1000:
                if bytelist[len(bytelist)-1] == 4:
                    continue # dupe
                bytelist.append(4)
                print("STOP")
            else:
                #continue
                print("noise frequency: %d Hz"%freqPeak)
        bytelist = list(filter((4).__ne__, bytelist))
        bytelist = list(filter((3).__ne__, bytelist))
        bytelist = bytelist[1:]
        print(bytelist)
        s = ""
        s = ' '.join([str(elem) for elem in bytelist])
        print(s)
        s = s.replace(" ", "")
        at = self.bits2a(s)
        print(at)
if __name__ == "__main__":
    a = AudioIn()
    a.RealTime()