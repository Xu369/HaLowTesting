import re
import pandas as pd
import matplotlib.pyplot as plt


def extract_info(filename):
    with open(filename, "r") as file:
        data = file.read()

    # 分割数据块
    blocks = re.findall(
        r"channel (\d+).*?Lost/Total Datagrams\s*(\d+/\d+ \(\d+%\)) sender\s*(\d+/\d+ \(\d+%\)) receiver",
        data,
        re.DOTALL,
    )

    # 存储结果
    results = []
    for block in blocks:
        channel = int(block[0])
        sender_data = re.search(r"(\d+)/(\d+)", block[1])
        receiver_data = re.search(r"(\d+)/(\d+)", block[2])

        if sender_data and receiver_data:
            sender_lost = int(sender_data.group(1))
            sender_total = int(sender_data.group(2))
            receiver_lost = int(receiver_data.group(1))
            receiver_total = int(receiver_data.group(2))

            results.append(
                {
                    "channel": channel,
                    "sender_lost": sender_lost,
                    "sender_total": sender_total,
                    "receiver_lost": receiver_lost,
                    "receiver_total": receiver_total,
                }
            )

    return results


def plot_data(data):
    df = pd.DataFrame(data)

    # 计算丢包率
    df["sender_loss_rate"] = df["sender_lost"] / df["sender_total"] * 100
    df["receiver_loss_rate"] = df["receiver_lost"] / df["receiver_total"] * 100

    # 分组计算平均值
    grouped = df.groupby("channel").mean()

    # 绘制图表
    plt.figure(figsize=(12, 6))
    plt.plot(grouped.index, grouped["sender_loss_rate"], label="Sender Loss Rate (%)")
    plt.plot(
        grouped.index, grouped["receiver_loss_rate"], label="Receiver Loss Rate (%)"
    )

    plt.xlabel("Channel")
    plt.ylabel("Loss Rate (%)")
    plt.title("Packet Loss Rate by Channel")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    filename = "data_5m_GI_frequency_bandwidth.txt"
    results = extract_info(filename)
    plot_data(results)
