---
layout: post
title: Designing Memory That Can Safely Forget
subtitle: Persistent project memory is trustworthy only when forgetting is explicit, previewable, and bounded.
date: 2026-07-21
updated: 2026-07-29
author: Zekun Wang
description: "A design for bounded agent-memory forgetting using explicit modes, dry-run previews, semantic entries, and validated multi-file plans."
image: /img/headers/post-bg-memory-disk.jpg
series: MemoryCustodian Design Series
series_nav_title: Safe Forgetting
series_order: 3
header-img: img/headers/post-bg-memory-disk.jpg
header-mask: 0.5
catalog: true
tags:
    - Agent
    - Agent Memory
    - Developer Tools
    - Software Architecture
    - Local-First
    - Data Governance
    - AI
    - Project
---

## What Makes Agent Memory Safe to Forget?

Deleting memory safely is harder than it sounds. In a repository, editing or deleting text by hand can easily break adjacent rules, leave stale references in other files, or leave behind a descriptive tombstone that re-introduces the very topic you wanted to retire.

MemoryCustodian treats forgetting as an explicit dry-run state change: it previews the exact diff across every affected file before touching disk, operates on complete semantic entries rather than text fragments, and clearly defines the boundaries of what it can and cannot erase.

*For developers building reviewable deletion and mutation workflows over durable agent memory. The CLI examples and three forgetting modes reflect MemoryCustodian v0.9.x. The stronger transaction, recovery, and structured erasure-reporting behaviors described as requirements below represent the design direction for upcoming releases.*

Most memory systems are evaluated primarily by what they can retain: Can they preserve context across sessions? Can they retrieve an old decision? Can they prevent an agent from repeating the same mistake?

Those questions matter. But a durable memory system must also be judged by what it can safely stop retaining. A project decision may become obsolete, a constraint may no longer apply, or an approach previously rejected may deserve fresh reconsideration.

Once memory becomes durable, forgetting is no longer a simple text-editing operation. Removing the wrong line can subtly invert the meaning of adjacent rules. Deleting active guidance while retaining unmanaged copies creates silent discrepancies, and replacing a removed entry with an overly verbose tombstone may preserve the very topic meant to disappear. A trustworthy project-memory system must therefore do more than store and retrieve information—it must govern how memory state transitions occur.

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) approaches this problem through four related design choices:

* Explicit forgetting modes
* Preview-first mutation
* Complete semantic entries
* Precomputed multi-file plans

Together, these choices treat forgetting as a governed state transition rather than an invisible side effect.

<img class="theme-surface" src="{{ "/img/posts/2026-07-21-memory-custodian-safe/gallery-safe-forgetting.png" | relative_url }}" alt="Safe forgetting workflow: Preview generates a dry-run plan, Review checks semantic units and blockers, Apply re-runs with --apply; supports soft, hard, and purge modes over plain Markdown" title="Memory you can review—and safely forget" width="1270" height="760" loading="lazy" decoding="async">

---

## Forgetting Is a Governance Problem

While remembering is naturally additive—appending a new entry to `decisions.md` or recording an invariant in `constraints.md` without disturbing existing prose—forgetting is inherently destructive. A deletion operation must alter existing knowledge structures without corrupting adjacent context. Depending on user intent, retiring a concept might require revoking active guidance, injecting a tombstone, updating cross-file manifests, and coordinating mutations across several markdown modules simultaneously.

This creates a fundamental asymmetry: remembering can add information without disturbing existing meaning, whereas forgetting must modify existing meaning without corrupting its surroundings. A generic `delete` command cannot safely capture the spectrum of user intent:
* When a user requests to forget a decision, they may simply want active guidance to cease while preserving an audit record of its deliberate removal.
* Alternatively, they may want both the guidance and its specific subject expunged from active managed files so future prompts contain no mention of the topic.
* In the most comprehensive case, they may require the topic eradicated across all active and archived files managed by the system.

Treating these requests as identical produces bad defaults: either deleting too little (leaving behind topic-bearing tombstones or unmanaged archives) or deleting too much (erasing critical context and allowing previously rejected ideas to be reintroduced without review). Safe forgetting begins by making the intended state transition explicit.

