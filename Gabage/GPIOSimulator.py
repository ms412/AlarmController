import time

from library.mqttclient import mqttclient



class RPI(object):
    OUT = 2
    IN = 1
    BCM =99
    def __init__(self):
        self.start_mqtt()
        self._port = {}
        self._state= {}
       # OUT = 2
      #  IN = 1

        for n in range(40):
            _temp ={'STATE': False, 'VALUE': None, 'TYPE':None, 'CALLBACK': False}
            self._port[n]=_temp

        print(self._port)

   # def IN(self):
    #    return True
    def setmode(self,mode):
        return

    def OUT(self):
        return False

    def start_mqtt(self):
        print('Methode: start_mqtt()')
        self._mqtt = mqttclient('test')

        _list = []
        self._cfg_broker={}

        _subscribe = ('RASPBERRY/PORT/RESPONSE/#')
        _callback = self.callbackBrokerResponce

        _list.append({'SUBSCRIBE': _subscribe, 'CALLBACK': _callback})

        _subscribe = ('RASPBERRY/PORT/INTERRUPT/#')
        _callback = self.callbackBrokerInterrupt

        _list.append({'SUBSCRIBE': _subscribe, 'CALLBACK': _callback})


        self._cfg_broker['SUBSCRIPTION'] = _list
        self._cfg_broker['PUBLISH'] = '/TEST'
        self._cfg_broker['HOST'] ='192.168.2.20'
        print(self._cfg_broker)

        (state, message) = self._mqtt.fullclient(self._cfg_broker)
        if state:
            print('mqtt completed with message %s',message)
        else:
            print('Failed to connect: %s',message)

        return False

    def callbackBroker(self,client, userdata, message):
        # topic /CH/GARAGEDOOR/ID{0/1}/FUNCTION{OPEN/CLOSE/LOCK/LIGHT
        print('Methode: callbackBroker called with client: %s userdata: %s message: %s Topic: %s'%(client, userdata, message.payload, message.topic))
        _marantecObj = ''
        _topic = message.topic
        _payload = message.payload.decode()

        _t = _topic.split('/')
       # _objectId = _t[-2]
        _functionId = _t[-1]
      #  print(self._marantecObj, _objectId )
        self.interrupt(_functionId,_payload)
       # _marantecObj.setGarageDoorState(_functionId, _payload)
        return True

    def callbackBrokerResponce(self,client, userdata, message):
        # topic /CH/GARAGEDOOR/ID{0/1}/FUNCTION{OPEN/CLOSE/LOCK/LIGHT
        print('Methode: callbackBrokerRepsonse called with client: %s userdata: %s message: %s Topic: %s'%(client, userdata, message.payload, message.topic))
        _topic = message.topic
        _payload = message.payload.decode()

        _t = _topic.split('/')
       # _objectId = _t[-2]
        _functionId = int(_t[-1])

        if _payload == 'True':
            _payload = 1
        else:
            _payload = 0
      #  print(self._marantecObj, _objectId )
#        self.interrupt(_functionId,_payload)

        self._port[_functionId]['STATE'] = True
        self._port[_functionId]['VALUE'] = _payload
       # if self._port[_functionId]['CALLBACK'] != False:
       #     print('CALLBACK!!!!')
        #    _temp = self._port[_functionId]['CALLBACK']
         #   _temp(_functionId)
       # _marantecObj.setGarageDoorState(_functionId, _payload)
        return True

    def callbackBrokerInterrupt(self, client, userdata, message):
        # topic /CH/GARAGEDOOR/ID{0/1}/FUNCTION{OPEN/CLOSE/LOCK/LIGHT
        print('Methode: callbackBrokerInterrupt called with client: %s userdata: %s message: %s Topic: %s' % (
        client, userdata, message.payload, message.topic))
        _marantecObj = ''
        _topic = message.topic
        _payload = message.payload.decode()

        if _payload == 'True':
            _payload = 1
        else:
            _payload = 0

        _t = _topic.split('/')
        # _objectId = _t[-2]
        _functionId = int(_t[-1])
        #  print(self._marantecObj, _objectId )
        #        self.interrupt(_functionId,_payload)

        self._port[_functionId]['STATE'] = True
        self._port[_functionId]['VALUE'] = _payload
        if self._port[_functionId]['CALLBACK'] != False:
            print('CALLBACK!!!!')
            _temp = self._port[_functionId]['CALLBACK']
            print(_temp, self._port[_functionId])
            _temp(_functionId)
    # _marantecObj.setGarageDoorState(_functionId, _payload)


    def publishmqtt(self,id,msg):
        print(id,msg)
        topic = id
        self._mqtt.publish(topic,msg)

    def setup(self,port,direction):
        _topic = 'RASPBERRY/PORT/SETUP/' + str(port)
        print('00000000000',direction)
        if direction == 1:
           # _payload = direction.split('.')[-1]
            _payload = 'IN'
        else:
            _payload = 'OUT'


        self.publishmqtt(_topic,_payload)
        self._port[port]['TYPE'] = direction

    def output(self,port,value):

        _topic = 'RASPBERRY/PORT/SET/' + str(port)
        if value in ['high','HIGH',1,True]:
            print(value)
            _payload = True
        else:
            _payload = False

        self.publishmqtt(_topic,_payload)

    def input(self,port):
        _topic = 'RASPBERRY/PORT/GET/' + str(port)
        self.publishmqtt(_topic,'')

        self._port[port]['STATE'] = False
        print('fff',self._port[port]['STATE'],self._port[port]['VALUE'])
        time.sleep(0.5)
        while(self._port[port]['STATE']):
            print('ggg',self._port[port]['STATE'],self._port[port]['VALUE'])
            self._port[port]['STATE'] = False

        return self._port[port]['VALUE']

    def add_event_detect(self,port,callback):
        self._port[port]['CALLBACK'] = callback
      #  self.setup(port,'GPIO.IN')
    #    (self,_topic,_payload):
     #   print(_topic,_payload)

    def callme(self,port):
        print('CALLBACK',port, self.input(port))

    def run(self):
     #   GPIO.IN = 0
        self.setup(10,'GPIO.IN')
        self.setup(23,'GPIO.OUT')
        self.add_event_detect(3,'x',self.callme)
        self.output(23,'LOW')
        while(True):
            self.output(23, 'HIGH')
            time.sleep(2)
            self.output(23, 'LOW')
            time.sleep(2)
            print(self.input(10))


if __name__ == "__main__":
    x = RPI()
    x.run()
