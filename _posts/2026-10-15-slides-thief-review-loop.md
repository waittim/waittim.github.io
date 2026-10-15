---
layout:     post
title:      "Designing the Review Loop in Slides Thief"
subtitle:   "Slides Thief Design Notes"
date:       2026-10-15
updated:    2026-10-15
author:     Zekun Wang
description: "How Slides Thief 3.0 turns uncertain detections into an actionable review queue with explicit reasons, export boundaries, recoverable state, and batch geometry reuse."
image: /img/posts/2026-07-13-slides-thief/ui.png
series: Slides Thief Series
series_nav_title: Review Loop
series_order: 3
header-img: img/headers/2026-08-01-slides-thief-2-detection.jpg
header-mask: 0.5
catalog: true
redirect_from:
  - /2026/10/15/designing-the-review-loop-in-slides-thief/
tags:
- Product Design
- Interaction Design
- Human-in-the-Loop
- Productivity Tool
- Software Architecture
- Local-First
- Computer Vision
- Project
---

Automatic perspective correction was already working reasonably well by the time I started on Slides Thief 3.0. For ordinary lecture and presentation photos, the detector could usually find the projected slide, correct the perspective, and produce a usable result without much intervention.

The failures that remained were rarely complete breakdowns. More often, a boundary would land slightly inside the screen, two candidates would look similarly plausible, an edge would be too weak to support a confident choice, or one frame in a sequence would disagree with the rest of the batch.

Those cases exposed a different problem. Improving detection accuracy was still useful, but the application also needed a sensible way to handle results that were plausible without being trustworthy enough to ignore.

A confidence score alone did not provide that workflow.

*Slides Thief is an open-source, local-first web app that straightens photographed lecture slides into clean PDFs. For the detection architecture, see Part 2: [From Rectangle Heuristics to Evidence-Aware Review](/2026/08/01/slides-thief-2-detection/).*

## Turning Detection Signals Into Review Reasons

The detector already produced more information than a single confidence value. Candidate scoring considers signals such as edge support and continuity, geometry validity, aspect-ratio consistency, and agreement with batch-level patterns. It can also detect cases where several candidates are too close to distinguish cleanly.

The easiest UI would have been to expose the final scalar directly:

```text
Confidence: 0.71
```

That number is useful when debugging the detector. It is much less useful when reviewing a deck.

A person looking at a slide does not really need to know whether the detector assigned it `0.71` or `0.74`. They need to know what deserves attention.

Slides Thief therefore keeps the confidence value available, but review is driven by explicit reasons attached to the detection result. In 3.0, those reasons include:

```text
Low detection confidence
Weak edge support
Multiple plausible candidate boundaries
Detected boundary outside the image
Inconsistency with the rest of the batch
Fallback frame used
```

The distinction matters because these conditions imply different kinds of inspection. A weak edge suggests checking the slide boundary. Ambiguous candidates suggest verifying that the detector chose the right region. A fallback frame means the automatic pipeline never found a satisfactory boundary at all.

