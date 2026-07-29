---
layout:     post
title:      "Slides Thief 2.0: From Rectangle Heuristics to Evidence-Aware Review"
subtitle:   "A browser-local redesign of boundary detection, confidence, and batch geometry."
date:       2026-07-29
updated:    2026-07-29
author:     Zekun Wang
description: "How Slides Thief 2.0 combines multiple detectors, candidate scoring, local refinement, and batch geometry for more reliable browser-local correction."
image: /img/posts/2026-07-13-slides-thief/ui.png
series: Slides Thief Series
series_nav_title: Detection
series_order: 2
header-img: img/headers/2026-07-29-slides-thief-2-detection.jpg
header-mask: 0.7
catalog: true
tags:
- Computer Vision
- Image Processing
- Web Application
- JavaScript
- Software Architecture
- Local-First
- Productivity Tool
- Project
---

## What Changed in Slides Thief 2.0?

Slides Thief 2.0 replaces a single rectangle heuristic with an evidence-aware detection pipeline.

Instead of trusting the first plausible boundary, several detectors now propose possible quadrilaterals. Slides Thief compares their visual and geometric evidence, refines the strongest result, and marks uncertain pages for review.

For users, the change is broader than a new detection algorithm:

* bright and dark slides can both produce valid boundary evidence
* uncertain and fallback results are easier to find and review
* photos from the same batch can share a carefully constrained geometry prior
* source format is separated from PDF page layout
* 16:10, A4, Letter, and custom source formats extend the workflow beyond presentation slides
* HEIC conversion, preview failures, large images, filenames, keyboard adjustment, and PDF export are handled more robustly

The complete workflow still runs locally. Photos are decoded, analyzed, corrected, and assembled into a PDF inside the browser without being uploaded to a backend.

This article explains why the detector needed a different architecture and how the new design combines automation with explicit human review. For the product overview and usage guide, see [Slides Thief - Turn Photographed Presentation Slides into Clean PDFs](/2026/07/13/slides-thief/).

*For developers building browser-local screen and document correction systems. Implementation details in this article reflect Slides Thief 2.0.0.*

---

## Why Slide Detection Is Harder Than It Looks

Once four accurate corners are known, correcting a photographed slide is relatively straightforward: a projective transform maps the detected quadrilateral into a rectangular output.

Finding those four corners is the difficult part.

A sheet of paper often has a visible physical boundary and a predictable relationship with the surface behind it. A presentation screen may have neither.

A projected image can blend gradually into the wall. A dark slide can be surrounded by a brighter room, while the next slide is nearly white. A display may have both a physical frame and a smaller content area inside it. Camera rotation and perspective can make the screen look far from horizontal, vertical, or even rectangular in image coordinates.

The slide itself also contains competing shapes:

* tables and chart borders
* code panels
* browser windows
* application frames
* large rectangular design elements

Some of these internal edges can be sharper than the actual screen boundary.

Real photographs add incomplete evidence. A person may block one side. Glare can erase contrast. A corner may fall outside the photograph. Motion blur, compression, reflections, and uneven exposure weaken different parts of the outline.

The detector therefore should not ask:

> Find the strongest rectangle in the image.

It should ask:

> Which quadrilateral best explains the available evidence—and is that evidence strong enough to trust automatically?

That change in framing drove most of the 2.0 redesign.

---

## The Limits of the Original Heuristic

The first Slides Thief detector was intentionally lightweight. It ran directly in a browser worker, required no machine-learning model, and avoided a large computer-vision runtime.

Its approximate flow was:

```text
Resize and blur the photograph
        ↓
Search for four contrast lines
        ↓
Combine them into quadrilaterals
        ↓
Score by contrast, area, and aspect ratio
        ↓
Return the best result
```

This worked well for a common case: a bright projected slide surrounded by a darker room.

Searching for four supporting lines independently also had an advantage over contour-only approaches. The detector could still construct a quadrilateral when the boundary was interrupted and no perfect closed contour existed.

