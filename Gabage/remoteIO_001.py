from gpiozero import Button, LED
from gpiozero.pins.pigpio import PiGPIOFactory
#from signal import pause

list = [0,2,3]

print(list[0])
#print([list[8]])
for n, val in enumerate(list):
    print(n,val)
dict = {'IF':0,'NAME':None,'TYPE':None,'MODe':'ACTIVE'}

_counter = 0
for k,i in dict.items():
    try:
        dict[k] = list[_counter]
    except:
        dict[k] = None
    _counter = _counter+1
    print(_counter,dict)

#led.source = button

#pause()