import asyncio
import matplotlib
import matplotlib.pyplot as plt
from bleak import BleakClient

matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
matplotlib.rcParams['axes.unicode_minus'] = False

ADDRESS = "2C:CF:67:F1:DD:C3"
TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

xs, ys, zs = [], [], []
done = asyncio.Event()


def notification_handler(sender, data):
    text = data.decode("utf-8").strip()
    if text == "END":
        done.set()
        return
    try:
        x, y, z = map(float, text.split(","))
        xs.append(x)
        ys.append(y)
        zs.append(z)
    except ValueError:
        pass


async def main():
    async with BleakClient(ADDRESS) as client:
        print("已連線，等待資料...")
        await client.start_notify(TX_UUID, notification_handler)
        await done.wait()
        await client.stop_notify(TX_UUID)

    print(f"共收到 {len(xs)} 筆資料，繪圖中...")
    t = range(len(xs))
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(8, 6))
    axes[0].plot(t, xs)
    axes[0].set_ylabel("X")
    axes[1].plot(t, ys)
    axes[1].set_ylabel("Y")
    axes[2].plot(t, zs)
    axes[2].set_ylabel("Z")
    axes[2].set_xlabel("取樣次數")
    fig.suptitle("手機加速度計資料 (X / Y / Z)")
    plt.tight_layout()
    plt.savefig("accel_chart.png")
    plt.show()


asyncio.run(main())