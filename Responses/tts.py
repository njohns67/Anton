from google.cloud import texttospeech as tts
import os

os.system("export GOOGLE_APPLICATION_CREDENTIALS=\"/home/pi/Anton/Key.json\"")
client = tts.TextToSpeechClient()
while 1:
	try:
		TEXT = input("\nEnter response to request\n")
	except KeyboardInterrupt:
		exit(0)
	file = input("\nEnter name of file\n")
	file = file + ".mp3"
	sinput = tts.types.SynthesisInput(text=TEXT)
	voice = tts.types.VoiceSelectionParams(language_code="en-US",
	ssml_gender=tts.enums.SsmlVoiceGender.MALE)
	config = tts.types.AudioConfig(audio_encoding=tts.enums.AudioEncoding.MP3)
	response = client.synthesize_speech(sinput, voice, config)
	with open(file, "wb") as out:
		out.write(response.audio_content)
