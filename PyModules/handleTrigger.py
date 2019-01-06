import speech_recognition as sr
import subprocess
import sys, os, time
import sounddevice as sd
import soundfile as sf
import parseTranscript as pT
import wave, pyaudio

length = 3.5
samplerate = 44100
filename = "temp.wav"
dong = "/home/pi/Anton/Sounds/dong.wav"
ding = "/home/pi/Anton/Sounds/ding.wav"
attempts = 0

def record():
    subprocess.Popen(["mpc", "volume", "0"])
    subprocess.Popen(["play", dong])
    recording = sd.rec(int(length * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(filename, recording, samplerate)
    transcript = processAudio()
    if transcript == 1:
        pT.parse("Bad transcript")
        return
    pT.parse(transcript)

def processAudio():
    subprocess.Popen(["mpc", "volume", "100"])
    subprocess.Popen(["play", ding])
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
