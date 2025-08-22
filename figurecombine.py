import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# 读取文件夹里的两路实验数据（channel A、channel B），把分段的采样点拼成完整时序
# 画出两条响应曲线图， 比较两个通道随时间的电压变化
def generate_fig(folderpath):
    dfA = pd.read_csv(os.path.join(folder_path, 'channelA.csv'), header=None, skiprows=1)
    dfB = pd.read_csv(os.path.join(folder_path, 'channelB.csv'), header=None, skiprows=1)

    y1 = dfA[0]
    y2 = dfB[0]
    t = 1
    while t <= 212:
        y1t = dfA[t]
        y2t = dfB[t]
        y1 = pd.concat([y1, y1t])
        y2 = pd.concat([y2, y2t])
        t += 1
    x = range(0, len(y1) * 25, 25)

    plt.figure(figsize=(10, 5))
    plt.plot(x, y1, label='ChannelA', color='b')
    plt.plot(x, y2, label='ChannelB', color='r')

    plt.title('response curve')
    plt.xlabel('time(ns)')
    plt.ylabel('response voltage(mv)')
    plt.legend()
    plt.grid()

    plt.show()


##change parameter and call function here
folder_path = "new/MgCl2/01/A"
t = 3
generate_fig(folder_path)
