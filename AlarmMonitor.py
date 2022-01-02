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
__VERSION__ = "0.8"
__DATE__ = "02.01.2022"
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
        self._systemState = 'IDLE'

        self._bus = None
        self._address = 0x00

        #self._watchdogTimer = time.time()

        _watchdogID = uuid.uuid1()
        self._watchdogTopic = 'WATCHDOG/' + str(_watchdogID)

        self._rootLoggerName = ''


    def readConfig(self):

        _config = ConfigObj(self._configfile)
     #   print(_config)

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
        time.sleep(2)
        self._buzzer.start()
       # self._buzzer.command('TONE4')
        #time.sleep(10)
        #self._buzzer.command('TONE4')
        print('next')

    def brokerCallback(self,client,userdata,msg):
        self._log.debug('mqttCallback: Topic ' + msg.topic + " QOS: " + str(msg.qos) + " Payload: " + str(msg.payload))
        _topic = msg.topic

        #try:
        self.setLED(msg.topic,msg.payload.decode("utf-8"))
        #except:
         #   self._log.error('brockerCallback evalutation of Mqtt message failed: %s'% str(msg.payload))

        return True

    def startLED(self):
        self._log.info('Start LED')
        _device = MCP23017(int(self._configDevice.get('I2C',1)),self._configDevice.get('ADDRESS',0x20))

        for k,v in self._configLED.items():
            self._ledDeviceList.append(LED(str(k),int(v),_device,self._rootLoggerName))

        self._log.debug('Led Device List %s',self._ledDeviceList)
        return True

    def setLED(self,topic,payload):
      #  print('setLED')
        self._log.debug('Update Led %s',payload)

        _device = topic.split('/')[-1]

        _systemStateTemp = False
        if _device == 'SYSTEM_STATE':
            _systemStateTemp = str(payload)

        self._log.debug('System State %s %s'%(self._systemState, _systemStateTemp))

     #   if _device == 'SYSTEM_STATE':

        if 'IDLE' == self._systemState and _systemStateTemp == False:
            self._log.debug('System State in mode IDEL')
            for _item in self._ledDeviceList:
                if _device == _item.deviceId():
                    #      print(str(paylosead))
                    if 'OPEN' == str(payload) or 'UNLOCK' == str(payload):
                        if 'GREEN' == _item.pinState():
                            self._buzzer.TONE1()
                            self._log.info("Change ID %s, change from RED to GREEN", _item.deviceId)
                        _item.setRed()

                    elif 'CLOSE' == str(payload) or 'LOCK' == str(payload):
                        if 'RED' == _item.pinState():
                            self._buzzer.TONE2()
                            self._log.info("Change ID %s, change from GREEN to RED", _item.deviceId)
                        _item.setGreen()
                    else:
                        self._log.error('UNKNOWN Port State')
        elif 'IDLE' != self._systemState and 'IDLE' == _systemStateTemp:
            self._log.info('System State Changed from %s to %s', self._systemState, _systemStateTemp)
            self._buzzer.TONE_OFF()
            self._systemState = _systemStateTemp

        elif 'ARMED' != self._systemState and 'ARMED' == _systemStateTemp:
            # changed system State to ARMED
            self._log.info('System State Changed from %s to %s', self._systemState, _systemStateTemp)
            self._systemState = _systemStateTemp
            self._buzzer.TONE3()
            for _item in self._ledDeviceList:
                _item.setYellow()

        elif 'ALARM' != self._systemState and 'ALARM' == _systemStateTemp:
            self._log.info('System State Changed from %s to %s', self._systemState, _systemStateTemp)
            self._buzzer.TONE_ON()
            self._systemState = _systemStateTemp
            for _item in self._ledDeviceList:
                _item.setRed()

        elif 'PANIC' != self._systemState and 'PANIC' == _systemStateTemp:
            self._log.info('System State Changed from %s to %s', self._systemState, _systemStateTemp)
            self._buzzer.TONE4()
            self._systemState = _systemStateTemp

        return True


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

