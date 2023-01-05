import time

import tellcore.telldus as td
import tellcore.constants as const
import paho.mqtt.client as mqtt

from loguru import logger

MQTT_BROKER = 'test.mosquitto.org'
MQTT_BASE_TOPIC = 'su-dsv/iot22/6-5/'

HYSTERESIS = 0.3

current_temperature = 0
temperature_setpoint = 0

### START TELLDUS SECTION
def get_temperature():
    for sensor in core.sensors():
        if str(sensor.id == 135):
            return sensor.value(const.TELLSTICK_TEMPERATURE).value

    return '0'

def get_humidity():
    for sensor in core.sensors():
        if str(sensor.id == 135):
            return sensor.value(const.TELLSTICK_HUMIDITY).value

    return '0'

def sensor_event(protocol, model, id_, dataType, value, timestamp, cid):
    logger.debug('Received event ' + str(id_) + ', ' + str(dataType) + ', ' + str(value))

    if id_ == 135:
        if dataType == 1:
            on_receive_real_temperature(value)
        elif dataType == 2:
            on_receive_real_humidity(value)

### START MQTT SECTION
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.debug('Connection established. Code: ' + str(rc))
    else:
        logger.debug('Connection failed. Code: ' + str(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.debug('Unexpected disconnection. Code: ', str(rc))
    else:
        logger.debug('Disconnected. Code: ' + str(rc))

def on_publish(client, userdata, mid):
    logger.debug('Published: ' + str(mid))

def on_log(client, userdata, level, buf):
    logger.debug('MQTT Log: ' + str(buf))

def on_message(client, userdata, message):
    global temperature_setpoint

    logger.debug('Message received: ' + str(message.payload) + ', on topic ' + message.topic)

    if message.topic == MQTT_BASE_TOPIC + 'actuators/0':
        if message.payload.decode('utf-8') == '1':
            core.devices()[0].turn_on()
            client.publish(MQTT_BASE_TOPIC + 'actuators/0/status', '1', retain=True)
        else:
            core.devices()[0].turn_off()
            client.publish(MQTT_BASE_TOPIC + 'actuators/0/status', '0', retain=True)
    elif message.topic == MQTT_BASE_TOPIC + 'actuators/1':
        if message.payload.decode('utf-8') == '1':
            core.devices()[1].turn_on()
            client.publish(MQTT_BASE_TOPIC + 'actuators/1/status', '1', retain=True)
        else:
            core.devices()[1].turn_off()
            client.publish(MQTT_BASE_TOPIC + 'actuators/1/status', '0', retain=True)
    elif message.topic == MQTT_BASE_TOPIC + 'temperature-setpoint':
        temperature_setpoint = float(message.payload)
        client.publish(message.topic + '/status', str(temperature_setpoint))

### OTHER FUNCTIONS
def on_receive_real_temperature(value):
    global current_temperature

    logger.debug('Received real temperature: ' + value)
    current_temperature = float(value)
    client.publish(MQTT_BASE_TOPIC + 'temperature', value, retain=True)

def on_receive_real_humidity(value):
    logger.debug('Received real humidity: ' + value)
    client.publish(MQTT_BASE_TOPIC + 'humidity', value, retain=True)

# Create the MQTT client, register for the events and connect to the MQTT_BROKER
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_log = on_log
client.on_message=on_message
client.connect(MQTT_BROKER)

# Create Tellstick callback dispatcher
dispatcher = td.QueuedCallbackDispatcher()

# Create Telldus Core and register for events
core = td.TelldusCore(callback_dispatcher=dispatcher)
core.register_sensor_event(sensor_event)

# Gest last temperature and humidity reported, and publish to the MQTT MQTT_BROKER
on_receive_real_temperature(get_temperature())
on_receive_real_humidity(get_humidity())

# Publish the initial temperature setopoint
client.publish(MQTT_BASE_TOPIC + 'temperature-setpoint', temperature_setpoint, retain=True)

try:
    while True:
        # process Telldus events
        core.callback_dispatcher.process_pending_callbacks()

        if current_temperature > (temperature_setpoint + HYSTERESIS):
            # turn off the heating if the current temperature is higher than the target temperature more the hysteresis offset
            core.devices()[2].turn_off()
            client.publish(MQTT_BASE_TOPIC + 'actuators/2/status', '0', retain=True)
        elif current_temperature < (temperature_setpoint - HYSTERESIS):
            # turn on the heating if the current temperature is lower than the target temperature minus the hysteresis offset
            core.devices()[2].turn_on()
            client.publish(MQTT_BASE_TOPIC + 'actuators/2/status', '1', retain=True)

        time.sleep(0.5)
except KeyboardInterrupt:
    pass
