import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

#這邊我留空了
WIFI_SSID = ""
WIFI_PASSWORD = ""

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = b"pico/ntut113gp2/led/control"
CLIENT_ID = b"ntut_113_gorupe2_hw2_led"

led = Pin(16, Pin.OUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print("連線中")
            time.sleep(1)
    print("已連線:", wlan.ifconfig()[0])

def on_message(topic, msg):
    cmd = msg.decode().strip().lower()
    print("收到:", cmd)
    if cmd == "on":
        led.value(1)
    elif cmd == "off":
        led.value(0)

connect_wifi()

client = MQTTClient(CLIENT_ID, BROKER, port=PORT, keepalive=60)
client.set_callback(on_message)
client.connect()
client.subscribe(TOPIC)
print("已訂閱", TOPIC)

while True:
    client.check_msg()
    time.sleep_ms(50)