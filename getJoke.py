import requests
import tts

def play():
    r = requests.get("http://icanhazdadjoke.com", headers={"Accept": "text/plain"})
    tts.text2speech(r.text, "delme", 1)