The detector output consequently carries both a proposed quadrilateral and enough metadata for the application to decide whether that proposal should enter the normal path or the review path.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 170" width="100%" aria-label="Slides Thief detection and review flow" style="max-width: 760px; height: auto; display: block; margin: 2rem auto;">
  <defs>
    <marker id="review-arrow" viewBox="0 0 10 10" refX="7" refY="5"
      markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 9 5 L 0 9 z"
        fill="currentColor" opacity="0.6" />
    </marker>
  </defs>

  <rect x="10" y="60" width="125" height="50" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5" />
  <text x="72.5" y="82" text-anchor="middle"
    font-size="13" font-family="sans-serif" fill="currentColor">
    Photo Import
  </text>
  <text x="72.5" y="98" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor" opacity="0.65">
    Batch input
  </text>

  <line x1="135" y1="85" x2="175" y2="85"
    stroke="currentColor" stroke-width="1.5"
    marker-end="url(#review-arrow)" />

  <rect x="178" y="60" width="135" height="50" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5" />
  <text x="245.5" y="82" text-anchor="middle"
    font-size="13" font-family="sans-serif" fill="currentColor">
    Quad Detection
  </text>
  <text x="245.5" y="98" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor" opacity="0.65">
    Candidate scoring
  </text>

  <line x1="313" y1="85" x2="355" y2="85"
    stroke="currentColor" stroke-width="1.5"
    marker-end="url(#review-arrow)" />

  <rect x="358" y="42" width="150" height="86" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5"
    stroke-dasharray="4 3" />
  <text x="433" y="63" text-anchor="middle"
    font-size="12" font-family="sans-serif" font-weight="600"
    fill="currentColor">
    Review Decision
  </text>

  <rect x="370" y="73" width="126" height="20" rx="4"
    fill="currentColor" fill-opacity="0.08" />
  <text x="433" y="87" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor">
    Normal path
  </text>

  <rect x="370" y="98" width="126" height="20" rx="4"
    fill="currentColor" fill-opacity="0.08" />
  <text x="433" y="112" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor">
    Needs review
  </text>

  <line x1="508" y1="83" x2="555" y2="55"
    stroke="currentColor" stroke-width="1.5"
    marker-end="url(#review-arrow)" />
  <line x1="508" y1="105" x2="555" y2="125"
    stroke="currentColor" stroke-width="1.5"
    marker-end="url(#review-arrow)" />

  <rect x="558" y="28" width="185" height="48" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5" />
  <text x="650.5" y="50" text-anchor="middle"
    font-size="13" font-family="sans-serif" fill="currentColor">
    Continue Normally
  </text>
  <text x="650.5" y="65" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor" opacity="0.65">
    No interruption
  </text>

  <rect x="558" y="101" width="185" height="48" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5" />
  <text x="650.5" y="123" text-anchor="middle"
    font-size="13" font-family="sans-serif" fill="currentColor">
    Review Queue
  </text>
  <text x="650.5" y="138" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor" opacity="0.65">
    Accept or correct
  </text>
</svg>

## Treating Review as a Queue

A review badge is sufficient when a batch contains one questionable slide. It becomes less useful when several slides need attention.

Without a dedicated workflow, reviewing a larger batch means scanning the sidebar, opening one flagged slide after another, and remembering which ones have already been handled. The detector may have identified the uncertain items correctly, but the application has done little to help finish the job.

Version 3.0 turns those items into a review queue.

Entering review mode selects slides that still have `needsReview` set. Navigation moves through that subset rather than through the entire deck, and the interface keeps track of how many review items remain.

There are two ways for a slide to leave the queue.

If the automatic result is already correct, the user can explicitly accept it with **Looks good**. If the result is wrong, moving a corner converts the slide to manual geometry. The manual result becomes the active result and its automatic review flags are cleared.

Those two paths lead to the same practical outcome—the slide no longer needs review—but they retain different provenance. One says that the automatic proposal was accepted. The other says that the automatic proposal was replaced by a manual one.

That distinction turned out to be more useful than trying to model every review interaction as a separate confirmation step.

## Using Export as the Review Boundary

Another question was when the application should interrupt the user.

Stopping detection every time an uncertain frame appears would make large imports painful. The useful behavior during import is usually to let the whole batch finish. At the other extreme, allowing export with no acknowledgement of unresolved slides would make the review system easy to miss.

The export action provided a natural boundary between the two.

Slides Thief can import a batch, run detection, and leave questionable results visible without blocking the rest of the workspace. When the user asks for an output artifact, unresolved review items become harder to ignore.

If review items remain, the export flow offers two choices: export anyway, or review the slides first.

Choosing review preserves the export format that initiated the flow. After the remaining review queue is resolved, the application can continue the pending PDF or JPG export instead of returning the user to a dead end where they have to remember what they were doing before review started.

