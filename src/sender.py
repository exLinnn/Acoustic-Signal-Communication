import numpy as np
import matplotlib.pyplot as plt
import wave
from scipy.io.wavfile import write


# 设置参数
T = 0.025  # 每个符号位的时间，单位s
f = 2000  # 频率
framerate = 48000  # 采样率

QPSK_signal = 0

# ASCII码->二进制
def ascii_to_bits(ascii_string):
    binary_string = ''.join(format(ord(char), '08b') for char in ascii_string)
    return binary_string

# QPSK调制函数
def qpsk_modulation(bitstream):
    bitstream_list = list(bitstream)
    bitstream_int_list = [int(x) for x in bitstream_list]
    bitstream = np.array(bitstream_int_list)
    bitstream = 2 * bitstream - 1
    N = len(bitstream)
    # 原始信号
    I = np.array([])
    Q = np.array([])
    for i in range(1, N + 1):
        if np.mod(i, 2) != 0:
            I = np.insert(I, len(I), bitstream[i - 1])
        else:
            Q = np.insert(Q, len(Q), bitstream[i - 1])
    # 生成调制信号
    bit_t = np.array([])
    for i in np.arange(0, T, 1 / framerate):
        bit_t = np.insert(bit_t, len(bit_t), i)
    # 载波
    I_carrier = np.array([])
    Q_carrier = np.array([])
    for i in range(1, int(N / 2) + 1):
        I_carrier = np.insert(I_carrier, len(I_carrier), I[i - 1] * np.cos(2 * np.pi * f * bit_t))
        Q_carrier = np.insert(Q_carrier, len(Q_carrier), Q[i - 1] * np.cos(2 * np.pi * f * bit_t + np.pi / 2))
    QPSK_signal = I_carrier + Q_carrier
    return QPSK_signal


# 分包程序，将数据分批次传给QPSK调制函数，在拼接得到最终的信号
def all_modulation(ascii_string):
    slices = [ascii_string[i:i+10] for i in range(0, len(ascii_string), 10)]
    preamble = "1"*64
    QPSK_signal = np.array([])
    for i in range(len(slices)):
        s = slices[i]
        ascii_s = ascii_to_bits(s)
        # 加入premable一起调制
        bitstream = preamble + ascii_s
        print(bitstream)
        # 一个包的调制信号
        QPSK_signal = np.insert(QPSK_signal, len(QPSK_signal), qpsk_modulation(bitstream))
        if i == len(slices) - 1: break
        # 空1秒
        QPSK_signal = np.insert(QPSK_signal, len(QPSK_signal), np.zeros(framerate))
    
    # 结尾插入preamble，方便找到最后一个包的范围
    bitstream = preamble
    QPSK_signal = np.insert(QPSK_signal, len(QPSK_signal), qpsk_modulation(bitstream))
    output_wave(QPSK_signal)
    # print(len(QPSK_signal))
    
    return QPSK_signal

# 输出.wav文件
def output_wave(y):
    framerate = 48000
    with wave.open("output.wav", 'wb') as f:
        f.setnchannels(1)  # 通道个数，1为单声道，2为立体声
        f.setsampwidth(2)  # 采样宽度
        f.setframerate(framerate)  # 采样率
        f.setcomptype('NONE', 'not compressed')  # 采样格式，无压缩
        y = y * 32768
        y_data = y.astype(np.int16).tobytes()  # 将类型转为字节
        f.writeframes(y_data)
        f.close()


if __name__ == '__main__':
    text = str(input("请输入字符串："))
    QPSK_signal = all_modulation(text)