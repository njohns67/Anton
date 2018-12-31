import speech_recognition as sr
import sys, os, time
import sounddevice as sd
import soundfile as sf
import parseTranscript as pT
import wave, pyaudio

length = 2.5
samplerate = 44100
filename = "temp.wav"
dong = "Sounds/dong.wav"
ding = "Sounds/ding.wav"
attempts = 0

def record():
    global attempts
    ding_wav = wave.open(dong, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

    recording = sd.rec(int(length * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(filename, recording, samplerate)
    transcript = processAudio()
    if transcript == 1:
        pT.parse("Bad transcript")
        return
    pT.parse(transcript)

def processAudio():
    ding_wav = wave.open(ding, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()
    reg = sr.Recognizer()
    audio = sr.AudioFile(filename)
    with audio as source:
        audio = reg.record(source)
    try:
        transcript = reg.recognize_google(audio)
    except:
        print("Sorry, I didn't quite get that. Please try again.")
        return 1
    print(transcript)
    return transcript

def main():
    record()

if __name__ == "__main__":
    main()
