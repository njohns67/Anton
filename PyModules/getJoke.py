import requests
import tts

def play():
    r = requests.get("http://icanhazdadjoke.com", headers={"Accept": "text/plain"})
    print(r.text)
    #a, b = (r.text).split(".")
    #tts.text2speech(a, "delme", 1)
    #tts.text2speech(b, "delme", 1)
    tts.text2speech(r.text, "delme", 1)