---

## Three Levels of Forgetting

MemoryCustodian formalizes three distinct forgetting intentions through `soft`, `hard`, and `purge` modes:

| Mode  | Active entries | Topic-bearing tombstones      | Managed archives     | Git history | Distributed copies |
| ----- | -------------- | ----------------------------- | -------------------- | ----------- | ------------------ |
| Soft  | Removed        | Retained or created           | Preserved            | Unchanged   | Outside control    |
| Hard  | Removed        | Replaced with a generic guard | Preserved            | Unchanged   | Outside control    |
| Purge | Removed        | Removed                       | Searched and removed | Unchanged   | Outside control    |

All three modes operate strictly within MemoryCustodian-managed files (`docs/memory/`); none rewrites Git history or attempts to revoke copies already distributed across developer machines or external systems.

### Soft forgetting: retiring active guidance with audit continuity

Soft forgetting removes matching active entries while preserving a structured tombstone that explicitly references the removed topic. For example, consider an active decision to maintain compatibility with a legacy export format:

```markdown
## Use the legacy export format

Continue generating the legacy export format for all new files.

Reasoning:
- Older clients cannot read the replacement format.
```

When client compatibility requirements are relaxed, the project wants future agents to stop following this rule, but also wants to prevent the rule from returning accidentally when someone rediscovers it in an old issue or design doc. A soft forget converts the decision into a tombstone:

```markdown
## Tombstone: legacy export format

Do not reintroduce unless the user explicitly reverses this.

Reason: the user asked MemoryCustodian to forget this topic.  
Mode: soft.  
Date: YYYY-MM-DD.
```

By intentionally retaining the topic in the tombstone, soft forgetting prioritizes architectural continuity: it documents that the project deliberately stopped applying this rule and ensures that re-adopting it requires conscious review.

### Hard forgetting: removing topic names from active governance

Hard forgetting removes active entries and stops mentioning the forgotten subject in active tombstones. While a soft tombstone still reveals the subject matter, hard forgetting replaces topic-bearing tombstones with an opaque guard:

```text
A previous memory entry was deliberately removed.
Do not reconstruct or restore it without explicit user direction.
```

This generic guard maintains the integrity of the governance boundary without preserving the forgotten subject in active memory. Managed archives remain untouched in hard mode.

### Purge: coordinated removal across active and archived state

Purge represents the strongest operation within MemoryCustodian’s scope. It performs a managed-memory-wide sweep across confirmed decisions, active constraints, rejected approaches, inbox candidates, managed archives, and earlier tombstones, eradicating matching records across the entire tree. 

Purge is not a single-file edit, but a coordinated multi-file state transition. However, purge does not claim universal erasure: Git commits and external repository clones remain outside the tool's authority. Selecting a mode follows a simple decision flow:

```text
Stop applying this memory?
  Keep topic evidence in a tombstone?
    Yes → soft
    No  → Also search managed archives?
            No  → hard
            Yes → purge
```

---

## Preview the Semantic Effect Before Writing

Deletion is easy to describe and difficult to reverse safely. Immediate mutation is therefore a poor default.

MemoryCustodian separates planning from application. A command such as:

```bash
memory-custodian forget "legacy deployment note" --mode soft
```

first produces a plan. It does not immediately change the managed files.

The caller can inspect which files contain candidate matches, which complete entries would be removed, which tombstones would be created or changed, which archives would be affected, and whether any match is ambiguous.

Only an explicit apply operation performs the mutation:

```bash
memory-custodian forget "legacy deployment note" \
  --mode soft \
  --apply
```

This separates two decisions:

1. What should happen?
2. Should the prepared plan now be executed?

A weak preview might say:

```text
Three matches found. Continue?
```

That is not enough. A match count does not reveal what the memory store will mean after the operation.

A useful preview should show the semantic effect:

```text
Forget mode: soft
Topic: legacy deployment process

Planned changes:

docs/memory/decisions.md
- Remove complete entry:
  "Use the legacy deployment process"

docs/memory/do-not-use.md
- Add topic-bearing tombstone

docs/memory/archive/2026-06.md
- No change in soft mode

Erasure boundary:
- Active managed memory: modified
- Managed archive: preserved
- Git history: unchanged
- Clones, forks, and backups: outside protocol control

No files have been modified.
```

