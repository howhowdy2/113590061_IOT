from machine import Pin
import time

led = Pin(16, Pin.OUT)
button = Pin(15, Pin.IN, Pin.PULL_UP)

while True:
    led.value(not button.value())
    time.sleep_ms(10)