import machine
import utime

led_onbored = machine.Pin(16, machine.Pin.OUT)

while True:
    led_onbored.value(1)
    utime.sleep(0.5)
    led_onbored.value(0)
    utime.sleep(0.5)