In the current CLI, a dry-run against the NightNotes example looks like this:

```bash
memory-custodian forget "Local session persistence" \
  --mode soft \
  --project-root examples/nightnotes-video-demo
```

<picture>
  <source srcset="{{ "/img/posts/2026-07-21-memory-custodian-safe/forget-preview-dark.png" | relative_url }}" media="(prefers-color-scheme: dark)">
  <img class="theme-chrome" src="{{ "/img/posts/2026-07-21-memory-custodian-safe/forget-preview.png" | relative_url }}" alt="Terminal dry-run of memory-custodian forget in soft mode, matching one decision entry and reporting that no files were modified" title="Preview-first forget plan" width="1356" height="459" loading="lazy" decoding="async">
</picture>

The primary goal of a dry-run preview is to make the proposed state transition inspectable so that developers can reject unintended changes before the first disk write occurs. 

Preview also introduces deliberate friction when a requested topic is overly broad. For instance, running `memory-custodian forget "Go" --mode soft` could inadvertently match a programming language, product name, common verb, or package header. In such cases, the system flags ambiguous matches and halts execution, requiring explicit scoping before modifying repository files.

---

## Delete Complete Meaning, Not Matching Text

Memory stored in Markdown is not a collection of independent text lines. An architectural decision encompasses a heading, an explicit choice, supporting reasoning, nested bullets, and scope limitations. As established in the [technical design](/2026/07/20/memory-custodian-tech-design/), scoped decisions must stay complete when loaded into context; forgetting applies that exact symmetry to deletion: remove complete semantic blocks, not loose keyword matches.

Consider a structured entry:

```markdown
- Do not use the legacy deployment token in new environments.
  - Existing installations still require a migration path.
  - This restriction does not apply to local development.
```

Deleting only the top line destroys the grammatical structure of the remaining bullets, while deleting only the trailing scope limitation silently turns a scoped restriction into an accidental global ban. MemoryCustodian therefore enforces that mechanical mutations operate on entire semantic units.

When a match occurs inside an unstructured, narrative paragraph alongside unrelated thoughts, deterministic tooling must refuse to guess:

```text
Manual rewrite required.

The matching topic appears inside an unstructured paragraph containing
unrelated information. No files have been modified.
```

Refusing ambiguous edits is not a limitation of tooling—it reflects the fundamental principle that string matching can locate candidate occurrences, but cannot judge how adjacent meaning should be rewritten.

---

## Plan the Whole Mutation Before the First Write

Forgetting operations rarely touch only one file. A soft forget removes an entry from `decisions.md` while adding an audit tombstone to `do-not-use.md`. A hard forget replaces topic-bearing tombstones with generic guards, and a purge coordinates removals across active files and archives simultaneously.

These multi-file state changes are transactions in disguise. Although a local Markdown tool lacks the row-locking primitives of a relational database, it can enforce equivalent operational discipline: build, validate, and preview the complete multi-file diff before executing the first write to disk:

```text
Forgetting intent
  ↓
Select soft, hard, or purge
  ↓
Locate complete semantic entries
  ↓
Build the full multi-file plan
  ↓
Validate every target and erasure boundary
  ↓
Prepare mode-compatible recovery behavior
  ↓
Apply bounded mutations
  ↓
Revalidate and report
```

Before writing, the system confirms every file to be modified, checks semantic alignment across matched regions, ensures recovery policies match the chosen mode, and enforces erasure boundaries:

```text
Forget mode: hard
Topic: legacy deployment token

Planned removals:
- docs/memory/decisions.md: 1 complete entry

Planned replacements:
- docs/memory/do-not-use.md:
  replace 1 topic-bearing soft tombstone
  with 1 generic redacted guard

Managed archives:
- preserved in hard mode

Recovery behavior:
- do not create a new topic-bearing backup or journal record
- preserve only generic structural operation metadata

Erasure boundary:
- Git history will not be rewritten
- existing clones, forks, and backups cannot be revoked

Validation:
- all target files exist
- all matched regions align with complete entries
- no manual rewrites are required
- protocol metadata is supported

No writes have occurred.
```