The state transition is roughly:

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 170" width="100%" aria-label="Slides Thief export boundary state transition" style="max-width: 760px; height: auto; display: block; margin: 2rem auto;">
  <defs>
    <style>
      :root {
        color: #24292f;
      }
      @media (prefers-color-scheme: dark) {
        :root {
          color: #e6edf3;
        }
      }
    </style>
    <marker id="export-arrow" viewBox="0 0 10 10" refX="7" refY="5"
      markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 9 5 L 0 9 z"
        fill="currentColor" opacity="0.6" />
    </marker>
  </defs>

  <!-- Step 1: Export requested -->
  <rect x="10" y="60" width="135" height="50" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5" />
  <text x="77.5" y="82" text-anchor="middle"
    font-size="13" font-family="sans-serif" fill="currentColor">
    Export Requested
  </text>
  <text x="77.5" y="98" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor" opacity="0.65">
    PDF or JPG intent
  </text>

  <!-- Arrow 1 to Decision -->
  <line x1="145" y1="85" x2="185" y2="85"
    stroke="currentColor" stroke-width="1.5"
    marker-end="url(#export-arrow)" />

  <!-- Decision Box: Review items remain? -->
  <rect x="188" y="42" width="158" height="86" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5"
    stroke-dasharray="4 3" />
  <text x="267" y="63" text-anchor="middle"
    font-size="12" font-family="sans-serif" font-weight="600"
    fill="currentColor">
    Unresolved Slides?
  </text>

  <rect x="200" y="73" width="134" height="20" rx="4"
    fill="currentColor" fill-opacity="0.08" />
  <text x="267" y="87" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor">
    No (Clean batch)
  </text>

  <rect x="200" y="98" width="134" height="20" rx="4"
    fill="currentColor" fill-opacity="0.08" />
  <text x="267" y="112" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor">
    Yes (Needs review)
  </text>

  <!-- Branch lines -->
  <line x1="346" y1="83" x2="388" y2="52"
    stroke="currentColor" stroke-width="1.5"
    marker-end="url(#export-arrow)" />
  <line x1="346" y1="107" x2="388" y2="125"
    stroke="currentColor" stroke-width="1.5"
    marker-end="url(#export-arrow)" />

  <!-- Step 2A: Direct Export -->
  <rect x="390" y="28" width="160" height="48" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5" />
  <text x="470" y="50" text-anchor="middle"
    font-size="13" font-family="sans-serif" fill="currentColor">
    Direct Export
  </text>
  <text x="470" y="65" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor" opacity="0.65">
    Download artifact
  </text>

  <!-- Step 2B: Review Slides -->
  <rect x="390" y="101" width="160" height="48" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5" />
  <text x="470" y="123" text-anchor="middle"
    font-size="13" font-family="sans-serif" fill="currentColor">
    Review Slides
  </text>
  <text x="470" y="138" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor" opacity="0.65">
    Preserve export intent
  </text>

  <!-- Arrow from Review Slides to Resume Export -->
  <line x1="550" y1="125" x2="588" y2="125"
    stroke="currentColor" stroke-width="1.5"
    marker-end="url(#export-arrow)" />

  <!-- Step 3B: Resume Export -->
  <rect x="590" y="101" width="160" height="48" rx="8"
    fill="none" stroke="currentColor" stroke-width="1.5" />
  <text x="670" y="123" text-anchor="middle"
    font-size="13" font-family="sans-serif" fill="currentColor">
    Resume Export
  </text>
  <text x="670" y="138" text-anchor="middle"
    font-size="11" font-family="sans-serif" fill="currentColor" opacity="0.65">
    Queue resolved
  </text>
</svg>

This is a small amount of state to retain, but without it the review flow feels detached from the action that caused it.

## Restoring a Detection Is Different From Running It Again

Manual editing introduced another ambiguity.

Suppose automatic detection produces quadrilateral **A**. The user then drags two corners and creates manual quadrilateral **B**.

At that point, “go back to automatic” can mean two different things.

The application can restore **A**, the automatic result that existed before the edit:

```text
A → manual edit → B
B → Restore Auto-Detection → A
```

