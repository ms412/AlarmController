
from gpiozero import Button

class Input(object):
    def __init__(self,config,callback):
        self._io = IO
        self._id = id
        self._callback = callback

        self._state = None
        self.setup()

    def setup(self):
        self._button = Button(self._io)
        if self._button.value:
            self._state= 'CLOSE'
        else:
            self._state= 'OPEN'

        print('Setup: ', self._id, self._io,self._state)

        self._button.when_pressed = self.close
        self._button.when_released = self.open

    def open(self):
        print('OPEN')
        self._state= 'OPEN'
        self._callback(self,self._state)

    def close(self):
        print('CLOSE')
        self._state= 'CLOSE'
        self._callback(self,self._state)

    def state(self):
        return self._state

    def id(self):
        return self._id