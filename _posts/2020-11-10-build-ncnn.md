---
layout:     post
title:      Tutorial for Compiling the NCNN Library
subtitle:   The first step to deploying a deep learning model
date:       2020-11-10
author:     Zekun
header-img: img/headers/post-deep-brain.jpg
catalog: true
tags:
    - NCNN
    - Deep Learning
    - C++
---

This is a tutorial for compiling the NCNN library. The content comes from my attempts to complete the Mask-Detection project, so the process is based on the Yolo-Fastest model. I hope it will help readers deploy the model, and also help me quickly rebuild the environment in the future.

According to the author nihui, the name of NCNN comes from (New/Next or Naive or Neon or Nihui) + CNN. This is the introduction on [its GitHub repository](https://github.com/Tencent/ncnn):

> ncnn is a high-performance neural network inference computing framework optimized for mobile platforms. ncnn is deeply considerate about deployment and uses on mobile phones from the beginning of design. ncnn does not have third party dependencies. it is cross-platform, and runs faster than all known open source frameworks on mobile phone cpu.

In addition to its excellent optimization for mobile devices, its lack of third-party library dependencies also means that there are fewer restrictions on model deployment. However, the process of compiling NCNN still requires several third-party libraries.

1. g++ & gcc
2. cmake
3. protobuf
4. opencv

The following content is based on Ubuntu 18.04.5. I also tried macOS, but after encountering various problems caused by clang instead of g++, I chose to switch environments.

## g++ & gcc

Usually, Ubuntu has these tools built in. You can use the following code in the terminal to check the installed version:

```bash
g++ -v
```

Or you can install it via `apt`.

```bash
sudo apt install gcc
sudo apt install g++
```

## cmake

Similar to the previous one, we can still use `apt`.

```bash
sudo apt install cmake
```

## Protobuf

The installation of protobuf can be done according to the instructions in its GitHub repository. The key steps are as follows.

```bash
sudo apt-get install autoconf automake libtool curl make g++ unzip
```

Then download the package from its release page:

[https://github.com/protocolbuffers/protobuf/releases/latest](https://github.com/protocolbuffers/protobuf/releases/latest)

The one I downloaded is [protobuf-all-3.14.0.tar.gz](https://github.com/protocolbuffers/protobuf/releases/download/v3.14.0/protobuf-all-3.14.0.tar.gz). Then unzip the package and enter the folder in the terminal. Run the following code.

```bash
./configure
 make
 make check
 sudo make install
 sudo ldconfig # refresh shared library cache.
```

**Hint:** If protobuf is installed successfully but some errors are reported when compiling NCNN, you can try restarting Ubuntu. If you still cannot compile NCNN normally, you can recompile and install protobuf before restarting.

## OpenCV

Open [https://opencv.org/releases/](https://opencv.org/releases/) and select an appropriate version. I installed OpenCV-3.4.12. Click **Sources** to download the package.

Then unzip the package and enter the folder in the terminal. Run the following code to install the dependencies.

```bash
sudo apt-get install build-essential libgtk2.0-dev libavcodec-dev libavformat-dev libjpeg.dev libtiff4.dev libswscale-dev libjasper-dev
```

Create a build folder under this folder, then run cmake.

```bash
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local ..
```

Then start to compile it.

```bash
sudo make
sudo make install
```

Add the OpenCV library to the path so that the system can find it.

```bash
sudo gedit /etc/ld.so.conf.d/opencv.conf
```

This command opens a file. Add `/usr/local/lib` at the end of the file and save it. Running the following command makes the configuration path effective.

```bash
sudo ldconfig
```

The following command will open a file.

```bash
sudo gedit /etc/bash.bashrc
```

Add these at the end of the file and save it:

```bash
PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib/pkgconfig  
export PKG_CONFIG_PATH
```

Executing this command makes the configuration path effective.

```bash
source /etc/bash.bashrc
sudo updatedb
```

The configuration process of OpenCV has been completed. Let's test it with its own tools.

Enter `opencv-3.4.12/samples/cpp/example_cmake` in the terminal.
Execute the following code:

```bash
cmake .
make
./opencv_example
```

If the camera is automatically turned on, and a `hello opencv` appears in the upper left corner of the image captured by the camera, it means that the configuration is successful.

## NCNN

Now that the dependent libraries have been installed, we will start to compile NCNN. You can find the official tutorial [here](https://github.com/Tencent/ncnn/wiki/how-to-build#build-for-linux).

If you want to use GPU, please install Vulkan as a dependency with the following code.

```bash
wget https://sdk.lunarg.com/sdk/download/1.2.154.0/linux/vulkansdk-linux-x86_64-1.2.154.0.tar.gz?Human=true -O vulkansdk-linux-x86_64-1.2.154.0.tar.gz
tar -xf vulkansdk-linux-x86_64-1.2.154.0.tar.gz
export VULKAN_SDK=$(pwd)/1.2.154.0/x86_64
```

However, because I am using a virtual machine running on a MacBook Pro, I chose to skip Vulkan. If you choose to do so, please remember to set the Vulkan option to OFF.

Then we need to clone the NCNN repository and start compiling it.

```bash
git clone https://github.com/Tencent/ncnn.git
cd ncnn
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DNCNN_VULKAN=ON -DNCNN_SYSTEM_GLSLANG=ON -DNCNN_BUILD_EXAMPLES=ON ..
make
make install
```

So far, the compilation process of NCNN has been completed. It is recommended to carefully read the official documents and issues on GitHub when compiling; you can find many solutions to errors there.

After this, we can start to use various tools in the `ncnn/build/tools` folder to help us convert the model.

For example, you can copy the **.cfg** and .**weights** files of your Darknet model to the **darknet** folder, and use the code to convert it to an NCNN model. The details can be found [here](https://github.com/Tencent/ncnn/tree/master/tools/darknet).

```bash
./darknet2ncnn yolo-fastest.cfg best.weights yolo-fastest.param yolo-fastest.bin 1
```

After getting **.param** and **.bin**, we can deploy the model to mobile devices or even the browser. The files in `ncnn/build/install` will be used when you need to run your own model.



--- 
*Note: Thanks to the articles "[pytorch模型的部署（系列一）--ncnn的编译和使用](https://zhuanlan.zhihu.com/p/137458205)" and "[ubuntu16.04安装opencv3.4.1教程](https://blog.csdn.net/cocoaqin/article/details/78163171)" for their help in the compilation process.*
