import pyaudio
import numpy as np
import threading


class AudioIn:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        self.bitlist = [0]

    def Transcriptor(self):
        while True:
            data = np.fromstring(self.stream.read(1024), dtype=np.int16)
            # smooth the FFT by windowing data
            data = data * np.hanning(len(data))
            fft = abs(np.fft.fft(data).real)
            fft = fft[:int(len(fft)/2)]
            freqPeak, freqs = self.ExtractFrequencies(fft)
            for index, item in enumerate(freqs):
                freqs[index] = item.round(-2)
            if freqPeak == 0:
                continue  # noise
            elif freqPeak == 1800 or freqPeak == 1700 or freqPeak == 1600:
                if self.bitlist[len(self.bitlist)-1] == 0xD:
                    continue  # dupe
                self.bitlist.append(0xD)
                # print("BYTE")
            elif freqPeak == 700 or freqPeak == 600:
                if self.bitlist[len(self.bitlist)-1] == 3:
                    continue  # dup
                # print("START")
                self.bitlist.append(3)
            elif freqPeak == 1400 or freqPeak == 1500 or freqPeak == 1300:
                if self.bitlist[len(self.bitlist)-1] == 1:
                    continue  # dupe
               # print("1")
                self.bitlist.append(1)
            elif freqPeak == 2100 or freqPeak == 2200 or freqPeak == 2000:
                if self.bitlist[len(self.bitlist)-1] == 0:
                    continue  # dupe
                # print("0")
                self.bitlist.append(0)
            elif freqPeak == 1000 or freqPeak == 900 or freqPeak == 1100:
                if self.bitlist[len(self.bitlist)-1] == 4:
                    continue  # dupe
                self.bitlist.append(4)
                # print("STOP")
            elif freqPeak == 3600:
                if self.bitlist[len(self.bitlist)-1] == 0xF:
                    continue  # dupe
                print("END TRANSMISSION")
                self.bitlist.append(0xF)
            else:
                #("noise frequency ", freqPeak, "Hz")
                continue

    def bits2a(self, b):
        return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(b)]*8))

    def ExtractFrequencies(self, fft):
        norm = fft/1024
        m_v = np.abs(norm[range(len(fft)//2)])
        ind = self.findPeak(magnitude_values=m_v, noise_level=100)
        freqs = self.extractFrequency(indices=ind)
        freq = np.fft.fftfreq(1024, 1.0/44100)
        freq = freq[:int(len(freq)/2)]  # keep only first half
        freqPeak = freq[np.where(fft == np.max(fft))[0][0]]+1
        freqPeak = round(freqPeak, -2)
        return freqPeak, freqs

    def Processmsg(self):
        # First, remove STOP and START symbols
        # Remove first 0 since it is not needed
        bitlist = self.bitlist
        bitlist = list(filter((4).__ne__, bitlist))
        bitlist = list(filter((3).__ne__, bitlist))
        bitlist = list(filter((0xF).__ne__, bitlist))
        bitlist = bitlist[1:]
        # Now, split to bytes
        bytelist = []
        templist = []
        for bit in bitlist:
            if bit == 0xD:
                if len(templist) == 8:
                    # Perfect!
                    bytelist.append(templist)
                elif len(templist) < 8:  # Corrupted byte
                    print("Corrupted byte")
                    while len(templist) != 8:
                        templist.append(1)
                    bytelist.append(templist)
                elif len(templist) > 8:  # Lost byte d istinguisher, need to split that... OR we got MORE bytes than expected, but I don't have solution to that problem
                    print("No distinquisher")
                    list1 = templist[:8]
                    bytelist.append(list1)
                    list2 = templist[8:]
                    if len(list2) != 8:
                        print("Irrecoverable distinquisher error")
                        # Fuck it! At least saved first char... or fucked up both LMAO
                        list2 = list2[:8]
                templist = []
            else:
                templist.append(bit)
        bitlist = []
        for l in bytelist:
            for bit in l:
                bitlist.append(bit)
        s = ' '.join([str(elem) for elem in bitlist])
        s = s.replace(" ", "")
        at = self.bits2a(s)
        print(at)
        self.bitlist = [0]

    def RealTime(self):
        tthread = threading.Thread(target=self.Transcriptor)
        tthread.start()
        while True:
            if 0xF in self.bitlist:
                if self.bitlist == [0xF]:
                    continue
                self.Processmsg()

    def findPeak(self, magnitude_values, noise_level=500):
        splitter = 0
        # zero out low values in the magnitude array to remove noise (if any)
        magnitude_values = np.asarray(magnitude_values)
        low_values_indices = magnitude_values < noise_level  # Where values are low
        # All low values will be zero out
        magnitude_values[low_values_indices] = 0
        indices = []
        flag_start_looking = False
        both_ends_indices = []
        length = len(magnitude_values)
        for i in range(length):
            if magnitude_values[i] != splitter:
                if not flag_start_looking:
                    flag_start_looking = True
                    both_ends_indices = [0, 0]
                    both_ends_indices[0] = i
            else:
                if flag_start_looking:
                    flag_start_looking = False
                    both_ends_indices[1] = i
                    # add both_ends_indices in to indices
                    indices.append(both_ends_indices)
        return indices

    def extractFrequency(self, indices, freq_threshold=2):
        extracted_freqs = []
        freq_bins = np.arange(1024) * 44100/1024
        for index in indices:
            freqs_range = freq_bins[index[0]: index[1]]
            avg_freq = round(np.average(freqs_range))
            if avg_freq not in extracted_freqs:
                extracted_freqs.append(avg_freq)
        # group extracted frequency by nearby=freq_threshold (tolerate gaps=freq_threshold)
        group_similar_values = np.split(extracted_freqs, np.where(
            np.diff(extracted_freqs) > freq_threshold)[0]+1)
        # calculate the average of similar value
        extracted_freqs = []
        for group in group_similar_values:
            extracted_freqs.append(round(np.average(group)))
        return extracted_freqs


if __name__ == "__main__":
    a = AudioIn()
    a.RealTime()
