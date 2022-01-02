import os
#import RPi.GPIO as GPIO  # import the GPIO library


def toneOn(duration):
    if duration >= 255:
        print('duration ON forever')
    else:
        print('sound ON for ',duration)

def toneOff(duration):
    if duration >= 255:
        print('duration OFF forever')
    else:
        print('sound OFF for ',duration)


_sequence = [[1,0.1],[0,0.2],[1,0.3],[0,255]]
for n in _sequence:
    if 1 == n[0]:
        print('Tone on for ',n[1])
        toneOn(n[1])

    else:
        print('Tone off for ',n[1])
        toneOff(n[1])
while(_sequence):
    print(_sequence)
    _sequence = []
print('end')

