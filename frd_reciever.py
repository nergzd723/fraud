import pyaudio
import numpy as np

class AudioIn:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream=self.p.open(format=pyaudio.paInt16,channels=1,rate=44100,input=True, frames_per_buffer=1024)
    def bits2a(self, b):
        return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(b)]*8))
    def RealTime(self):
    
        bitlist = [0]
        ctr = 0
        while True:
            data = np.fromstring(self.stream.read(1024),dtype=np.int16)
            data = data * np.hanning(len(data)) # smooth the FFT by windowing data
            fft = abs(np.fft.fft(data).real)
            fft = fft[:int(len(fft)/2)]
            freq = np.fft.fftfreq(1024,1.0/44100)
            freq = freq[:int(len(freq)/2)] # keep only first half
            freqPeak = freq[np.where(fft==np.max(fft))[0][0]]+1
            freqPeak = round(freqPeak, -2)
            if freqPeak == 0:
                continue # noise
            elif freqPeak == 700:
                if bitlist[len(bitlist)-1] == 3:
                    continue # dup
                print("START")
                bitlist.append(3)
            elif freqPeak == 1800: 
                if bitlist[len(bitlist)-1] == 1:
                    continue # dupe
                print("1")
                bitlist.append(1)
            elif freqPeak == 2100:
                if bitlist[len(bitlist)-1] == 0:
                    continue # dupe
                print("0")
                bitlist.append(0)
            elif freqPeak == 1000:
                if bitlist[len(bitlist)-1] == 4:
                    continue # dupe
                bitlist.append(4)
                print("STOP")
            elif freqPeak == 3600:
                if ctr == 1:
                    print("END TRANSMISSION")
                    break
                ctr = 1 # wait for END TRANSMISSION 2 times
            else:
            #continue
                print("noise frequency: %d Hz"%freqPeak)
        bitlist = list(filter((4).__ne__, bitlist))
        bitlist = list(filter((3).__ne__, bitlist))
        bitlist = bitlist[1:]
        print(bitlist)
        s = ""
        s = ' '.join([str(elem) for elem in bitlist])
        print(s)
        s = s.replace(" ", "")
        at = self.bits2a(s)
        print(at)
if __name__ == "__main__":
    a = AudioIn()
    a.RealTime()