But the approach embedded several assumptions.

It preferred a brighter interior, searched within limited slope ranges, and allowed area and aspect ratio to strongly influence the answer. A dark slide could have the wrong contrast direction. A rotated phone could move the correct edges outside the search range. A large display frame or photograph boundary could outscore the visible slide.

Most importantly, the detector returned one answer too early. It did not preserve enough information about competing explanations or communicate when the result was ambiguous.

The next version needed more than additional thresholds. It needed a pipeline that could preserve alternatives.

---

## Separate the Source from the PDF

One of the most important 2.0 changes is not a new edge detector.

It is the separation of two concepts:

```text
The geometry present in the photograph
                    ≠
The geometry of the exported PDF page
```

Suppose a photograph contains a 16:9 slide and the user wants an A4 landscape PDF. The detector should still find the 16:9 source. After correction, that slide can be centered inside an A4 page with margins.

The PDF preference should not encourage the detector to search for an A4-shaped region in the photograph.

Slides Thief 2.0 therefore uses this flow:

```text
Photograph
    ↓
Detect the source boundary
    ↓
Rectify it using the source format
    ↓
Place the corrected result into the PDF layout
```

Source formats now include 16:9, 4:3, 16:10, A4, Letter, and custom ratios. One source format is selected for the batch, while the PDF layout remains a separate choice.

This also allows the same workflow to correct photographed document pages without stretching them into an unrelated presentation ratio.

The broader rule is:

> **Recognition should describe the source. Formatting should decide how that result is presented.**

---

## Detectors Propose Candidates, Not Answers

The central architectural change in 2.0 is that no individual detector owns the final result.

Each detector proposes one or more quadrilateral candidates. A shared pipeline then validates, scores, deduplicates, and compares them:

```text
Image
  ↓
Shared image features
  ├── Contrast-line candidates
  ├── Adaptive-mask candidates
  ├── Gradient and Hough-line candidates
  └── Optional batch-prior candidates
  ↓
Geometry validation and shared scoring
  ↓
Candidate deduplication
  ↓
Local edge refinement
  ↓
Confidence and review decision
```

This avoids a weakness of sequential fallback systems. If detector A returns a merely plausible result, detector B should still have the opportunity to propose something better.

Slides Thief currently combines three complementary single-image methods.

### Bidirectional contrast

The contrast detector keeps the strongest idea from the original implementation: a screen boundary often creates a measurable difference between pixels just inside and just outside an edge.

Version 2.0 evaluates both directions. The interior may be brighter or darker than the exterior, and the preferred direction can differ from one edge to another.

This makes dark slides on bright walls valid candidates rather than automatic failures.

### Adaptive masks

The mask detector uses brightness and saturation statistics from the current image to search for a coherent region. It fits possible boundary lines around that region and proposes several nearby quadrilaterals.

This method can help when the slide forms a consistent bright or low-saturation area even though its physical outline is weak.

It can also be confused by a bright wall or a large neutral object. For that reason, its output is treated as evidence—not as the final answer.

### Multiscale gradients and line geometry

The third method combines luminance and color-opponent gradients at several image scales.

Smaller scales reduce the influence of text, chart marks, and fine texture while preserving larger structural transitions. Gradient orientation then guides a Hough-style line search, allowing the detector to find long boundaries without assuming that the phone was held level.

The resulting lines are grouped into two dominant direction families. Opposing lines from those families can form rotated or perspective-distorted quadrilateral candidates.

The methods solve different parts of the problem. Reliability comes from comparing them under the same rules.

---

## Score the Whole Boundary

A strong line can still be the wrong line.

Slides Thief therefore evaluates evidence along the full length of all four sides. It considers:

* edge strength and support
* continuity and unsupported gaps
* gradient alignment
* inside-outside separation
* region consistency
* geometric validity
* source-ratio and area priors

