# Anton

Anton is a custom built "Alexa"-type personal assistant, 
designed to be used with an IOT style series of Arduinos
and other devices.

# Dependencies
Anton relies on Snowboy for Python3 for hotword detection and must be installed for Anton to work properly. Additionally various python libraries are needed as well as google text to speech credentials for certain functions.
**List of python modules required:**
- Snowboy
- weather
- speech_recognition
- soundfile
- sounddevice
- pyaudio
- wave
- serial
- google.cloud

# Commands
Anton's current hotword is "Hey Anton", but can be changed with a few minor tweaks.
**Current Commands Include:** 
- Turn on the lights (Temporary command, currently connected to an Arduino Nano)
- Turn on/off the green/red light
- What's the weather in *city* today/tomorrow?
- Tell me a (dad) joke
- Set a timer for *x* seconds/minutes/hours and *y* seconds/minutes/hours

**Future Commands Include:**
- Feed Scout (my cat)
- Beer me
- Turn on the shower
- Set the oven to (temperature)

Most of the commands I intend on implementing rely on other devices to be configured ahead of time.
