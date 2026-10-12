import asyncio
from bleak import BleakClient

ADDRESS = "2C:CF:67:F1:DD:C3"
TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

count = 0


def notification_handle(sender, data):
    global count
    if data == b"1":
        count += 1
        print("目前計數:", count)


async def main():
    async with BleakClient(ADDRESS) as client:
        print("connected!")
        await client.start_notify(TX_UUID, notification_handle)
        while True:
            await asyncio.sleep(1)


asyncio.run(main())
