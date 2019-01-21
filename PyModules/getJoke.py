import requests
import tts
import string


def play():
    printable = set(string.printable)
    r = requests.get("http://icanhazdadjoke.com", headers={"Accept": "text/plain"})
    print(r.text)
    joke = "".join(i for i in r.text if ord(i)<128)
    print(joke)
    tts.text2speech(joke, "delme", 1)

