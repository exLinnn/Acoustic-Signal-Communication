# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
import sounddevice as sd
from scipy.signal import argrelextrema
from scipy.signal import correlate
import scipy
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import tkinter.messagebox as messagebox

# 各参数，可以修改
T = 0.025  # 每个符号位的时间，单位s
f = 2000  # 频率
framerate = 48000  # 采样率
recording_time = 35  # 录音时长

# 二进制->ASCII码
def binary_to_ascii(binary_string):
    ascii_string = ''.join(chr(int(binary_string[i:i+8], 2)) for i in range(0, len(binary_string), 8))
    return ascii_string

# 输出成功解码率
def output_success(str1, str2):
    ntotal = len(str1)
    nsuccess = 0
    for i in range(ntotal):
        if str1[i] == str2[i]:
            nsuccess += 1
    print(nsuccess / ntotal)


# QPSK_signal：信号， t：信号时间, 返回信号解调出的二进制字符串
def signal_to_bit(QPSK_signal) -> str:
    t = len(QPSK_signal) / framerate
    # N为该段信号拥有的bit长度
    N = round(t * 2 / T)
    n = int(framerate * T * 2)

    t = [i for i in np.arange(0, N * T, 1 / framerate)]
    bit_t = np.array([i for i in np.arange(0, T, 1 / framerate)])
    I_recover = []
    Q_recover = []
    for i in range(1, int(N / 2) + 1):
        I_output = QPSK_signal[(i - 1) * len(bit_t):i * len(bit_t)] * np.cos(2 * np.pi * f * bit_t)
        if np.sum(I_output) > 0:
            I_recover.append(1)
        else:
            I_recover.append(-1)
        Q_output = QPSK_signal[(i - 1) * len(bit_t):i * len(bit_t)] * np.cos(2 * np.pi * f * bit_t + np.pi / 2)
        if np.sum(Q_output) > 0:
            Q_recover.append(1)
        else:
            Q_recover.append(-1)
    bit_recover = []
    for i in range(1, N + 1):
        if np.mod(i, 2) != 0:
            bit_recover.append(I_recover[int((i - 1) / 2)])
        else:
            bit_recover.append(Q_recover[int(i / 2) - 1])
    recover_data = []
    for i in range(1, N + 1):
        recover_data.extend(bit_recover[i - 1] * np.ones(int(T * framerate)))
    I_recover_data = []
    Q_recover_data = []
    for i in range(1, int(N / 2) + 1):
        I_recover_data.extend(I_recover[i - 1] * np.ones(int(T * framerate * 2)))
        Q_recover_data.extend(Q_recover[i - 1] * np.ones(int(T * framerate * 2)))
    
    bitdata = ""
    I_recover_data = np.array(I_recover_data)
    Q_recover_data = np.array(Q_recover_data)
    for i in range(int(N/2)):
        symbI = I_recover_data[i * n:(i+1)*n]
        bitdata += "1" if np.sum(symbI) > 0 else "0"
        symbQ = Q_recover_data[i * n:(i+1)*n]
        bitdata += "1" if np.sum(symbQ) > 0 else "0"
    
    return bitdata


# 解调入口
def qpsk_demodulation():
    payloads = find_preamble()
    bitdata = ""
    for payload in payloads:
        bitdata += signal_to_bit(payload)
    print(bitdata)
    
    text = binary_to_ascii(bitdata)
    print(text)
    # 调用tkinter的API实现可视化界面
    messagebox.showinfo("解码结果", text)


# 录音
def audio_recording(time):
    fs = 48000
    duration = time  # 录音时间，单位为秒
    print("录制开始！")
    # 录制音频
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)

    # 等待录音结束
    sd.wait()
    print("录制结束！")

    # 录制结果为二维数组，需要处理成一维返回
    recording = recording.T
    return recording[0]


# 滤波
def wave_filter(signal):
    fs = 48000

    lowcut = 1900  # 低频截止频率
    highcut = 2100  # 高频截止频率
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(5, [low, high], btype='band')

    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal


# preamble定位
def find_preamble():
    # 获取preamble波形
    fs, preamble_signal = read('preamble.wav')
    # 录音
    recording = audio_recording(recording_time)
    recording = wave_filter(recording)
    # time = np.arange(0, len(recording))
    # plt.plot(time, recording)
    # plt.show()
    recording = recording.reshape(1, -1)[0]
    # 计算录音信号和preamble信号之间的相关性
    correlations = correlate(recording, preamble_signal, 'valid')

    # t = np.arange(0, len(correlations))
    # plt.plot(t, correlations)
    # plt.show()

    max_corr = np.max(correlations)
    dist = int(framerate * T * 64)
    # 找到相关性峰值
    pos = scipy.signal.find_peaks(correlations, height=0.5*max_corr, distance=dist)[0]

    # 输出最大值的位置
    # print(pos)
    payloads = []
    # 从第一个峰值后面开始就是你的payload
    for i in range(0, len(pos) - 2):
        start, end = pos[i] + len(preamble_signal), pos[i] + len(preamble_signal) + framerate * T * 10 * 4
        payload = recording[start: int(round((end-start)/(framerate*T))*(framerate*T) + start)]
        payloads.append(payload)
    n = len(pos)
    start, end = pos[n - 2] + len(preamble_signal), pos[n - 1]
    payload = recording[start: int(round((end-start)/(framerate*T))*(framerate*T) + start)]
    payloads.append(payload)
    return payloads

if __name__ == '__main__':
    qpsk_demodulation()