Recovery behavior must strictly respect the selected mode: soft forgetting preserves ordinary recovery material because audit evidence is intentionally retained, whereas hard and purge modes avoid generating secondary topic-bearing journal copies that contradict the requested removal scope.

---

## Be Honest About Failure and Erasure Boundaries

Even with preflight validation, filesystem operations can encounter runtime interruptions, permissions failures, or disk limits. A trustworthy tool must report actual execution state rather than masking partial completion behind generic errors:

```text
The mutation completed partially.

Completed:
- Removed matching entry from decisions.md

Incomplete:
- Could not update do-not-use.md
- Generic guard was not written

The managed memory does not fully reflect the requested hard-forget state.
Review the saved plan and current files before continuing.
```

The user immediately knows whether active guidance was revoked, whether guards were placed, and what state remains in the repository.

The same transparency applies to erasure scope: MemoryCustodian controls what is provided to future agents through managed repository files (`docs/memory/`); it does not guarantee erasure from Git commit history or external forks. In distributed software engineering, claiming universal erasure is impossible, and pretending otherwise only erodes operational trust.

### Repo-native memory is not a secret store

Because repo-native memory inherits Git’s distribution model, credentials, API tokens, private keys, and detailed commercial terms do not belong in project memory. Stored entries should capture only minimal operational constraints, pointing to secure internal documentation when detailed context is required:

```markdown
This integration must respect the externally defined vendor rate limit.

Evidence: internal/vendor-policy.md
```

The division of labor remains clean: humans and agents govern semantic intent, while deterministic tooling validates and applies mutations.

---

## A Memory System Should Know How to Let Go

A memory system that can only accumulate information inevitably degrades into technical debt. Old decisions linger after their rationale expires, temporary workarounds harden into rigid rules, and contradictions multiply. 

Safe forgetting prevents persistence from degenerating into accidental permanence. By making forgetting modes explicit, previewing state transitions across files, preserving semantic entry boundaries, and strictly bounding what managed deletion can and cannot promise, MemoryCustodian ensures that project memory remains an asset rather than a liability. A memory system is mature not when it can store everything indefinitely, but when it can cleanly retire obsolete constraints without corrupting active context or over-promising on external deletion.

## Key Takeaways

* Forgetting is a governed state transition, not generic string deletion.
* Soft, hard, and purge represent distinct, bounded outcomes within managed memory.
* Preview and validation must verify complete semantic entries and multi-file plans before writing.
* Hard and purge operations must not create topic-bearing recovery records.
* Forgetting operates strictly on managed repository files and does not rewrite Git history.
* Project memory should record minimal operational constraints, never sensitive credentials.

## Frequently Asked Questions

### What is the difference between soft, hard, and purge forgetting?

Soft forgetting removes active guidance while retaining topic-bearing evidence. Hard forgetting removes the topic from active guidance and replaces its active tombstone with a generic guard. Purge also searches and removes the topic from managed archives.

### Does purge erase the topic everywhere?

No. Purge extends forgetting into MemoryCustodian-managed archives, but it does not rewrite Git history or revoke copies in clones, forks, backups, caches, or external systems.

### Can MemoryCustodian safely store secrets or detailed contract information?

No. Repo-native memory inherits the repository’s distribution and retention model. Store only the minimum operational constraint needed by the agent and keep sensitive source material in an appropriately protected system.

### Why preview a forgetting operation?

A preview lets a person or agent verify the intended mode, semantic entry boundaries, affected files, recovery behavior, and erasure boundary before destructive writes begin.

* [Read Part 4: What Should a Coding Agent Be Allowed to Remember?](/2026/08/26/memory-custodian-remember/)
* [Read Part 5: A Memory System Should Explain What It Did Not Load](/2026/09/15/memory-custodian-explainable-routing/)
* [Start with the series overview](/2026/07/01/memory-custodian/)
* [Read Part 2: Why Project Memory Should Be Plain Text and Repo-Native](/2026/07/20/memory-custodian-tech-design/)
* [View the implementation on GitHub](https://github.com/waittim/MemoryCustodian)
