from google.cloud import texttospeech as tts
import os

def text2speech(TEXT, file="delme", PLAY=1):
    os.system("export GOOGLE_APPLICATION_CREDENTIALS=\"/home/pi/Anton/Key.json\"")
    client = tts.TextToSpeechClient()
    sinput = tts.types.SynthesisInput(text=TEXT)
    voice = tts.types.VoiceSelectionParams(language_code="en-US", 
        ssml_gender=tts.enums.SsmlVoiceGender.MALE)
    config = tts.types.AudioConfig(audio_encoding=tts.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(sinput, voice, config)
    with open(file + ".mp3", "wb") as out:
        out.write(response.audio_content)
    if PLAY == 1:
        play(file)

def play(file):
    os.system("mpg123 " + file + ".mp3")
