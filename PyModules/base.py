import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", "-v", help="Print output from all functions", action="store_true")
parser.add_argument("--debug", "-d", help="Enable debug mode", action="store_true")
parser.add_argument("-m", "--models", help="List of models to be used", nargs='+')
args = parser.parse_args()

import os
from Anton import Anton
import sys
from threading import Thread
sys.path.append("/home/pi/Anton/Py3Snowboy/snowboy/examples/Python3")
sys.path.append("/home/pi/Anton/PyModules")
import snowboydecoder
import signal

anton = Anton(debug=args.debug, verbose=args.verbose)
if args.debug:
    while True:
        anton.parseTranscript(input("Enter command\n"))
interrupted = False

def trigger():
    print("Triggered")
    sys.stdout.flush()

def signal_handler(signal, frame):
    global interrupted
    interrupted = True
    for x in anton.processes:
        x.send_signal(signal)
        x.wait()
    anton.isDead = 1
    anton.isRecording = 1
    os.system("stty sane")

def interrupt_callback():
    global interrupted
    return interrupted
model = args.models
sensitivity = [.33, .33]
# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)
detector = snowboydecoder.HotwordDetector(model, sensitivity=sensitivity)
print('Listening... Press Ctrl+C to exit')
# main loop
detector.start(detected_callback=anton.record,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
