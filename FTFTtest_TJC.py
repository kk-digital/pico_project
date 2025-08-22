# coding=gbk
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram


def load_channel_data(folder_path, col_index):
    """��ȡָ���ļ����е� channelA �� channelB ������"""
    dfA = pd.read_csv(os.path.join(folder_path, 'channelA.csv'))
    dfB = pd.read_csv(os.path.join(folder_path, 'channelB.csv'))
    A = dfA.iloc[:, col_index].values
    B = dfB.iloc[:, col_index].values
    return A, B, dfA


def extract_parameters(df):
    """�������ļ������б�������ȡʵ�����"""
    title = df.columns[0]
    pairs = title.split(',')
    params = {}
    for pair in pairs:
        key, value = pair.split('=')
        params[key] = int(value)
    return params


def compute_spectrogram(signal, fs, window_size):
    """����Ƶ��ͼ"""
    return spectrogram(signal, fs, nperseg=window_size)


def plot_spectrogram(times, freqs, Sxx, title, params, window_size, ylim=None, dB=True):
    """���Ƶ�ͨ��Ƶ��ͼ"""
    plt.pcolormesh(times, freqs,
                   10 * np.log10(Sxx) if dB else Sxx,
                   shading='gouraud')
    plt.colorbar(label='Intensity (dB)' if dB else 'Intensity')
    plt.title(title)
    plt.ylabel('Frequency (Hz)')
    if ylim:
        plt.ylim(0, ylim)
    plt.grid()

    # ��ͼ��Ƕ�������Ϣ
    plt.text(-0.3, 0.5,
             f"WG Frequency: {params['f']} Hz\n"
             f"Wavelet Type: {params['type']}\n"
             f"Wavelet A={params['A']}, B={params['B']}, C={params['C']}\n"
             f"Sampling Interval: 25 ns\n"
             f"FTFT window size: {window_size}",
             horizontalalignment='center', verticalalignment='center',
             transform=plt.gca().transAxes, fontsize=10,
             bbox=dict(facecolor='white', alpha=0.5, edgecolor='black'))


def analyze_signals(folder_path, col_index=200, window_size=100, ylim=2e6):
    """������������·�źż�����źŽ���ʱƵ��������ͼ"""
    # ��ȡ����
    A, B, dfA = load_channel_data(folder_path, col_index)
    params = extract_parameters(dfA)
    fs = 1 / (25e-9)  # ����Ƶ��

    # ͨ�� A��B
    fA, tA, SxxA = compute_spectrogram(A, fs, window_size)
    fB, tB, SxxB = compute_spectrogram(B, fs, window_size)

    # ���� dB ��ʽƵ��
    plt.figure(figsize=(12, 10))
    plt.subplot(2, 1, 1)
    plot_spectrogram(tA, fA, SxxA, 'Spectrogram of ChannelA (solution)',
                     params, window_size)
    plt.subplot(2, 1, 2)
    plot_spectrogram(tB, fB, SxxB, 'Spectrogram of ChannelB (series resistor)',
                     params, window_size)
    plt.tight_layout()
    plt.show()

    # ����ԭʼǿ��Ƶ��
    plt.figure(figsize=(12, 10))
    plt.subplot(2, 1, 1)
    plot_spectrogram(tA, fA, SxxA, 'ChannelA (solution) - Linear Intensity',
                     params, window_size, ylim=ylim, dB=False)
    plt.subplot(2, 1, 2)
    plot_spectrogram(tB, fB, SxxB, 'ChannelB (series resistor) - Linear Intensity',
                     params, window_size, ylim=ylim, dB=False)
    plt.tight_layout()
    plt.show()

    # ����ź� A-B
    fD, tD, SxxD = compute_spectrogram(A - B, fs, window_size)
    plt.figure(figsize=(10, 6))
    plot_spectrogram(tD, fD, SxxD, 'Spectrogram of Difference (A-B)',
                     params, window_size, ylim=ylim, dB=False)
    plt.xlabel('Time (s)')
    plt.show()


# ================== ʹ��ʾ�� ==================
if __name__ == "__main__":
    folder_path = "new/MgCl2/1/A"
    analyze_signals(folder_path, col_index=200, window_size=100, ylim=2e6)
