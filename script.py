import time

import tellcore.telldus as td
import tellcore.constants as const
import paho.mqtt.client as mqtt

def print_devices(devices):
    print("Number of devices: {}\n".format(len(devices)))
    print("{:<5s} {:<25s} {:<10s} {:<10s} {:<20s} {}".format(
            "ID", "NAME", "STATE", "PROTOCOL", "MODEL", "PARAMETERS"))
    for device in devices:
        cmd = device.last_sent_command(
            const.TELLSTICK_TURNON
            | const.TELLSTICK_TURNOFF
            | const.TELLSTICK_DIM)
        if cmd == const.TELLSTICK_TURNON:
            cmd_str = "ON"
        elif cmd == const.TELLSTICK_TURNOFF:
            cmd_str = "OFF"
        elif cmd == const.TELLSTICK_DIM:
            cmd_str = "DIMMED:{}".format(device.last_sent_value())
        else:
            cmd_str = "UNKNOWN:{}".format(cmd)
        params_str = ""
        for name, value in device.parameters().items():
            params_str += " {}:{}".format(name, value)
        print("{:<5d} {:<25s} {:<10s} {:<10s} {:<20s}{}".format(
                device.id, device.name, cmd_str,
                device.protocol, device.model, params_str))

def print_sensors(sensors):
    print("Number of sensors: {}\n".format(len(sensors)))
    print("{:<15s} {:<15s} {:<5s} {:<8s} {:<8s} {:<18s} {:<20s} {}".format(
            "PROTOCOL", "MODEL", "ID", "TEMP", "HUMIDITY", "RAIN", "WIND",
            "LAST UPDATED"))

    def format_value(sensor, datatype, formatter):
        if not sensor.has_value(datatype):
            return ("", None)
        value = sensor.value(datatype)
        return (formatter(value.value), value.datetime)

    for sensor in sensors:
        values = []
        values.append(format_value(sensor, const.TELLSTICK_TEMPERATURE,
                                   lambda x: "{} C".format(x)))
        values.append(format_value(sensor, const.TELLSTICK_HUMIDITY,
                                   lambda x: "{} %".format(x)))
        values.append(format_value(sensor, const.TELLSTICK_RAINRATE,
                                   lambda x: x + " mm/h "))
        values.append(format_value(sensor, const.TELLSTICK_RAINTOTAL,
                                   lambda x: x + " mm"))
        values.append(format_value(sensor, const.TELLSTICK_WINDDIRECTION,
                                   lambda x: ["N", "NNE", "NE", "ENE",
                                              "E", "ESE", "SE", "SSE",
                                              "S", "SSW", "SW", "WSW",
                                              "W", "WNW", "NW", "NNW"]
                                   [int(float(x) / 22.5)] + " "))
        values.append(format_value(sensor, const.TELLSTICK_WINDAVERAGE,
                                   lambda x: x + " m/s "))
        values.append(format_value(sensor, const.TELLSTICK_WINDGUST,
                                   lambda x: "({} m/s)".format(x)))

        # Get first valid timestamp
        timestamp = [v[1] for v in values if v[1] is not None][0]

        s = [v[0] for v in values]
        values_str = "{:<8s} {:<8s} ".format(s[0], s[1])
        values_str += "{:<18s} ".format(s[2] + s[3])
        values_str += "{:<20s} ".format(s[4] + s[5] + s[6])

        print("{:<15s} {:<15s} {:<5d} {}{}".format(
            sensor.protocol, sensor.model, sensor.id, values_str,
            timestamp))

def sensor_event(protocol, model, id_, dataType, value, timestamp, cid):
    print('Received event ' + str(id_) + ', ' + str(dataType) + ', ' + str(value))

    if dataType == 1:
        print('Temperature: ' + str(value))
    elif dataType == 2:
        print('Humidity: ' + str(value))


def on_message(client, userdata, message):
    print(str(message.payload) + ' - ' + message.topic)

    if message.topic == 'su-dsv/iot22/6-5/actuators/0':
        if message.payload.decode('utf-8') == '1':
            core.devices()[0].turn_on()
        else:
            core.devices()[0].turn_off()
    elif message.topic == 'su-dsv/iot22/6-5/actuators/1':
        if message.payload.decode('utf-8') == '1':
            core.devices()[1].turn_on()
        else:
            core.devices()[1].turn_off()

client = mqtt.Client()
client.connect('test.mosquitto.org')
client.on_message=on_message

# callback dispatcher
dispatcher = td.QueuedCallbackDispatcher()

core = td.TelldusCore(callback_dispatcher=dispatcher)
core.register_sensor_event(sensor_event)

print_devices(core.devices())
print("")
print_sensors(core.sensors())

while True:
    #core.devices()[0].turn_on()
    #time.sleep(5)
    #core.devices()[0].turn_off()
    #print_sensors(core.sensors())
    core.callback_dispatcher.process_pending_callbacks()
    time.sleep(30)