Visual evidence has the strongest influence. Area and source ratio are weak terms in the shared scorer. Separately, the contrast-line generator uses broad ratio bounds to reject extreme hypotheses before ranking. These signals no longer determine the final result by themselves.

Invalid geometry is rejected early. A candidate must describe a sufficiently large, convex, non-degenerate quadrilateral that remains within bounded image-relative limits.

Candidates from different detectors are also deduplicated. If contrast, mask, and Hough methods converge on nearly the same boundary, that should count as agreement rather than appear as three competing answers.

After ranking, the strongest candidate is refined locally. Each side can move by a limited amount to find a better-supported edge, but the search is constrained so it cannot jump freely to an internal table or outer display frame.

This separates two tasks:

```text
Global detection:
Which boundary is intended?

Local refinement:
Where exactly does that boundary lie?
```

---

## Confidence Is Part of the Workflow

A high candidate score does not automatically mean that the result is unambiguous.

Another, geometrically different candidate may have almost the same score. The detector may be unable to decide between the visible slide, the physical frame, and an internal rectangle.

Slides Thief 2.0 therefore considers both the winning candidate and its alternatives. Confidence is influenced by:

* the winning score
* the margin over the next distinct candidate
* the weakest supported edge
* agreement between independent detectors
* a binary geometry-validity term after hard filtering

Because invalid geometries have already been rejected, most of the remaining discrimination comes from score, margin, edge support, and detector agreement.

The result is connected directly to review behavior:

```text
Strong result
→ Accept automatically

Low confidence or competing candidates
→ Keep the result and suggest review

No supported candidate
→ Use an editable fallback frame and require review
```

A fallback rectangle is useful because it gives the user a starting point for manual corner adjustment. But it is not presented as a successful automatic detection.

Manual correction is also preserved as a distinct state. Once a user has adjusted a page, later processing should not silently return it to an unresolved automatic state.

This reflects a broader reliability principle:

> **When automation cannot justify its result, preserving editability is useful. Pretending completion is not.**

---

## A Batch Contains Useful Geometry

Slides Thief normally processes a group of photographs rather than one isolated image.

If several photos were taken from the same seat, slide content may change completely while the screen geometry remains similar. A dark slide that is difficult to detect alone may be surrounded by several bright slides with reliable boundaries.

Version 2.0 uses a two-pass process.

First, every image is analyzed independently. Reliable results are normalized by image size and grouped into low-variance camera-position clusters. A cluster requires several consistent images, and multiple clusters are allowed if the photographer moves.

In the second pass, uncertain pages can receive the cluster geometry as another candidate. That candidate is mapped into the current photograph, refined against its actual edge evidence, and compared with the independent results.

The prior is never accepted simply because nearby images used the same crop. The current photograph must still support it.

This makes the batch useful without allowing one mistaken result to propagate across every page.

---

## More Than a Detector Update

The detector is the largest architectural change in 2.0, but the surrounding product also became more robust.

Slides Thief now supports presentation and document source shapes while keeping source format separate from PDF layout. Automatic and manual review states are clearer across the localized interface, and corner handles support keyboard adjustment.

HEIC and HEIF conversion still happens locally, with visible placeholders while conversion is running. Preview errors are isolated per image so one problematic file does not collapse the entire batch.

PDF filenames are sanitized before download. Automatic fill handling can match the corrected content when appropriate, while standard paper layouts retain clean margins and users can still select a custom color.

Detection and PDF export now run in separate workers. Detection uses resized analysis buffers, while export has a separate, larger source-image budget. This keeps the interface responsive and avoids retaining unnecessary full-resolution intermediates.

The detector remains model-free, deterministic, and inspectable. A learned model could eventually join the system as another candidate generator, but it would still need to pass through the same validation, scoring, refinement, and review pipeline.

---

## Measuring the Redesign

A more complicated detector is not automatically a better detector.

