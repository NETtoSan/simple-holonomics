# Created by https://github.com/NETtoSan
# This file is for controlling DC motors

import machine
from machine import Pin, PWM


class DCMotor:
    def __init__(self, pin1:int, pin2:int, enable_pin, freq:int=30000, duty:int=1023):
        # For enable_pin, it it's soldered or jumpered.
        # Please leave it alone
        self.pin1 = machine.Pin(pin1, Pin.OUT)
        self.pin2 = machine.Pin(pin2, Pin.OUT)
        self.pwm = machine.PWM(machine.Pin(enable_pin), freq)
        self.duty = duty

    def set_speed(self, pct:int):
        pct = self.map_range(pct, -100, 100, -1 * self.duty, self.duty)
        if pct == 0:
            self.pin1.value(1)
            self.pin2.value(1)
            self.pwm.duty(0)
        elif pct < 0:
            self.pin1.value(1)
            self.pin2.value(0)
            self.pwm.duty(-1 * pct)
        elif pct > 0:
            self.pin1.value(0)
            self.pin2.value(1)
            self.pwm.duty(pct)

    def map_range(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
