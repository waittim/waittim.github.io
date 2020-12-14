---
layout:     post
title:      Tutorial for compiling NCNN with WASM
subtitle:   The second step to deploy a deep learning model in the browser.
date:       2020-11-15
author:     Zekun
header-img: img/post-bg-code.jpg
catalog: true
tags:
    - NCNN
    - Deep Learning
    - C++
    - WebAssembly
---

The content of this tutorial is an extension of the [Tutorial for compiling NCNN library](https://waittim.github.io/2020/11/10/build-ncnn/).

When we successfully compile the NCNN library normally, we can use the tools in it to convert our models into NCNN format models (`*.param` and `*.bin`). This model can be used for various mobile terminal deployments.

But when we need to deploy the model in a webpage, we need to compile the model and the C++ program that calls it into WebAssembly format. Before compiling the program, we must first compile the NCNN library into the form of WebAssembly.

The content of this article is the specific steps for compiling the NCNN library into WebAssembly. The following steps have been tested on **Ubuntu 18.04**.

## Install Node.js

Before starting, we need to install the latest version of node.js as a dependency in the environment. You can find the installation tutorial on its official [Github](https://github.com/nodejs/help/wiki/Installation). I chose its recommended installation location.

```bash
VERSION=v14.15.1
DISTRO=linux-x64
sudo mkdir -p /usr/local/lib/nodejs
sudo tar -xJvf node-$VERSION-$DISTRO.tar.xz -C /usr/local/lib/nodejs
```

This step is to extract the nodejs package to the recommended location. Next, run `~/.profile` in terminal, and paste the content below to the end of the pop-up file.

```bash
# Nodejs
VERSION=v14.15.1
DISTRO=linux-x64
export PATH=/usr/local/lib/nodejs/node-$VERSION-$DISTRO/bin:$PATH
```

Run `. ~/.profile` in terminal to refresh the profile.


After the installation is over, you can run `node -v` in terminal to check whether the installation is successful.

## Build NCNN with WASM

First, let's clone the NCNN repository. This folder should be **different** from the one we used before(in the previous article), because they have different usage.

```bash
git clone https://github.com/Tencent/ncnn.git
cd ncnn
```

Then clone the key library **emsdk** for compiling WASM.

```bash
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
```

Install and activate it.

```bash
./emsdk install latest
./emsdk activate latest
```

Then, return to the parent folder(master of ncnn), set the emsdk as a source.

```bash
cd ..
source emsdk/emsdk_env.sh
```

Observe the output of the terminal here, you will find that the currently used nodejs is a built-in library in emsdk, and its version is old. Therefore, we need to re-add the latest version of nodejs that we installed before to the path.

```bash
export PATH=/usr/local/lib/nodejs/node-v14.15.1-linux-x64/bin:$PATH
```

You can run `node -v` to check the version again.

Next, prepare to compile the NCNN library.

```bash
mkdir build && cd build
```

If you are compiling for a browser that supports experimental WebAssembly features such as SIMD and SSE2, please use the following code.

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=../emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DNCNN_SIMPLEOMP=ON -DNCNN_BUILD_TESTS=ON ..
```

If it is compiled for browsers such as Safari in iOS without SIMD SSE2, replace it with the following code.

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=../emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DNCNN_OPENMP=OFF -DNCNN_SIMPLEOMP=OFF -DNCNN_RUNTIME_CPU=OFF -DNCNN_SSE2=OFF -DNCNN_AVX2=OFF -DNCNN_BUILD_TESTS=ON ..
```

Then start make.

```bash
make
```

After the make ends, use the built-in test case of NCNN to check whether the compilation is successful.

With SIMD SSE2:

```bash
TESTS_EXECUTABLE_LOADER=node TESTS_EXECUTABLE_LOADER_ARGUMENTS="--experimental-wasm-simd;--experimental-wasm-threads;--experimental-wasm-bulk-memory" ctest --output-on-failure -j 2
```

Without SIMD SSE2:

```bash
TESTS_EXECUTABLE_LOADER=node ctest --output-on-failure -j 2
```

If all the tests are passed, generate the install file.

```bash
make install
```

So far, the NCNN with WebAssembly has been compiled, and the next step is to introduce its usage.

## Compile C++ code

First, we need to write a C++ program that calls the NCNN model. The relevant files I have written have been uploaded in the facemask-detection repository, and I will compile it based on this.

Clone it to the specified folder.

```bash
cd ~/Documents 
git clone https://github.com/waittim/facemask-detection.git
cd facemask-detection
```

Note that if you are compiling a version without SIMD and SSE2, please delete the following content in [CMakeLists.txt](https://github.com/waittim/facemask-detection/blob/master/CMakeLists.txt).

```bash
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=15") 
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=15") 
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fopenmp -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=15")
```

And change `target_link_libraries(yolo ncnn pthread)` to be `target_link_libraries(yolo ncnn)`.


Next, create an empty folder named ncnn in it, and copy the two files under `build/install/` under ncnn master to this ncnn folder.

```bash
mkdir ncnn
```

Copy the emsdk folder under ncnn master and paste it to the master folder of facemask-detection.

At this time, I recommend to use `node -v` to ensure that the version of nodejs is correct.

Finally, use emsdk to compile.

```bash
emcmake cmake
emmake make
```

After compiling, you can get `yolo.js`, `yolo.wasm`,
`yolo.worker.js`. These are the files needed to call WASM format functions in the JavaScript environment.

------

The complete CMakeLists.txt content is as follows:

```bash
project(facemask-detection)

cmake_minimum_required(VERSION 3.10)

set(CMAKE_BUILD_TYPE release)

set(ncnn_DIR "${CMAKE_CURRENT_SOURCE_DIR}/ncnn/lib/cmake/ncnn")
find_package(ncnn REQUIRED)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -s FORCE_FILESYSTEM=1 -s INITIAL_MEMORY=256MB -s EXIT_RUNTIME=1")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s FORCE_FILESYSTEM=1 -s INITIAL_MEMORY=256MB -s EXIT_RUNTIME=1")
set(CMAKE_EXECUTBLE_LINKER_FLAGS "${CMAKE_EXECUTBLE_LINKER_FLAGS} -s FORCE_FILESYSTEM=1 -s INITIAL_MEMORY=256MB -s EXIT_RUNTIME=1")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=15")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=15")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fopenmp -s USE_PTHREADS=1 -s PTHREAD_POOL_SIZE=15")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -sEXPORTED_FUNCTIONS=['_yolo_ncnn'] --preload-file ${CMAKE_CURRENT_SOURCE_DIR}/assets@.")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -sEXPORTED_FUNCTIONS=['_yolo_ncnn'] --preload-file ${CMAKE_CURRENT_SOURCE_DIR}/assets@.")
set(CMAKE_EXECUTBLE_LINKER_FLAGS "${CMAKE_EXECUTBLE_LINKER_FLAGS} -sEXPORTED_FUNCTIONS=['_yolo_ncnn'] --preload-file ${CMAKE_CURRENT_SOURCE_DIR}/assets@.")


add_executable(yolo yolo.cpp)
target_link_libraries(yolo ncnn pthread)
```


--- 
*Note: Thanks to NCNN creator nihui for her help in this process.*
