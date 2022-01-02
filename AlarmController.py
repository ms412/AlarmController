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


__app__ = "Alarm Controller"
__VERSION__ = "0.6"
__DATE__ = "10.11.2021"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2021 Markus Schiesser"
__license__ = 'GPL v3'

import sys
import os
import time
import json
import logging
import uuid
import RPi.GPIO as GPIO

from configobj import ConfigObj

from library.mqttclient import mqttclient
from library.logger import loghandler
from library.alarmObject import inputObject
#from library.GPIOSimulator import RPI as GPIO

from library.stateMachine import StateMachine
#from library.alarmManager import Interface
#from library.S0Manager import S0manager

#class manager(threading.Thread):
class AlarmController(object):

    def __init__(self,configfile='AlarmController.config'):
    #    threading.Thread.__init__(self)

        self._configfile = os.path.join(os.path.dirname(__file__),configfile)
        print(self._configfile)

        self._configBroker =  None
        self._configLog = None
        self._configInput = None
        self._configOutput = None

        self._mqtt = None

        _watchdogID = uuid.uuid1()
        self._watchdogTopic = 'WATCHDOG/' + str(_watchdogID)

        self._rootLoggerName = ''

        self._systemState = 'UNKNOWN'
        self._inputObjectRegister = {}

    def readConfig(self):

        _config = ConfigObj(self._configfile)

        if bool(_config) is False:
            print('ERROR config file not found',self._configfile)
            sys.exit()
            #exit

        self._configBroker = _config.get('BROKER',None)
        self._configLog = _config.get('LOGGING',None)
        self._configInput = _config.get('INPUT',None)
        self._configOutput = _config.get('OUTPUT',None)
      #  self._cfg_msgAdapter = _cfg.get('BROKER',None)
        return True

    def startLogger(self):
       # self._log = loghandler('marantec')

        self._configLog['DIRECTORY'] = os.path.dirname(__file__)
        self._root_logger = loghandler(self._configLog.get('NAME','ALARMCONTROLLER'))
        self._root_logger.handle(self._configLog.get('LOGMODE','PRINT'),self._configLog)
        self._root_logger.level(self._configLog.get('LOGLEVEL','DEBUG'))
        self._rootLoggerName = self._configLog.get('NAME',self.__class__.__name__)
        self._log = logging.getLogger(self._rootLoggerName + '.' + self.__class__.__name__)

        self._log.info('Start %s, %s'%(__app__,__VERSION__))

        return True

    def startMqttBroker(self):
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

    def brokerCallback(self):
        pass

    def startStateMaschine(self):
        self._stateMaschine = StateMachine(self._inputObjectRegister, self.callbackStateMaschine,self._rootLoggerName)

    def startInputInterface(self):
        print(self._configInput)
        gpioObject = GPIO

        for key1,item1 in self._configInput.items():
            item1['ID'] = key1

            self._inputObjectRegister[key1]= inputObject(item1,gpioObject,self.inputcallback,self._rootLoggerName)

    def inputcallback(self,object,state):
       # print(object.id(),object.type(),object.io(),state)
        self._log.info('Object: %s, Tpye: %s IO: %d , State: %s'%(object.id(),object.type(),object.io(),state))
        self._stateMaschine.update(object)
        return True

    def callbackStateMaschine(self,state):
        self._log.info('Update System State from: %s to: %s'%(self._systemState,state))
        for key, item  in self._inputObjectRegister.items():
            self._log.info('%s : %s'%(key,item.state()))

        self._systemState = state
        self.publishUpdate()
        return True

    def publishUpdate(self):
        self._log.debug('Send Update State')
        _configTopic = self._configBroker.get('PUBLISH','/SMARTHOME/DEFAULT')

        _topic = _configTopic + '/' + 'SYSTEM_STATE'
        #self._log.info('SYSTEM_STATE: %s'%(self._systemState))
        self._mqtt.publish(_topic, self._systemState)

        for key, item  in self._inputObjectRegister.items():
            _payload = item.state()
            if _payload is None:
                _payload = 'UNKNOWN'
            _topic = _configTopic + '/' + key
        #    self._log.info('%s : %s'%(key,_payload))
          #  print(_topic, item.state(), type(item.state()))
            self._mqtt.publish(_topic,item.state())


        return True

    def start(self):
        self.readConfig()
        self.startLogger()
        self.startMqttBroker()
        self.startStateMaschine()
        self.startInputInterface()
      #  self.monitoringStart()
        while(True):
            time.sleep(15)
            self.publishUpdate()
           # self.inputcallback()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
     #   configfile = '/opt/alarm/AlarmController.config'
        configfile = './AlarmController.config'

    a = AlarmController(configfile)
    a.start()