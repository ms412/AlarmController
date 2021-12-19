import logging


class StateMachine(object):
    def __init__(self,inputObjectRegister,callback,logger):
        '''
        :param inputObjectRegister: object which created the event
        :param callback: callback to which are stage changes reported
        :param logger: logging modele
        '''
        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + self.__class__.__name__)
        self._log.debug('start Statemachine')

        self._inputObjectRegister = inputObjectRegister
        self._callback = callback

        self._state = self.stateIdle
        self._stateInfo = 'IDLE'
        self._callback('IDLE')
        self._stateChange = [self.changeIdleToArmed,self.changeSabotage,self.changeIdleToPanic]

    def _helperAllItemsInState(self,type,state):
        print('_helperAllItemsInState',type,state)

        _temp = True
        for k, i in self._inputObjectRegister.items():
         #   print(k, i, i.type(), i.state())
            if i.type() == type and i.state() != state:
                print('item unexpected state', i.id())
                _temp = False
        return _temp

    def stateIdle(self):
        self._stateInfo = 'IDLE'
        self._log.info('New State: %s',self._stateInfo)
       # self._log.info('State IDLE')
        #print('state Idle')
        self._stateChange = [self.changeIdleToArmed, self.changeSabotage, self.changeIdleToPanic]
        #self._callback('IDLE')

    def stateAlarm(self):
        self._stateInfo = 'ALARM'
        self._log.info('New State: %s', self._stateInfo)
        self._stateChange =[self.changeAlarmToIdle]
      #  print('ALARM')
    #    self._callback('ALARM')

    def stateArmed(self):
        self._stateInfo = 'ARMED'
        self._log.info('New State: %s',self._stateInfo)
      #  print('state Armed')
        self._stateChange = [self.changeArmedToAlarm,self.changeArmedToIdle]
     #   self._callback('ARMED')

    def stateSabotate(self):
        self._stateInfo = 'SABOTAGE'
        self._log.info('New State: %s',self._stateInfo)
        print('state Saborage')
      #  self._callback('SABOTAGE')

    def statePanic(self):
      #  self._log.info('New State PANIC')
        self._stateInfo = 'PANIC'
        self._log.info('New State: %s',self._stateInfo)
      #  print('state Panic')
        self._stateChange = [self.changePanicToIdle]
       # self._callback('PANIC')

    def changeAlarmToIdle(self,object):
        self._log.info('Alarm to Idle %s, %s'%(object.type(), object.state()))
        if (object.type() == 'RESET' and object.state() == 'ON') or (object.type() == 'LOCK' and object.state() == 'UNLOCK'):
            self._log.info('Change to IDLE')
            self.stateIdle()
        else:
            self._log.info('Failed to change to IDLE')

    def changeArmedToAlarm(self,object):
       # print('changeArmedToAlarm')
        if object.type() == 'ALARMLOOP' or object.type() == 'SABOTAGE':
            if (object.state() == 'OPEN' and object.mode() == 'ACTIVE') or object.state('ON'):
              #  print('ALARM')
                self.stateAlarm()

    def changeIdleToArmed(self,object):
        if object.type() == 'LOCK':
            #if self._helperAllItemsInState('LOCK', 'LOCK') and self._helperAllItemsInState('ALARMLOOP','CLOSE'):
            self._log.info('All LOCK: %s, All ALARMLOOP: %s, All SABOTAGE: %s'%(self._helperAllItemsInState('LOCK','LOCK'),self._helperAllItemsInState('ALARMLOOP','CLOSE'),self._helperAllItemsInState('SABOTAGE','OFF')))
            if self._helperAllItemsInState('LOCK','LOCK') and self._helperAllItemsInState('ALARMLOOP','CLOSE') and self._helperAllItemsInState('SABOTAGE','OFF'):
                self.stateArmed()
            else:
                self._log.debug('Alarm System failed to change to ARMED')

    def changeArmedToIdle(self,object):
      #  print('cahnge ArmedToIdle')
        if object.type() == 'LOCK':
            self._log.debug('Type LOCK in State: %s',object.state())
            if object.state() == 'UNLOCK':
                self.stateIdle()
            else:
                self._log.debug('Failed to change state to IDEL')

    def changeSabotage(self,object):
       # print('changeSboratge')
        if object.type() == 'SABOTAGE':
            self._log.debug('Type SABOTAGE in State: %s',object.state())

    def changeIdleToPanic(self,object):
      #  self._log.debug('Change Idle To Panic ObjectId: %s, Type %s State: %s' % (object.id(), object.type(),object.state()))
        if object.type() == 'PANIC':
            self._log.debug('Type PANIC in State: %s',object.state())
            if object.state() == 'ON':
              #  self._log.info('Change from IDLE to PANIC')
                self.statePanic()
            else:
                self._log.error('State Change not allowed')

    def changePanicToIdle(self,object):
     #   self._log.debug('Change Panic to Idle ObjectId: %s, Type %s, State: %s' % (object.id(), object.type(), object.state()))
        if object.type() == 'RESET':
            if object.state() == 'ON':
                self._log.info('Change from PANIC to IDLE')
                self.stateIdle()

    def update(self,object):
        self._log.info('Current State: %s',self._stateInfo)
        self._log.debug('State changed ID: %s, Type: %s, State: %s' % (object.id(), object.type(), object.state()))

        for item in self._stateChange:
            item(object)
        self._callback(self._stateInfo)

class InputObject(object):
    '''
    config = {'STATE':{True ='ON',False='OFF'},'TYPE': 'PANIC'}
    '''
    def __init__(self,config,callback):
        self._state = 'ON'
        self._type = 'PANIC'

    def id(self):
        return 0

    def state(self):
        return self._state

    def type(self):
        return self._type
