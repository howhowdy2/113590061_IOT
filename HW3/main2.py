#第2題
import bluetooth

UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_NOTIFY,)
UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_WRITE,)
UART_SERVICE = (UART_UUID, (UART_TX, UART_RX),)

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

connections = set()
ble = None
tx_handle = None
rx_handle = None


def START_BLE():
    ble = bluetooth.BLE()
    ble.active(True)
    ((tx_handle, rx_handle),) = ble.gatts_register_services((UART_SERVICE,))
    return ble, tx_handle, rx_handle


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

    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle, addr_type, addr = data
        connections.discard(conn_handle)
        print("BLE disconnected")
        advertise(ble)

    elif event == _IRQ_GATTS_WRITE:
        conn_handle, attr_handle = data
        if attr_handle == rx_handle:
            msg = ble.gatts_read(rx_handle)
            try:
                print("收到手機訊息:", msg.decode("utf-8"))
            except UnicodeDecodeError:
                print("收到 bytes:", msg)


if __name__ == "__main__":
    ble, tx_handle, rx_handle = START_BLE()
    ble.irq(irq)
    advertise(ble)

    print("System ready, 等待手機連線 (Bluefruit Connect App -> UART)...")

    while True:
        pass