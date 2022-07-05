
import logging
from Gabage.inputDevice import Input
from library.stateMachine import StateMachine
import paho.mqtt.client as mqtt


class AlarmManager(object):

    def __init__(self,config,logger):

        _libName = str(__name__.rsplit('.', 1)[-1])
       # print(__name__,_libName,logger)
      #  self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)
        self._log = logging.getLogger(logger + '.' + self.__class__.__name__)
        #  print(self._log)
        #  time.sleep(3)
        self._log.debug('Start instance of Interface object')

        self._config = config
      #  print(config)
        '''
        UNLOCKED = no alarm only notify state
        LOCKED = full alarm
        TEST = like LOCKED only FLASH no BELL
        '''
        self._stateMachine = StateMachine()

        self._alarmObject = {}
        self._lockObject = {}
        self._panikObject = {}
        self._resetObject = {}

    def startInterface(self):
        _temp ={}
        _counter =0
        _temp = {'INTERFACE': 0, 'NAME': None, 'TYPE': None, 'MODE': 'ACTIVE',True:'ON',False:'OFF'}
        for k,i in self._config.items():
            try:
                _temp['NAME']=k
                _temp['INTERFACE'] = i[0]
                _temp['TYPE'] = i[1]
                _temp[True] = i[2]
                _temp[False] = i[3]
                _temp['MODE'] = i[4]
            except:
                _temp['MODE'] = None

            if 'STRIP' == i[1]:
                self._alarmObject[k] = inputObject(_temp, self._stateMachine.update)
            elif 'LOCK' == i[1]:
                self._lockObject[k] = LockObject(i[0],k,self.updateLock)
            elif  'PANIK' == i[1]:
                self._panikObject[k] = Input(i[0],k,self.updateLock)
            elif 'RESET' == i[1]:
                self._resetObject[k] = Input(i[0],k,self.updateReset)
            self._log.info('start object %s %s'%(k,i))


    def updateAlarm(self,object):
        #print('update', object)
        #print('state', object.id(), object.state())
        self._log.info('ALARM state changed %s %s'%(object.id(),object.state()))

        if self._systemState == 'UNLOCKED':
            print('state change')
        elif self._systemState == 'LOCKED':

            self._alarmState = 'ALARM'
            self._alarmCondition = 'BURGLARY'
            self._log.info(self._alarmState, self._alarmCondition)

        self.publishMqtt(object.id(), object.state())

    def updateLock(self,object):
        self._log.info('LOCK state changed %s %s' % (object.id(), object.state()))

        _temp = True
        for k,i in self._lockObject:
            if 'LOCKED' != i.state():
                _temp = False

        if _temp:
            self._systemState = 'LOCKED'
        else:
            self._systemState = 'UNLOCKED'
            self._alarmState = 'NO ALARM'
            self._alarmCondition = 'NONE'

        return True

    def updatePanik(self,object):
        self._log.info('Panik state changed %s %s' % (object.id(), object.state()))

        _temp = True
        for k,i in self._panikObject:
            if 'ACTIVE' != i.state():
                _temp = False

        if _temp:
            self._alarmState = 'ALARM'
            self._alarmCondition = 'PANIK'

        return True

    def updateSabotage(self,object):
        self._log.info('Sabotage state changed %s %s' % (object.id(), object.state()))

        _temp = True
        for k,i in self._panikObject:
            if 'ACTIVE' != i.state():
                _temp = False

        if _temp:
            self._alarmState = 'ALARM'
            self._alarmCondition = 'SABOTAGE'

        return True

    def updateReset(self):
        self._log.info('Reset state changed %s %s' % (object.id(), object.state()))

        self._alarmState = 'NO ALARM'
        self._alarmCondition = 'NONE'

        return True


    def stateAlarm(self):
        _temp = {}
        for k,i in self.self._alarmObject.items():
            if 'ACTIVE' == i[2]:
                _temp[k]=i[0]

    def state(self,object):
        for k, i in object.items():
            if 'CLOSE' == i.state():
                return False

        return True

    def statusUpdate(self):
        for k, i in self._alarmObject.items():
            self.publishMqtt(i.id(), i.state())

    def publishMqtt(self, path, data):

        _path = 'SMARTHOME/DE/IN/ALARM/' + path
        #print(_path)
        mqttc = mqtt.Client()
        mqttc.connect("192.168.2.20")
        mqttc.loop_start()

        mqttc.publish(_path, data)


class Manager(object):

    def __init__(self):
        pass

    def normalState(self):