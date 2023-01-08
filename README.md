# SmartHomeServer

This repository contains the Python script for the [SmartHome](https://github.com/Keihar/SmartHome) project.

The script acts like a gateway between the MQTT broker and the [Tellstick Duo](https://productz.com/it/telldus-tellstick-duo/p/y1XxB).

<p align="center">
<img src="https://i.imgur.com/HZ9m1j5.png" alt="drawing" width="800"/>
</p>

### Features

It allows the control of the actuators by publishing `0` and `1` on the topic `~/actuators/ID`, and it allows to get the room temperature and humidity by subscribing to the topics `~/temperature` and `~/humidity`.

It can also manage an heating system, by turning automatically on and off when the room temperature is below or above the target temperature (set on the topic `~/temperature-setpoint`).

The current status of the actuator is reported on the topics `~/actuators/ID/status`, in this way all MQTT clients can subscribe and stay updated about them.

For example, by using the Android app [SmartHome](https://github.com/Keihar/SmartHome) on multiple devices, if we turn on an actuator from device 1, we'll se the switch status updated even on device 2.

In the same way, on `~/temperature-setpoint/status` is published the current setpoint temperature.

Note: in the above examples, `~` represents the prefix of the topic. We used the prefix as we used a public MQTT broker ([test.mosquitto.org](test.mosquitto.org)), and so it can be easy to have some collision with other users, by using common topic names such as `temperature` or `humidity`.

### Library used
- [paho_mqtt](https://pypi.org/project/paho-mqtt/), to communicate with the MQTT broker
- [tellcore-py](https://pypi.org/project/tellcore-py/), to communicate with the Tellstick Duo
- [loguru](https://pypi.org/project/loguru/), to easily print debug information
