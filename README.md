# README

## 程序结构

-   `sender.py`：发送端代码，输入待发送的 ASCII 字符，输出名为`output.wav`的文件。
-   `receiver.py`：接收端代码，运行代码开始监听，在录制时间结束后自动停止，在命令行中输出解码的二进制结果与 ASCII 字符结果，并将解码的 ASCII 字符通过可视化弹窗进行弹出。
-   `preamble.wav`：是`receiver.py`的依赖文件，保存了 preamble 的波形数据，便于相关性计算。

## 使用方法

-   首先在发送端设备上运行发送端代码，输入待发送字符串。当`output.wav`文件生成后，程序执行结束；
-   在接收端设备上运行`receiver.py`代码进行监听；
-   在发送端设备上播放`output.wav`；
-   监听结束，弹出解码结果。

## 注意事项

-   程序使用 Python3 运行，运行前需要安装 wave 处理、数据分析等包，如果运行中发现包找不到可以调用`pip install package-name`进行安装。
-   程序中有可调参数，包括每个符号位时间 T，频率 f，采样率 framerate，录音时间 recording_time，可根据需求进行调整。相关性检测中也有相关参数，可以调整相关性峰间距，峰阈值等，详见`scipy.signal.find_peaks`的参数说明。