It may become slower, less predictable, or more likely to produce confident mistakes. Slides Thief therefore includes Python and browser benchmarks based on annotated quadrilaterals.

The measurements include normalized corner error, quadrilateral intersection over union, review rate, high-confidence failure rate, and detection latency.

High-confidence failure rate is especially important. A result that is marked for review is inconvenient. A wrong result that appears trustworthy is much more likely to reach the final PDF unnoticed.

The current public fixture set contains only three controlled synthetic images. These results are regression signals, not a universal accuracy claim.

On the current three-image CLI regression fixture set:

| Metric | Previous baseline | Slides Thief 2.0 |
| --- | ---: | ---: |
| Mean normalized corner error | 0.06833 | 0.00273 |
| Mean Quad IoU | 0.72576 | 0.98659 |
| Images with all corners under 1% | 1/3 | 3/3 |
| High-confidence failures | 1/3 | 0/3 |
| Runtime P95 | 626.23 ms | 1033.29 ms |

The browser implementation reaches a mean normalized corner error of `0.00487` and a mean Quad IoU of `0.97777` on the same controlled fixtures, with a P95 detection time of `195.05 ms`.

The CLI and browser timings come from different runtimes and benchmark harnesses, so they should be read as per-implementation regression measurements rather than a direct speed comparison.

The added gradient, Hough, scoring, and refinement stages have a measurable runtime cost. The goal is not to hide that tradeoff, but to keep it bounded while reducing known geometric failures and avoiding silent overconfidence.

The test suite also includes deterministic difficult-boundary cases. Strong internal grids and fixed-seed image noise must preserve a high-overlap result, while a missing edge or large foreground obstruction must not become a silent success.

The next evaluation step is a larger annotated set of real conference rooms, classrooms, documents, reflections, clipped corners, multiple screens, and camera movement.

---

## What Slides Thief Still Cannot Guarantee

No boundary detector can recover evidence that is not present.

If most of the slide is outside the photograph, several quadrilaterals may be equally plausible. If a person covers an entire side and the scene contains multiple displays, the intended target may require human interpretation.

Other difficult conditions include:

* borderless projections with no stable transition
* severe motion blur or overexposure
* large reflections
* curved projection surfaces
* two adjacent displays
* large internal panels that resemble the outer boundary
* dramatic camera movement between every photo

Batch geometry helps only when the batch contains several reliable anchors. A source-ratio prior helps only when the selected format is correct. Local refinement improves an approximately correct boundary; it cannot turn an unrelated rectangle into the intended target without supporting evidence.

Manual four-corner adjustment therefore remains part of the normal workflow: the goal is not to eliminate human correction, but to reduce how often it is needed and surface the pages most likely to need it.

---

## From Rectangle Detection to Evidence-Aware Review

The original Slides Thief detector asked:

> Which four contrast lines form the largest plausible slide-shaped region?

Slides Thief 2.0 asks:

> Which quadrilateral is best supported by the available visual, geometric, and batch evidence—and is that support strong enough to accept without review?

That change is more important than any individual algorithm added to the project.

Contrast lines, adaptive masks, multiscale gradients, line geometry, local refinement, and batch priors each solve only part of the problem. The system becomes more reliable when those methods can propose alternatives, disagree, expose their evidence, and be compared under the same rules.

At the same time, the product has become more flexible. Slides Thief now supports presentation and document formats, separates recognition from PDF layout, handles large and converted images more carefully, and gives uncertainty an explicit place in the workflow.

The product goal remains simple:

> **Capture slides. Straighten them. Keep them readable.**

Version 2.0 does not merely search harder for four corners. It treats detection as evidence gathering, ambiguity as a meaningful result, and human review as part of a trustworthy local-first workflow.

Try Slides Thief in the browser:

[Open Slides Thief](https://slidesthief.com/)

View the source code:

[Slides Thief on GitHub](https://github.com/waittim/Slides-Thief)
