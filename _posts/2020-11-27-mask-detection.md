---
layout:     post
title:      Super fast In-browser FaceMask Detection
subtitle:   Open the webpage, then you have it!
date:       2020-11-27
author:     Zekun
header-img: img/products-bg.jpg
catalog: true
tags:
    - Deep Learning
    - Object Detection
    - Project
    - Python
    - C++
    - JavaScript
---

**[facemask-detection.com](https://facemask-detection.com/)** 👈👈

This is an AI that **detects masks super fast**:
- No installation or registration.
- No need to buy expensive devices.
- You don't even need a continuous internet connection.
- Most importantly, completely **FREE**!

Well, let's be serious. This is an AI model running in the browser that can recognize whether people are wearing masks and automatically remind them.

![mask-detection-machines.png](https://github.com/waittim/waittim.github.io/raw/master/img/mask-detection-machines.png)

Let us recall those mask detection machines at the entrance of luxury stores, they can remind customers to wear masks. However, most small business and local shops cannot pay thousands of dollars to equip them. Now, you only need a tablet or laptop, and you can have it! After loading, this model runs completely locally on your device, and no data will be uploaded to the server.

<iframe width="700" height="393" src="https://www.youtube-nocookie.com/embed/Zx6cvJPsEoU" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## How to use it?

Now, you can use it on Android, iOS, Windows, macOS, Linux systems. For the best experience and fastest speed, please use the Chrome browser under non-iOS systems.

1. [Download](https://www.google.com/chrome/) and Launch the latest version of Chrome browser
2. Enter *chrome://flags* in the address bar
3. Enable all *WebAssembly* features
4. Re-launch chrome, open the [webpage](http://facemask-detection.com/), and allow the access to camera.

![webassemblysetting.png](https://github.com/waittim/waittim.github.io/raw/master/img/webassembly-setting.png)

**Hint:** The FPS depends on your device CPU.

## Why it's so fast?

This model is modified from [Yolo-Fastest](https://github.com/dog-qiuqiu/Yolo-Fastest) and is only 1.3M in size. It might be the fastest and lightest open source improved version of yolo general object detection model. The Yolo series models that we are familiar with, which are characterized by detection speed, are much larger than it, usually tens of M in size. Even the smallest one, YOLOv5s, is 7.5M. Therefore, this model only puts little pressure on the device.


| Model | Yolo-Fastest | [YOLOv3-tiny](https://github.com/ultralytics/yolov3/releases) | [YOLOv3-SPP](https://github.com/ultralytics/yolov3/releases) | [YOLOv5s](https://github.com/ultralytics/yolov5/releases) | [YOLOv5m](https://github.com/ultralytics/yolov5/releases) | [YOLOv5l](https://github.com/ultralytics/yolov5/releases) | [YOLOv5x](https://github.com/ultralytics/yolov5/releases) |
| - | - | - | - | - | - | - | - |
| **Size** | 1.3M | 8.9M | 63.0M | 7.5M | 21.8M | 47.8M | 89.0M |

The deployment of this model is achieved through the [NCNN](https://github.com/Tencent/ncnn) framework and [WebAssembly](https://webassembly.org/). NCNN is a high-performance neural network inference computing framework optimized for mobile platforms. It has excellent performance on low computing power devices. WebAssembly compiles the C++ program into a binary format, so that it can run at high speed in the browser.

Because of this, even without a GPU, even if it runs in a browser, it can complete the detection with a high FPS, which exceeds most common mask detection tools.

## What about privacy issues?

Since this model runs entirely in the browser, it does not and does not need to upload any data, such as video content, to the server. All detection processes are completed locally. After loading, the user can even cut off the Internet connection. 

All video content will only be processed in real time and will not be stored in any form.

Therefore, there is no need to worry about any privacy leakage and other issues. This also means that the user does not need to set up wifi for the place where the device is placed or worry about the extra data charge caused by detection. At the same time, the tool will not occupy the storage space of the device.

## What's more?

Because only Safari supports WebAssembly under the iOS system, and it does not support parallel computing acceleration methods such as SIMD, the speed will be slower than other platforms.

All in all, it is just a free alternative to the expensive mask detection machine. You can buy a tablet for $60 and a floor standing for $20 to get similar functions. After this pandemic, these devices can also be used for other purposes.

![price-eg.jpg](https://github.com/waittim/waittim.github.io/raw/master/img/price-eg.jpg)

In such a hard time, I hope this AI can give a hand to those small businesses that strive to persist. So that they can obtain protection similar to luxury shops at a small cost. As long as this tool can protect one more person from COVID-19, it would be enough.

Of course, this project is not mature yet. If you have any suggestions or are willing to contribute to this project, please contact me.

Thank you very much!

<br /><br /><br /><br /><br />

-------

## Release information 

**2021.01.06 - 2.0.4**: Add feedback function.

**2020.12.13 - 2.0.0**: Deployed a new model. It can distinguish the face that doesn't wear a mask properly (completely cover nose and mouth). Improved the recognition of covering the face with a mobile phone.

**2020.12.01 - 1.1.0**: Added support for iOS system. Now it can automatically recognize whether the browser supports advanced computing functions and apply them.

**2020.11.30 - 1.0.3**: Added Spanish and Chinese versions.

**2020.11.28 - 1.0.2**: The domain name was changed to facemask-detection.com, which is convenient for users to remember.

**2020.11.26 - 1.0.1**: The website is officially established.

