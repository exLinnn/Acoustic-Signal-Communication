# README

本项目实现了基于声波的通讯系统，可以在两台设备之间传递任意长度 ASCII 字符串。

## 程序结构

-   `sender.py`：发送端代码，输入待发送的 ASCII 字符，输出名为`output.wav`的文件。
-   `receiver.py`：接收端代码，运行代码开始监听，在录制时间结束后自动停止，在命令行中输出解码的二进制结果与 ASCII 字符结果，并将解码的 ASCII 字符通过可视化弹窗进行弹出。
-   `preamble.wav`：是`receiver.py`的依赖文件，保存了 preamble 的波形数据，便于相关性计算。

## 使用方法

-   首先在发送端设备上运行发送端代码，输入待发送字符串。当`output.wav`文件生成后，程序执行结束；
-   在接收端设备上运行`receiver.py`代码进行监听；
-   在发送端设备上播放`output.wav`；
-   监听结束，弹出解码结果。
