# WearMask: Fast in-browser face mask detection with serverless edge computing for COVID-19

Electronic Imaging

> Paper summary: WearMask brings fast in-browser face mask detection with serverless edge computing for COVID-19.

- Canonical: https://www.zekun.blog/2023/01/01/paper-wearmask-fast-in-browser/
- Published: 2023-01-01
- Author: Zekun Wang, Pengwei Wang, Peter C. Louis, Lee E. Wheless, Yuankai Huo
- Tags: Paper, COVID-19, Masked Face, Deep Learning, Serverless, Edge Computing, AI, Local-First, Computer Vision
- Series: WearMask Series, part 3 of 5

The COVID-19 epidemic has been a significant healthcare challenge in the United States. COVID-19 is transmitted predominantly by respiratory droplets generated when people breathe, talk, cough, or sneeze. Wearing a mask is the primary, effective, and convenient method of blocking 80% of respiratory infections. Therefore, many face mask detection systems have been developed to supervise hospitals, airports, public transportation, sports venues, and retail locations. However, the current commercial solutions are typically bundled with software or hardware, impeding public accessibility. In this paper, we propose an in-browser serverless edge-computing-based face mask detection solution, called Web-based efficient AI recognition of masks (WearMask), which can be deployed on common devices (e.g., cell phones, tablets, computers) with internet connections using web browsers. The serverless edge-computing design minimizes hardware costs (e.g., specific devices or cloud computing servers). It provides a holistic edge-computing framework for integrating (1) deep learning models (YOLO), (2) a high-performance neural network inference computing framework (NCNN), and (3) a stack-based virtual machine (WebAssembly). For end-users, our solution has the advantages of (1) serverless edge-computing design with minimal device limitation and privacy risk, (2) installation-free deployment, (3) low computing requirements, and (4) high detection speed. Our application has been launched with public access at facemask-detection.com.

The paper has been published at [Electronic Imaging](https://doi.org/10.2352/EI.2023.35.11.HPCI-229).


## WearMask Series

- [Intro](https://www.zekun.blog/2020/11/27/mask-detection/index.md)
- [Project Details](https://www.zekun.blog/2020/12/01/mask-detection-report/index.md)
- Paper (this page)
- [Build NCNN](https://www.zekun.blog/2020/11/10/build-ncnn/index.md)
- [Build NCNN WASM](https://www.zekun.blog/2020/11/15/build-ncnn-wasm/index.md)

## Related

- [Characterizing browser-based medical imaging AI with serverless edge computing: towards addressing clinical data security constraints](https://www.zekun.blog/2023/04/10/paper-browser-based-medical-imaging-ai/index.md): Paper summary: characterizing browser-based medical imaging AI with serverless edge computing under clinical data constraints.
- [Designing the Review Loop in Slides Thief](https://www.zekun.blog/2026/10/15/slides-thief-review-loop/index.md): How Slides Thief 3.0 turns uncertain detections into an actionable review queue with explicit reasons, export boundaries, recoverable state, and batch geometry reuse.
- [A Memory System Should Survive an Interrupted Write](https://www.zekun.blog/2026/10/01/memory-custodian-crash-recovery/index.md): Why multi-file agent-memory mutations require repo-external transaction journaling, conditional rollback, audit blockers, and staged protocol migration.

Older: [K-Means-Based Anomalous Email Detection in PySpark](https://www.zekun.blog/2021/05/05/kmeans-anomaly-detection/index.md)
Newer: [Characterizing browser-based medical imaging AI with serverless edge computing: towards addressing clinical data security constraints](https://www.zekun.blog/2023/04/10/paper-browser-based-medical-imaging-ai/index.md)
