import paho.mqtt.subscribe as subscribe

def on_message_print(client, userdata, message):
    print("%s %s" % (message.topic, message.payload))

subscribe.callback(on_message_print, "SMARTHOME/DE/IN/ALARMCONTROLLER01/STATUS/SYSTEM_STATE", hostname="192.168.2.20")

print('terminated')

#https://ch.mathworks.com/help/icomm/ug/subscribe-to-an-mqtt-topic-with-a-callback-function.html