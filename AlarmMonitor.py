#!/usr/bin/python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "Alarm Monitor"
__VERSION__ = "0.01"
__DATE__ = "11.09.2021"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2021 Markus Schiesser"
__license__ = 'GPL v3'

import os
import sys
import time
import json
import logging
import uuid
import smbus

from configobj import ConfigObj

from library.mqttclient import mqttclient
from library.logger import loghandler
from library.MCP23017 import MCP23017
from library.outputLED import LED
from library.buzzer import Buzzer
#from library.Interface import Interface
#from library.S0Manager import S0manager

#class manager(threading.Thread):
class AlarmMonitor(object):

    def __init__(self,configfile='AlarmController.config'):
    #    threading.Thread.__init__(self)

        self._configfile = os.path.join(os.path.dirname(__file__), configfile)
        print(self._configfile)

        #self._configfile = configfile

        self._configBroker = None
        self._configLog = None
        self._configDevice = None
        self._configLED = None

        self._ledDeviceList  = []

        self._bus = None
        self._address = 0x00

        #self._watchdogTimer = time.time()

        _watchdogID = uuid.uuid1()
        self._watchdogTopic = 'WATCHDOG/' + str(_watchdogID)

        self._rootLoggerName = ''


    def readConfig(self):

        _config = ConfigObj(self._configfile)
        print(_config)

        if bool(_config) is False:
            print('ERROR config file not found',self._configfile)
            sys.exit()
            #exit

        self._configBroker = _config.get('BROKER',None)
        self._configLog = _config.get('LOGGING',None)
        self._configDevice = _config.get('DEVICE', None)
        self._configLED = _config.get('LED',None)
      #  self._cfg_msgAdapter = _cfg.get('BROKER',None)
        return True

    def startLogger(self):
       # self._log = loghandler('marantec')

        self._configLog['DIRECTORY'] = os.path.dirname(__file__)
        self._root_logger = loghandler(self._configLog.get('NAME','ALARM-MONITOR'))
        self._root_logger.handle(self._configLog.get('LOGMODE','PRINT'),self._configLog)
        self._root_logger.level(self._configLog.get('LOGLEVEL','DEBUG'))
        self._rootLoggerName = self._configLog.get('NAME',self.__class__.__name__)
        self._log = logging.getLogger(self._rootLoggerName + '.' + self.__class__.__name__)
      #  print('TEST')

        self._log.debug('Start instance of marantec250c object')
        return True

    def startMqtt(self):

        self._log.debug('Methode: startMqtt()')
        self._mqtt = mqttclient(self._rootLoggerName)

        _list = []

        _subscribe = (self._configBroker['SUBSCRIBE']) + '/#'
        _callback = self.brokerCallback

        _list.append({'SUBSCRIBE': _subscribe, 'CALLBACK': _callback})
        self._configBroker['SUBSCRIPTION'] = _list

        (state, message) = self._mqtt.fullclient(self._configBroker)
        if state:
            self._log.debug('mqtt completed with message %s', message)
        else:
            self._log.error('Failed to connect: %s', message)

        return False

    def startBuzzer(self):
        self._buzzer = Buzzer(16)

    def brokerCallback(self,client,userdata,msg):
        self._log.debug('mqttCallback: Topic ' + msg.topic + " QOS: " + str(msg.qos) + " Payload: " + str(msg.payload))
        _topic = msg.topic

        try:
            self.setLED(msg.topic,msg.payload.decode("utf-8"))
        except:
            self._log.error('brockerCallback evalutation of Mqtt message failed: %s'% str(msg.payload))

        return True

    def startLED(self):
        print('startLED')
        _device = MCP23017(int(self._configDevice.get('I2C',1)),self._configDevice.get('ADDRESS',0x20))

        for k,v in self._configLED.items():
            self._ledDeviceList.append(LED(str(k),int(v),_device,self._rootLoggerName))

        return True

    def setLED(self,topic,payload):
        print('setLED')

        _device = topic.split('/')[-1]

        for _item in self._ledDeviceList:
            if _device == _item.deviceId():
          #      print(str(payload))
                if 'OPEN' == str(payload) or 'UNLOCK' == str(payload):
                    if 'GREEN' == _item.pinState():
                        self._buzzer.tone1()
                    _item.setRed()

                elif 'CLOSE' == str(payload) or 'LOCK' == str(payload):
                    if 'RED' == _item.pinState():
                        self._buzzer.tone2()
                    _item.setGreen()
                else:
                    self._log.error('UNKNOWN Port State')

        return True

    def startLEDold(self):
        print('START LED')
        self._bus = smbus.SMBus(1)
        self._address = 0x20
        self._bus.write_byte_data(self._address,0x00,0x00) #Output
        self._bus.write_byte_data(self._address,0x01,0x00)
        self._bus.write_byte_data(self._address, 0x12, 0x00)
        self._bus.write_byte_data(self._address, 0x13, 0x00)


    def setLEDold(self,topic,payload):
       # print(topic)

        if 'OPEN' in str(payload):
            state = 1
        else:
            state = 0
      #  print('STATE: ',state)
        item = topic.split('/')[-1]
        print(item, state)
        x = 0x01
        if 'KITCHEN' == item:
            x = 0x01 << 5
        elif 'EATING' == item:
            x = 0x01 << 4
        elif 'BATH' == item:
            x = 0x01 << 3
        elif 'FRONTDOOR' == item:
            x = 0x01 << 2
        elif 'FRONTDOORLOCK' == item:
            x = 0x01 << 7
        elif 'BACKDOORLOCK' == item:
            x = 0x01 << 6
        elif 'PANIK' == item:
            x = 0x01 << 1
        elif 'RESET' == item:
            x = 0x01
        else:
            print('NOT FOUND')
            x = 0x00

        if state:
            _valueB = self._bus.read_byte_data(self._address,0x13)
            _yB = _valueB & ~x
            print('xx',_yB,_valueB,~x)
            self._bus.write_byte_data(0x20, 0x13, _yB)

            _value = self._bus.read_byte_data(self._address, 0x12)
            _y = _value | x
            print('CLOSE',_y,_value,x)
            self._bus.write_byte_data(0x20, 0x12, _y)
        else:
            _valueB = self._bus.read_byte_data(self._address,0x12)
            _yB = _valueB & ~x
            print('yy', _yB, _valueB, ~x)
            self._bus.write_byte_data(0x20, 0x12, _yB)

            _value = self._bus.read_byte_data(self._address, 0x13)
            _y = _value | x
            print('OPEN',_y, _value, x)
            self._bus.write_byte_data(0x20, 0x13, _y)

       # print('%s %s d%'%(item,hex(x)))
        print(item,x)
        #self._bus.write_byte_data(0x20,0x12,x)

    def start(self):
        self.readConfig()
        self.startLogger()
        self.startLED()
        self.startBuzzer()
        self.startMqtt()
      #  self.monitoringStart()
        while(True):
            time.sleep(15)
           # self.update()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
     #   configfile = '/opt/AlarmMonitor/AlarmMonitor.config'
        configfile = 'AlarmMonitor.config'

    am = AlarmMonitor(configfile)
    am.start()