Or it can run detection again:

```text
A → manual edit → B
B → Re-detect → detector → C
```

There is no guarantee that **C** is identical to **A**. Re-detection is a new computation. Restoration is not.

Slides Thief therefore keeps an automatic-detection snapshot with the slide. The snapshot contains the detected quad together with the method, confidence, review state, review reasons, and source ratio that belonged to that result.

**Restore Auto-Detection** copies that stored result back into the active slide state. **Re-detect** submits the image to the detection pipeline again.

Separating the two removed a surprisingly ambiguous “reset” operation from the editor. More importantly, it prevents a recoverable automatic result from being confused with a new detector run.

## Reusing a Manual Quad Across Similar Photos

Slides are often photographed as a sequence. The camera position may stay nearly fixed while the projected content changes from one frame to the next.

That makes independent correction unnecessarily repetitive.

Version 3.0 allows the current quadrilateral to be applied to selected slides or subsequent slides. The coordinates cannot simply be copied as pixels because source images may have different dimensions.

Instead, each point is mapped through normalized image coordinates:

```javascript
const u = x / sourceWidth;
const v = y / sourceHeight;

const targetX = u * targetWidth;
const targetY = v * targetHeight;
```

The implementation also clamps the adapted points to the target image bounds.

The important detail is what happens next: the adapted quadrilateral becomes the target slide's **manual** geometry. Slides Thief does not feed it back into the detector as a new edge-search prior. The feature is intentionally simpler than that.

For a sequence photographed from a stable position, this can still remove a large amount of repetitive dragging. Correct one representative frame, propagate the geometry, and then inspect the exceptions.

That workflow also complements the separate batch-prior logic already used by automatic detection. One operates inside the detector; the other is an explicit user action. Keeping those mechanisms separate avoids pretending that a manual edit carries more statistical meaning than it actually does.

## Keeping Existing Exports Honest After an Edit

Editable geometry creates one more state problem after export.

A user can generate a PDF or JPG archive and then continue editing the workspace. Once any relevant slide geometry or export setting changes, the artifact that was generated earlier no longer represents the current state.

There are two easy but unsatisfying responses.

The first is to delete the old artifact immediately. That is safe, but throws away a file the user may still want.

The second is to leave the artifact untouched with no indication that it is outdated. That preserves access, but makes it easy to download an export that no longer matches the visible workspace.

Slides Thief keeps the artifact and marks it as stale.

The download remains available, while the interface indicates that the workspace has changed since that artifact was generated. Regenerating the output replaces it with an artifact based on the current state.

There is no complicated provenance graph behind this. The application simply preserves an important distinction:

```text
Artifact exists
        ≠
Artifact represents current workspace
```

That distinction became necessary only because 3.0 made the workspace substantially more editable after automatic processing had completed.

## What Changed in 3.0

None of these individual ideas are unusual. Review queues, recoverable state, manual overrides, and uncertainty-aware interfaces all have established precedents.

What changed in Slides Thief was that uncertainty became part of the application state instead of remaining a property of the detector.

A detection result can now carry review reasons. A questionable result has somewhere to go. The user can accept the automatic proposal or replace it. The original proposal remains recoverable. A new detector run remains a separate operation. Similar manual geometry can be reused across a batch. Previously generated exports remain accessible without pretending they are current.

The detector still makes mistakes. Version 3.0 does not try to hide that fact.

It gives those mistakes somewhere to go.

---

## Slides Thief Design Series

* Part 1: [Turn Photographed Presentation Slides into Clean PDFs](/2026/07/13/slides-thief/)
* Part 2: [Slides Thief 2.0: From Rectangle Heuristics to Evidence-Aware Review](/2026/08/01/slides-thief-2-detection/)
* Part 3: Designing the Review Loop in Slides Thief *(This post)*

---

Try Slides Thief in the browser:

[Open Slides Thief](https://slidesthief.com/)

View the source code:

[Slides Thief on GitHub](https://github.com/waittim/Slides-Thief)

