---
layout:     post
title:      "WearMask: Fast in-browser face mask detection with serverless edge computing for COVID-19"
subtitle:   Electronic Imaging
date:       2023-01-01
author:     Zekun Wang, Pengwei Wang, Peter C. Louis, Lee E. Wheless, Yuankai Huo
authors:
    - name: Zekun Wang
      url: /about/
    - name: Pengwei Wang
    - name: Peter C. Louis
    - name: Lee E. Wheless
    - name: Yuankai Huo
description: "Paper summary: WearMask brings fast in-browser face mask detection with serverless edge computing for COVID-19."
header-img: img/headers/post-bg-unix-linux.jpg
catalog: true
series: WearMask Series
series_nav_title: Paper
series_order: 3
tags:
    - Paper
    - COVID-19
    - Masked Face
    - Deep Learning
    - Serverless
    - Edge Computing
    - AI
    - Local-First
    - Computer Vision
---

The COVID-19 epidemic has been a significant healthcare challenge in the United States. COVID-19 is transmitted predominantly by respiratory droplets generated when people breathe, talk, cough, or sneeze. Wearing a mask is the primary, effective, and convenient method of blocking 80% of respiratory infections. Therefore, many face mask detection systems have been developed to supervise hospitals, airports, public transportation, sports venues, and retail locations. However, the current commercial solutions are typically bundled with software or hardware, impeding public accessibility. In this paper, we propose an in-browser serverless edge-computing-based face mask detection solution, called Web-based efficient AI recognition of masks (WearMask), which can be deployed on common devices (e.g., cell phones, tablets, computers) with internet connections using web browsers. The serverless edge-computing design minimizes hardware costs (e.g., specific devices or cloud computing servers). It provides a holistic edge-computing framework for integrating (1) deep learning models (YOLO), (2) a high-performance neural network inference computing framework (NCNN), and (3) a stack-based virtual machine (WebAssembly). For end-users, our solution has the advantages of (1) serverless edge-computing design with minimal device limitation and privacy risk, (2) installation-free deployment, (3) low computing requirements, and (4) high detection speed. Our application has been launched with public access at facemask-detection.com.

The paper has been published at [Electronic Imaging](https://doi.org/10.2352/EI.2023.35.11.HPCI-229).
