import network
import socket
from machine import Pin, ADC
import webconfig

led = Pin(webconfig.LED_PIN, Pin.OUT)
sensor_temp = ADC(4)
conversion_factor = 3.3 / 65535
last_temp = None


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(webconfig.SSID, webconfig.PASSWORD)
    while not wlan.isconnected():
        pass
    print("WiFi 已連線，IP:", wlan.ifconfig()[0])


def read_temperature():
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706) / 0.001721
    return round(temperature, 1)


def load_template():
    with open("index.html") as f:
        return f.read()


def web_page():
    led_state = "ON" if led.value() else "OFF"
    temp_html = "<h2>目前溫度: {:.1f} °C</h2>".format(last_temp) if last_temp is not None else ""
    template = load_template()
    return template.format(led_state=led_state, temp_html=temp_html)


def start_server():
    global last_temp
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print("伺服器啟動")
    ...

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()

        if "/led/on" in request:
            led.value(1)
        elif "/led/off" in request:
            led.value(0)
        elif "/temp" in request:
            last_temp = read_temperature()

        response = web_page()
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(response)
        cl.close()


connect_wifi()
start_server()
