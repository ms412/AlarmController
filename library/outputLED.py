
import logging

class LED(object):

    def __init__(self,id,bit,handle,logger):

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)

        self._log.debug('Create LED Object ID %s Bit %d'%(id,bit))

        self._id = id
        self._bit = bit
        self._handle = handle

        self._pinState = None

    def deviceId(self):
        return self._id

    def deviceBit(self):
        return self._bit

    def pinState(self):
        return self._pinState

    def setRed(self):
        self._log.debug('Set LED %s to RED',self._id)
        _x = 0x01 << self._bit
       # _valueB = self._handle.readB()
        self._handle.writeB(self._handle.readB() & ~_x)
       # print('xx',self._id, self._bit, hex(_yB), hex(_valueB), hex(x),hex(~x))
       # self._handle.writeB(_yB)

      #  _value = self._handle.readA()
    #    _y = _value | x
        self._handle.writeA(self._handle.readA() | _x)
      #  print('OPEN',self._id, _y, _value, x)
       # self._handle.writeA(_y)
        self._pinState = 'RED'

    def setGreen(self):
        self._log.debug('Set LED %s to GREEN', self._id)
        _x = 0x01 << self._bit
      #  _valueB = self._handle.readA()
       # _yB = _valueB & ~x
      #  print('yy',self._id, self._bit, hex(_yB), hex(_valueB), hex(x),hex(~x))
     #   self._handle.writeA(_yB)
        self._handle.writeA(self._handle.readA() & ~_x)

       # _value = self._handle.readB()
       # _y = _value | x
       # print('CLOSE', self._id,_y, _value, x)
        #self._handle.writeB(_y)
        self._handle.writeB(self._handle.readB() | _x)
     #   print(self._handle.readB())
        self._pinState = 'GREEN'

    def setYellow(self):
        self._log.debug('Set LED %s to YELLOW', self._id)

        _x = 0x01 << self._bit
        self._handle.writeA(self._handle.readA() | _x)
        self._handle.writeB(self._handle.readB() | _x)
        self._pinState = 'YELLOW'