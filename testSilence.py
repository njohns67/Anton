import pyaudio
import math
import struct
import wave

Threshhold = 30

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE= 16000
swidth = 2
Max_Seconds = 10
TimeoutSignal = ((RATE / chunk * Max_Seconds) + 2)
silence = True
FileNameTmp = "temp.wav"
Time = 0
all = []

def GetStream(chunk):
    return stream.read(chunk)

def rms(frame):
    count = len(frame)/swidth
    format = "%dh"%(count)
    shorts = struct.unpack(format, frame)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
        rms = math.pow(sum_squares/count, .5)
        return rms * 1000

def WriteSpeech(WriteData):
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(FileNameTmp, "wb")
    wf.setsamwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(WriteData)
    wf.close()

def KeepRecord(TimeoutSignal, LastBlock):
    all.append(LastBlock)
    for i in range(0, TimeoutSignal):
        try:
            data = GetStream(chunk)
        except:
            continue
        all.append(data)
    print("End record")
    WriteSpeech(data)
    silence = True
    Time = 0
def listen(silence, Time):
    print("Waiting")
    while silence:
        try:
            input = GetStream(chunk)
        except:
            continue
        rms_value = rms(input)
        if rms_value > Threshhold:
            silence = False
            LastBlock = input
            print('Recording')
            KeepRecord(TimeoutSignal, LastBlock)
            Time += 1
            if Time > TimeoutSignal:
                print("Nothing detected")
                sys.exit
p = pyaudio.PyAudio()
stream = p.open(format = FORMAT,
        channels = CHANNELS,
        rate = RATE,
        input = True,
        output = True,
        frames_per_buffer = chunk)
listen(silence, Time)
