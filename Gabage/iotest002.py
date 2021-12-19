from gpiozero import Button
#from signal import pause
import paho.mqtt.client as mqtt
import time

class IO(object):
    def __init__(self,io,id,callback):
        self._io = io
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
        self._callback(self)

    def close(self):
        print('CLOSE')
        self._state= 'CLOSE'
        self._callback(self)

    def state(self):
        return self._state

    def id(self):
        return self._id

class AlarmManager(object):
    def __init__(self):
        '''
        UNLOCKED = no alarm only notify state
        LOCKED = full alarm
        TEST = like LOCKED only FLASH no BELL
        '''
        self._sytemState= 'UNLOCKED'

        self._alarmStripConfig = {}
        self._alarmStripObject = {}

    def config(self):
        config1 = {'ALARMSTRIP': {'KITCHEN' : 4, 'EATING': 17,'BATH':27,'FRONTDOOR':23,'PANIK_SLEEP': 11,'FRONTDOOR': 22,'BACKDOOR':24, 'RESET':10}}
        config2 = {'PANIK':{'SLEEPING': 11}}
        config3 = {'LOCK': {'FRONTDOOR':22, 'BACKDOOR':24}}
        self._alarmStripConfig = config1['ALARMSTRIP']
       # self._panikButtonConfig = config2['PANIK']
        print(config1,self._alarmStripConfig)


    def monitoringStart(self):
        for k,i in self._alarmStripConfig.items():
            print(k,i)
            self._alarmStripObject[k]=IO(i,k,self.updateAlarmStrip)
        print(self._alarmStripObject)

    def updateAlarmStrip(self,object):
        print('update',object)
        print('state',object.id(), object.state())

        if 'LOCK' == self._sytemState:
            print('ALARM')
        elif 'TEST' == self._sytemState:
            print('TEST')

        else:
            print('Notify')
            self.publishMqtt(object.id(), object.state())

    def stateAlarmStrip(self):
        for k,i in self._alarmStripObject.items():
            if 'CLOSE' == i.state():
                return False

        return True

    def statusUpdate(self):
        for k,i in self._alarmStripObject.items():
            self.publishMqtt(i.id(), i.state())



    def publishMqtt(self,path,data):

        _path = 'SMARTHOME/DE/IN/ALARM/' + path
        print(_path)
        mqttc = mqtt.Client()
        mqttc.connect("192.168.2.20")
        mqttc.loop_start()

        mqttc.publish(_path, data)

        print('Done')




    def start(self):
        self.config()
        self.monitoringStart()
        while(True):
            time.sleep(10)
            self.statusUpdate()


if __name__ == "__main__":
    a = AlarmManager()
    a.start()

