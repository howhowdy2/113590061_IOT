import bluetooth
import struct
import time

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

samples = []
rx_buf = b""
stage = "collect"  # collect -> send
connect_time = None
sent = False


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
    print("BLE advertising as PICO2W... stage =", stage)


def parse_accel_packet(data):
    if len(data) < 15 or data[0:1] != b"!" or data[1:2] != b"A":
        return None
    x, y, z = struct.unpack("<fff", data[2:14])
    return x, y, z


def irq(event, data):
    global stage, rx_buf, connect_time, sent

    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, addr_type, addr = data
        connections.add(conn_handle)
        print("BLE connected, stage =", stage)
        if stage == "send":
            connect_time = time.ticks_ms()

    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle, addr_type, addr = data
        connections.discard(conn_handle)
        print("BLE disconnected, stage =", stage)
        if stage == "collect":
            stage = "send"
            print("共收集 {} 筆資料，切換成等電腦連線".format(len(samples)))
        advertise(ble)

    elif event == _IRQ_GATTS_WRITE:
        conn_handle, attr_handle = data
        if attr_handle == rx_handle and stage == "collect":
            rx_buf = rx_buf + ble.gatts_read(rx_handle)
            while len(rx_buf) >= 15:
                if rx_buf[0:1] != b"!":
                    rx_buf = rx_buf[1:]
                    continue
                packet = bytes(rx_buf[:15])
                result = parse_accel_packet(packet)
                rx_buf = rx_buf[15:]
                if result:
                    samples.append(result)


if __name__ == "__main__":
    ble, tx_handle, rx_handle = START_BLE()
    ble.irq(irq)
    advertise(ble)
    print("System ready, 等待手機連線 (Bluefruit Connect -> Controller -> 加速度計)...")

    while True:
        if (stage == "send" and connections and not sent
                and connect_time is not None
                and time.ticks_diff(time.ticks_ms(), connect_time) > 20000):
            for x, y, z in samples:
                line = "{:.3f},{:.3f},{:.3f}\n".format(x, y, z).encode("utf-8")
                for conn_handle in connections:
                    try:
                        ble.gatts_notify(conn_handle, tx_handle, line)
                    except Exception as e:
                        print("Notify error:", e)
                time.sleep_ms(20)
            for conn_handle in connections:
                ble.gatts_notify(conn_handle, tx_handle, b"END\n")
            sent = True
            print("傳送完成")
        time.sleep_ms(50)