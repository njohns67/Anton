import requests
import tts

def play():
    r = requests.get("http://icanhazdadjoke.com", headers={"Accept": "text/plain"})
    filter(lambda x: x in printable, r.text)
    print(r.text)
    tts.text2speech(r.text, "delme", 1)

