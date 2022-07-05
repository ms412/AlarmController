import time
import logging
#from library.MCP23017 import MCP23008

from Gabage.GPIOSimulator import RPI as GPIO


class inputObject(object):
    def __init__(self,config,gpioObject,callback,logger):

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + self.__class__.__name__)
      #  self._log.debug('start GPIO')

        self._gpio = gpioObject
        self._io = int(config.get('IO',3))
        self._id = config.get('ID','UNKNOWN')
        self._type = config.get('TYPE','ALARM')
        self._mode = config.get('MODE','ACTIVE')
        self._mapping = {}
        self._mapping[0] = config.get('0','OFF')
        self._mapping[1] = config.get('1','ON')

        self._state = None
        self._callback = callback

       # self._ioState = None
        self.setup()

    def setup(self):
       # self._io = IO(self._gpio)
        self._log.debug('Setup IO: %d, ID: %s, State: %s ' % (self._io, self._id, self._state))
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setup(self._io, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)

        self._state = self._mapping.get(self._gpio.input(self._io))
       # print(self._io,type(self._io))
        self._gpio.add_event_detect(self._io,self._gpio.BOTH, self.event)

    def event(self,io):
        self._state = self._mapping.get(self._gpio.input(io))
        self._log.debug('I/O EVENT IO: %d, ID: %s, State: %s LowLevelState: %s' % (io, self._id, self._state,self._gpio.input(io)))
       # print(self._callback,self._state)
        self._callback(self,self._state)

    def setState(self,newState):
        _state = False

        for key, item in self._mapping.items():
            if item == newState:
                _state = True

        if _state:
            self._state = newState
            self._callback(self,self._state)

        return _state

    def state(self):
        return self._state

    def id(self):
        return self._id

    def type(self):
        return self._type

    def io(self):
        return self._io

    def mode(self):
        return self._mode

class outputObjcet(object):

    def __init__(self):
        self._io = MCP23008(1,0x20)

    def write(self):
        pass

class callbackTest(object):

    def event(self):
        print('event')
        return

if __name__ == "__main__":
    gg = GPIO()
    _config1 = {'INTERFACE': 3,1:'OPEN', 0:'CLOSE'}
    _config2 = {'INTERFACE': 5, 1: 'ON', 0: 'OFF'}
    _config3 = {'INTERFACE': 7, 1: 'OFFEN', 0: 'GESCHLOSSEN'}
    y = callbackTest()

    x = inputObject(gg,_config1,y.event)
    z = inputObject(gg,_config2,y.event)
    c = inputObject(gg,_config3,y.event)
 #   x.setup()
    while(True):
        print(x.state())
        print(z.state())
        print(c.state())
        time.sleep(4)
