

import logging
import smbus


class MCP23017(object):

    def __init__(self,busId,address):

        self._busId = busId
        self._address = address

        self._bus = smbus.SMBus(1)
        self._address = 0x20
        self._bus.write_byte_data(self._address,0x00,0x00) #Output
        self._bus.write_byte_data(self._address,0x01,0x00)
        self._bus.write_byte_data(self._address, 0x12, 0x00)
        self._bus.write_byte_data(self._address, 0x13, 0x00)

    def readA(self):
     #   print('ReadA',self._bus.read_byte_data(self._address,0x12))
        return self._bus.read_byte_data(self._address,0x12)

    def readB(self):
      #  print('ReadB', self._bus.read_byte_data(self._address, 0x13))
        return self._bus.read_byte_data(self._address,0x13)

    def writeA(self,value):
       # print('writeA',value)
        self._bus.write_byte_data(self._address,0x12,value)

    def writeB(self,value):
        #print('writeB',value)
        self._bus.write_byte_data(self._address,0x13,value)
