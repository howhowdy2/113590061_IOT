#第1題
import bluetooth
import time
from machine import Pin

UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_NOTIFY,)
UART_SERVICE = (UART_UUID, (UART_TX,),)

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

connections = set()
ble = None
tx_handle = None


def START_BLE():
    ble = bluetooth.BLE()
    ble.active(True)
    ((tx_handle,),) = ble.gatts_register_services((UART_SERVICE,))
    return ble, tx_handle


def advertise(ble):
    name = b"PICO2W"

    payload = bytearray()
    payload += bytes((2, 0x01, 0x06))
    payload += bytes((len(name) + 1, 0x09))
    payload += name

    uuid = bytes(UART_UUID)
    payload += bytes((len(uuid) + 1, 0x07))
    payload += uuid

    ble.gap_advertise(100_000, adv_data=payload)
    print("BLE advertising as PICO2W...")


def irq(event, data):
    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, addr_type, addr = data
        connections.add(conn_handle)
        print("BLE connected")
        print("connection:", conn_handle)

    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle, addr_type, addr = data
        connections.discard(conn_handle)
        print("BLE disconnected")
        advertise(ble)


if __name__ == "__main__":
    button = Pin(18, Pin.IN, Pin.PULL_UP)

    ble, tx_handle = START_BLE()
    ble.irq(irq)
    advertise(ble)

    print("System ready")
    last_state = button.value()

    while True:
        current_state = button.value()

        if current_state != last_state:
            if current_state == 0:
                data = b"1"
            else:
                data = b"0"
            last_state = current_state

            for conn_handle in connections:
                try:
                    ble.gatts_notify(conn_handle, tx_handle, data)
                except Exception as e:
                    print("Notify error:", e)
        time.sleep_ms(50)