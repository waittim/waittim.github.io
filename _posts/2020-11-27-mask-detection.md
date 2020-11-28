---
layout:     post
title:      Super fast In-browser FaceMask Detection
subtitle:   Open the webpage, then you have it!
date:       2020-11-27
author:     Zekun
header-img: img/bg-mask.jpg
catalog: true
tags:
    - Deep Learning
    - Object Detection
    - Project
---

**[facemask-detection.com](http://facemask-detection.com/)**

This is an AI that **detects masks super fast**:
- No installation.
- No registration.
- No need to buy expensive devices.
- You don't even need a continuous internet connection.
- Most importantly, it is completely **FREE**!

Well, let's be serious. This is an AI model running in the browser that can recognize whether people are wearing masks and automatically remind them.

Let us recall those mask detection machines at the entrance of luxury stores, they can remind customers to bring masks. However, most small business and local shops cannot pay thousands of dollars to equip them. Now, you only need a tablet or laptop, and you can have it! After loading, this model runs completely locally on your device, and no data will be uploaded to the server (trust me, I can't afford it).

<iframe width="700" height="393" src="https://www.youtube-nocookie.com/embed/Zx6cvJPsEoU" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## How to use it?

1. Launch Google chrome browser, open *chrome://flags* in the address bar
2. Enable all *WebAssembly* features
3. Re-launch chrome , open the [webpage](http://facemask-detection.com/),and allow the access to camera.

![webassemblysetting.png](https://github.com/waittim/waittim.github.io/raw/master/img/webassembly-setting.png)

**Hint:** iOS is not supported yet, please use Android, MacOS and Windows. The FPS depends on your device CPU.

## Why it's so fast?

This model is modified from [Yolo-Fastest](https://github.com/dog-qiuqiu/Yolo-Fastest) and is only 1.3M in size. It might be the fastest and lightest open source improved version of yolo general object detection model. The Yolo series models that we are familiar with, which are characterized by detection speed, are much larger than it, usually tens of M in size. Even the smallest one, YOLOv5s, is 7.5M. Therefore, this model only puts little pressure on the device.


| Model | Yolo-Fastest | [YOLOv3-tiny](https://github.com/ultralytics/yolov3/releases) | [YOLOv3-SPP](https://github.com/ultralytics/yolov3/releases) | [YOLOv5s](https://github.com/ultralytics/yolov5/releases) | [YOLOv5m](https://github.com/ultralytics/yolov5/releases) | [YOLOv5l](https://github.com/ultralytics/yolov5/releases) | [YOLOv5x](https://github.com/ultralytics/yolov5/releases) |
| - | - | - | - | - | - | - | - |
| **Weight size** | 1.3M | 8.9M | 63.0M | 7.5M | 21.8M | 47.8M | 89.0M |

The deployment of this model is achieved through the [NCNN](https://github.com/Tencent/ncnn) framework and [WebAssembly](https://webassembly.org/). NCNN is a high-performance neural network inference computing framework optimized for mobile platforms. It has excellent performance on low computing power devices. WebAssembly compiles the C++ program into a binary format, so that it can run at high speed in the browser.

Because of this, even without a GPU, even if it runs in a browser, it can complete the detection with a high FPS, which exceeds most common mask detection tools.

## What about privacy issues?

Since this model runs entirely in the browser, it does not and does not need to upload any data, such as video content, to the server. All detection processes are completed locally. After loading, the user can even cut off the Internet connection. (So I don't need to rent a server lol)

All video content will only be processed in real time and will not be stored in any form.

Therefore, there is no need to worry about any privacy leakage and other issues. This also means that the user does not need to set up wifi for the place where the device is placed or worry about the extra data charge caused by detection. At the same time, the tool will not occupy the storage space of the device.

## What's more?

Because the existing deployment uses SIMD, etc., it cannot run on Safari temporarily. And iOS only supports WebAssembly in Safari, so it cannot be used on the iOS now. I am still working on the problem.

Of course, this project is not yet mature. If you have any suggestions or are willing to contribute to this project, please be sure to contact me.

Thank you very much!