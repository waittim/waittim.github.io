---
layout:     post
title:      "Slides Thief - Turn Photographed Presentation Slides into Clean PDFs"
subtitle:   "Just take photos of the slides, they are yours now."
date:       2026-07-13
author:     Zekun Wang
header-img: img/headers/post-bg-rwd.jpg
catalog: true
tags:
    - Computer Vision
    - Image Processing
    - Web Application
    - JavaScript
    - PDF Generation
    - Client-Side App
    - Productivity Tool
    - Project
---

We have all done it: sitting at an angle in a classroom, academic talk, tech sharing session, or trade show, quickly taking photos of presentation slides before they disappear.

The problem comes later. Those photos are often skewed, rotated, surrounded by background clutter, or difficult to organize into a clean document.

[Slides Thief](https://github.com/waittim/Slides-Thief) is a browser-based tool that turns photographed presentation slides into clean, perspective-corrected PDF pages.

**Live Web App:** [slidesthief.com](https://slidesthief.com/)

Its goal is simple:

> **Capture slides. Straighten them. Keep them readable.**

Slides Thief can automatically detect slide boundaries, correct perspective distortion, and compile the results into standardized 16:9 or 4:3 PDF pages. When automatic detection is not perfect, you can manually adjust the four corners before exporting.

Please use it only for slides you are allowed to photograph, keep, or reference.

---

## Why Slides Thief?

Phone photos are convenient, but they are rarely clean. A typical slide photo may include:

* perspective distortion from sitting off-center
* background noise around the projected screen
* rotation or uneven framing
* reflections, shadows, or audience obstruction
* dozens of separate images that are hard to review later

Slides Thief helps convert those messy photos into a readable, organized PDF that is easier to archive, search, and share for personal study or documentation.

---

## Web App: Local Processing in Your Browser

For most users, the easiest way to use Slides Thief is the web app. It runs locally in your browser and requires no installation.

### Key Features

* **Local-first processing**
  Image conversion, perspective correction, and PDF generation happen directly in your browser. Your slide photos are not uploaded to a backend server.

* **Automatic perspective correction**
  Slides Thief detects the likely slide boundary and transforms the photo into a clean rectangular page.

* **Manual corner adjustment**
  When the automatic result is affected by reflections, complex backgrounds, or partial obstruction, you can drag the four corner handles to fine-tune the correction.

* **Batch PDF export**
  Process multiple slide photos and export them as a single PDF document.

* **iPhone-friendly image support**
  In addition to JPG, PNG, and WebP, Slides Thief supports HEIC/HEIF images and converts them in the browser before processing.

* **Clean web interface**
  The app supports drag-and-drop, dark/light theme behavior, and bilingual interface options.

---

## Web UI Preview

The following screenshot shows the main interface of the Slides Thief Web App:

[![Slides Thief Web UI]({{ "/img/posts/2026-07-13-slides-thief/ui.png" | relative_url }} "Slides Thief Web UI")](https://slidesthief.com/)

A typical workflow looks like this:

1. **Import images**
   Drag and drop your slide photos into the upload area.

2. **Run automatic correction**
   Click **Auto straighten** to detect slide boundaries and apply perspective correction.

3. **Review and adjust**
   Check each result. If automatic detection misses the real slide boundary, drag the four corner handles to correct it manually.

4. **Export PDF**
   Choose the target aspect ratio, generate the PDF, and download the final document.

---

## Tips for Better Results

Automatic detection works best when the physical slide boundary is visible in the photo.

For better results:

* keep the full slide frame inside the photo
* avoid cutting off slide corners
* reduce reflections when possible
* take photos with enough contrast between the slide and the background
* run automatic correction first, then manually adjust outliers

Internal chart lines, audience members, strong reflections, or dark slide backgrounds may occasionally confuse the edge detector. In those cases, manual corner adjustment gives you full control over the final crop and perspective.

---

## Try It

You can try Slides Thief directly in your browser:

[Open the Web App](https://slidesthief.com/)

The source code is available on GitHub:

[View on GitHub](https://github.com/waittim/Slides-Thief)

If the tool helps your note-taking or slide-archiving workflow, consider starring the repository or opening an issue with feedback.
