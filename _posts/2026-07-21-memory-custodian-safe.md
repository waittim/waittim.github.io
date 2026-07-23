---
layout: post
title: Designing Memory That Can Safely Forget
subtitle: Persistent project memory is trustworthy only when forgetting is explicit, previewable, and bounded.
date: 2026-07-21
updated: 2026-07-21
author: Zekun Wang
description: "A design for safe agent-memory deletion using explicit forgetting modes, previews, semantic entries, and precomputed multi-file plans."
image: /img/headers/post-bg-memory-disk.jpg
series: MemoryCustodian Design Series
series_nav_title: Safe Forgetting
series_order: 3
header-img: img/headers/post-bg-memory-disk.jpg
catalog: true
tags:
    - Agent
    - Agent Memory
    - Developer Tools
    - Software Architecture
    - Local-First
    - Data Governance
    - AI
---

## What Makes Agent Memory Safe to Forget?

Safe forgetting makes deletion intent explicit, previews the complete semantic effect before writing, and plans every affected file as one mutation. It removes whole memory entries rather than matching text fragments and reports honestly when execution is incomplete.

*For developers building reviewable deletion and mutation workflows over durable agent memory. Implementation details in this article reflect MemoryCustodian v0.9.x.*

Most memory systems are judged by what they can retain.

Can they preserve context across sessions? Can they retrieve an old decision? Can they prevent an agent from repeating the same mistake?

Those questions matter. But a durable memory system should also be judged by what it can safely stop retaining.

A project decision may become obsolete. A constraint may no longer apply. A rejected approach may deserve reconsideration. An entry may have been promoted too early, written too broadly, or preserved without enough context.

Once memory becomes durable, forgetting is no longer a simple text-editing operation. Removing the wrong line can change the meaning of the content around it. Deleting an active decision while retaining its archived copy may leave the project in an ambiguous state. Replacing a removed entry with a detailed tombstone may preserve the very topic that was supposed to disappear. Updating several files independently can produce a partially mutated repository that matches none of the user’s intended outcomes.

A trustworthy project-memory system must therefore do more than store and retrieve information. It must govern how memory changes.

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) approaches this problem through four related design choices:

* Explicit forgetting modes
* Preview-first mutation
* Complete semantic entries
* Precomputed multi-file plans

Together, these choices treat forgetting as a governed state transition rather than an invisible side effect.

---

## Forgetting Is a Governance Problem

Remembering is usually additive.

A new decision can be added to `decisions.md`. A new constraint can be recorded in `constraints.md`. A rejected approach can be placed in `do-not-use.md`. The existing memory remains intact while the project gains a new entry.

Forgetting is destructive.

It must alter existing information without damaging the information that should remain. Depending on the request, it may need to remove active guidance, update tombstones, search archived memory, preserve unrelated reasoning, and coordinate changes across several files.

This creates a fundamental asymmetry:

> **Remembering can add information without disturbing existing meaning. Forgetting must change existing meaning without corrupting its surroundings.**

A generic delete command cannot express every forgetting intention safely.

When a user says “forget this,” they may mean that the active guidance should stop while evidence of its deliberate removal remains. They may instead want both the guidance and its subject removed from active managed memory. In the strongest case, they may want the topic removed from all active and archived memory managed by the system.

These requests have different semantic outcomes.

Treating them as equivalent forces the system into one of two bad defaults. It may delete too little: the active entry disappears, but archived copies, topic-bearing tombstones, or generated metadata remain. The system claims to have forgotten something while continuing to preserve it elsewhere.

Or it may delete too much: every trace disappears immediately, including useful governance context that would have prevented the same obsolete or rejected idea from quietly returning.

Safe forgetting begins by making the intended outcome explicit.

---

## Three Levels of Forgetting

MemoryCustodian represents three different forgetting intentions through `soft`, `hard`, and `purge` modes.

| Mode  | Active entries | Topic-bearing tombstones      | Managed archives     |
| ----- | -------------- | ----------------------------- | -------------------- |
| Soft  | Removed        | Retained or created           | Preserved            |
| Hard  | Removed        | Replaced with a generic guard | Preserved            |
| Purge | Removed        | Removed                       | Searched and removed |

The specific names are less important than the principle behind them:

> **Forgetting semantics should be explicit rather than hidden inside a generic delete operation.**

### Soft forgetting

Soft forgetting removes matching active entries while preserving a topic-bearing tombstone.

Conceptually, it means:

> Stop applying this memory, but retain evidence that its removal was deliberate.

Suppose the project contains:

```markdown
## Use the legacy export format

Continue generating the legacy export format for all new files.

Reasoning:
- Older clients cannot read the replacement format.
```

The compatibility requirement is later removed. The project no longer wants future agents to follow this decision, but it also does not want the old rule to return accidentally because someone rediscovers it in an issue, archive, or outdated design document.

A soft forget can remove the active decision while leaving a tombstone such as:

```markdown
- The previous guidance about the legacy export format was deliberately removed.
  Do not restore it without explicit review.
```

The tombstone still contains the topic. That is intentional.

Soft forgetting prioritizes continuity. It records that the project stopped applying a particular memory and that restoring it should require an explicit decision.

This mode is appropriate when the active guidance should stop, the removal itself should remain visible, and retaining the subject of the removed memory is acceptable.

### Hard forgetting

Hard forgetting removes matching active entries and stops preserving their subject in active managed tombstones.

Conceptually, it means:

> Remove the active memory and stop naming the forgotten topic in the governance record.

A soft tombstone such as:

```text
The previous decision about encrypting exported notes was deliberately removed.
```

still reveals that exported-note encryption was the subject of the removed memory.

That may be acceptable under soft forgetting. It is not acceptable when the goal is to stop retaining the topic itself inside active managed memory.

A hard forget therefore replaces a topic-bearing tombstone with a generic guard:

```text
A previous memory entry was deliberately removed.
Do not reconstruct or restore it without explicit user direction.
```

The guard preserves the governance boundary without preserving the forgotten subject.

This mode is appropriate when the active guidance should stop, topic-bearing tombstones should not remain, and a generic warning against reconstruction is still useful. Managed archives remain outside the scope of the operation.

### Purge

Purge is the strongest operation within MemoryCustodian’s managed-memory boundary.

It searches active and archived managed memory and removes entries and tombstones that preserve the requested topic.

Conceptually, it means:

> Remove this topic from the active and archived memory managed by MemoryCustodian.

A purge may examine confirmed decisions, active constraints, rejected approaches, inbox candidates, managed archives, earlier soft-forget tombstones, and related generated records. It is therefore not a single-file edit but a repository-level mutation.

Purge is appropriate when the topic should disappear from active managed memory, earlier topic-bearing tombstones should disappear, and archived managed copies should also be searched and removed.

Those limits matter. A purge can govern MemoryCustodian-managed files. It cannot claim to erase prior Git commits, remote forks, backups, existing clones, editor caches, provider-side records, or conversation histories outside the repository.

A trustworthy deletion model must state both what it can remove and what remains outside its control.

---

## Preview the Semantic Effect Before Writing

Deletion is one of the easiest operations to describe and one of the hardest to reverse safely.

That makes immediate mutation a poor default.

MemoryCustodian therefore separates planning from application. A command such as:

```bash
memory-custodian forget "legacy deployment note" --mode soft
```

first produces a plan. It does not immediately change the repository.

The caller can inspect which files contain candidate matches, which complete entries would be removed, which tombstones would be created or changed, which archives would be affected, and whether any match is ambiguous.

Only an explicit apply operation performs the mutation:

```bash
memory-custodian forget "legacy deployment note" \
  --mode soft \
  --apply
```

This separates two different decisions:

1. What should happen?
2. Should the prepared plan now be executed?

That distinction is essential for destructive operations.

A weak preview might say:

```text
Three matches found. Continue?
```

That is not enough.

A match count does not reveal what the repository will mean after the operation. Three matches could represent three independent decisions, one decision with nested reasoning, or a single topic repeated across active and archived files.

A useful preview should show the semantic effect of the plan:

```text
Forget mode: soft
Topic: legacy deployment process

Planned changes:

docs/memory/decisions.md
- Remove complete entry:
  "Use the legacy deployment process"

docs/memory/do-not-use.md
- Add topic-bearing tombstone:
  "The previous guidance about the legacy deployment process
   was deliberately removed."

docs/memory/archive/2026-06.md
- No change in soft mode

No files have been modified.
```

The purpose of preview is not merely to ask for confirmation. It is to make the proposed state transition inspectable.

> **The caller should be able to disagree with the plan before the first write occurs.**

Preview also creates space for deliberate friction when the requested topic is too broad.

Consider:

```bash
memory-custodian forget "Go" --mode soft
```

`Go` might refer to the programming language, a product name, a heading, a package, or a common verb appearing throughout unrelated prose. Automatically applying such a match would create unacceptable deletion risk.

A safe system should recognize short or broad topics, surface the risk, and require an additional acknowledgment before applying the plan. The extra step is not a complete semantic safety mechanism. It is an explicit signal that the caller accepts a wider matching surface.

This kind of friction is not accidental inconvenience. It is part of making destructive behavior visible.

The same preview-first principle can extend beyond forgetting to other high-impact memory operations, including compaction, protocol migration, archive movement, route restructuring, bulk renaming, and scaffold replacement.

The broader rule is simple:

> **Mutation should be planned before it is performed.**

---

## Delete Complete Meaning, Not Matching Text

Memory stored in Markdown is not a collection of independent lines.

A decision may include a heading, a selected direction, supporting reasoning, nested bullets, scope limitations, examples, and references to related constraints. Together, those elements form one semantic entry.

Consider:

```markdown
- Do not use the legacy deployment token in new environments.
  - Existing installations still require a migration path.
  - This restriction does not apply to local development.
```

A naïve line-based deletion might remove only the first line:

```markdown
  - Existing installations still require a migration path.
  - This restriction does not apply to local development.
```

The remaining content is structurally broken. The reasoning has lost the statement it was intended to explain.

A different deletion might remove only the final scope limitation:

```markdown
- Do not use the legacy deployment token in new environments.
  - Existing installations still require a migration path.
```

This version still looks valid, but its meaning has changed. Future agents may interpret the restriction as more permanent or more general than the project intended.

The command may have succeeded syntactically while failing semantically.

> **Safety requires preserving the boundaries that carry meaning.**

MemoryCustodian therefore treats complete semantic entries as the minimum unit for mechanical mutation. If a match belongs to a structured entry, the preview should identify the entire affected unit. The heading, reasoning, nested content, and scope should remain attached to one another.

This follows the same design principle used when loading memory into context, described in the [technical design article](/2026/07/20/memory-custodian-tech-design/): a scoped decision should not be truncated into a broader, misleading fragment. Forgetting applies that rule to mutation. The system should remove complete meaning, not matching tokens.

Not every match can be handled mechanically.

A topic may appear inside an ordinary paragraph:

```markdown
The first prototype reused the legacy deployment token, but after testing several
auth approaches, the project moved toward short-lived credentials while retaining
some of the old migration utilities for compatibility.
```

Suppose the user asks to forget `legacy deployment token`.

Removing only the matching phrase would produce damaged prose. Removing the entire paragraph would discard unrelated information about migration utilities and compatibility. The correct result requires understanding and rewriting the paragraph.

That is a semantic task, not a deterministic deletion.

In such cases, the safe response is:

```text
Manual rewrite required.

The matching topic appears inside an unstructured paragraph containing
unrelated information. No files have been modified.
```

The operation should stop before the first write.

Refusing an ambiguous mutation is not a failure of automation. It is evidence that the system recognizes the limits of mechanical editing.

A trustworthy tool should distinguish between complete entries it can remove safely, structured regions it can transform predictably, and ambiguous prose that requires semantic review.

String matching can locate candidates. It cannot, by itself, decide which surrounding meaning should survive.

---

## Plan the Whole Mutation Before the First Write

Many forgetting operations affect more than one file.

A soft forget might remove an entry from `decisions.md`, add a tombstone to `do-not-use.md`, preserve an archived copy, and record operation metadata. A hard forget may also need to find an earlier topic-bearing tombstone and replace it with a generic guard. A purge may additionally search managed archives, remove archived entries, delete earlier tombstones, and update archive references or generated indexes.

These steps form one logical state transition.

If the system edits each file independently, an error can leave the repository in a state that matches none of the intended modes. The active decision might be removed while the tombstone is never created, or the archived copy might remain after the command claims to have completed a purge.

Multi-file memory operations are transactions in disguise.

A local Markdown tool may not provide database-level transactions, but it can still adopt the most important transactional discipline: build and validate the complete operation before the first destructive write.

The workflow should be:

```text
Forgetting intent
  ↓
Select soft, hard, or purge
  ↓
Locate complete semantic entries
  ↓
Build the full multi-file plan
  ↓
Validate every target
  ↓
Create recovery material
  ↓
Apply bounded mutations
  ↓
Revalidate and report
```

Before writing, the system should determine every file that may change, every complete entry that will be removed, every tombstone that will be created or replaced, every archive that will be searched, and every validation that must pass. It should also identify whether any target requires a manual rewrite or uses an unsupported file structure.

A hard-forget plan might look like:

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

Recovery:
- create pre-mutation archive

Validation:
- all target files exist
- all matched regions align with complete entries
- no manual rewrites are required
- protocol metadata is supported

No writes have occurred.
```

Only after the plan is complete and valid should the mutation begin.

Preflight validation removes an important class of partial failures. If a four-file operation encounters a malformed fourth file, validating during execution would allow the first three files to change before the problem is discovered. Validating the complete plan first allows the system to stop without modifying anything.

This does not eliminate every possible runtime failure. A disk can become unavailable, permissions can change, or a process can be interrupted after writing begins. But it converts the most preventable failures from problems discovered after mutation into problems discovered before execution.

When recovery material is appropriate, it should be created before destructive mutation. An archive created after deletion is not a reliable recovery mechanism if the operation fails between the delete and archive steps.

The recovery path must exist before the action that may require recovery.

---

## Be Honest About Failure and Erasure Boundaries

Even a carefully planned filesystem operation cannot guarantee perfect atomicity in every environment. Storage may become unavailable, permissions may change, a file may be modified externally, or the process may be interrupted after one write succeeds and before the next begins.

A trustworthy tool should report the repository’s actual state rather than hide partial completion behind a generic error. If only part of a mutation succeeds, the result should identify which files changed, which planned steps remain incomplete, where recovery material was written, and whether the resulting memory structure still passes validation.

For example:

```text
The mutation completed partially.

Completed:
- Removed matching entry from decisions.md
- Created pre-mutation archive

Incomplete:
- Could not update do-not-use.md
- Generic guard was not written

The repository does not fully reflect the requested hard-forget state.
Review the saved plan and recovery archive before continuing.
```

The important information is not merely that the command failed. The user needs to know whether the active decision is already gone, whether the intended tombstone exists, and whether the repository currently represents any valid forgetting mode.

The same honesty is required when describing deletion scope.

The word `purge` can imply universal erasure, but MemoryCustodian operates within a defined project boundary. It can remove active managed entries, managed archives, managed tombstones, and generated memory metadata stored within the configured repository structure.

It cannot erase information from prior Git commits, remote forks, existing clones, backups, caches, CI artifacts, model-provider systems, external conversation histories, screenshots, or exported copies.

A purge therefore means:

> Remove the topic from the active and archived memory managed by MemoryCustodian.

It does not mean that the topic has ceased to exist everywhere.

This limitation should be part of the product model rather than buried in a disclaimer. Trust depends on describing deletion power accurately.

The boundary between semantic and deterministic work must also remain explicit. A human or agent decides which topic should be removed, which scope applies, and whether soft, hard, or purge matches the desired outcome. It must also determine whether similarly worded entries refer to the same concept and whether an ambiguous paragraph should be rewritten rather than deleted.

The CLI then performs the work that can be enforced mechanically: locating candidates, grouping complete entries, building the multi-file plan, validating structure, creating recovery material, applying approved changes, and reporting the final state.

> **Humans and agents govern meaning. Deterministic tooling governs execution.**

---

## A Memory System Should Know How to Let Go

A memory system that can only accumulate information will eventually become less reliable.

Old decisions remain active after their assumptions change. Temporary workarounds become permanent rules. Contradictions multiply. Rejected approaches remain blocked even after the reasons for rejecting them disappear. Unwanted information continues influencing future work because there is no safe mechanism for retiring it.

At that point, more memory produces less trust.

Safe forgetting is part of maintaining durable memory. It allows a project to retire obsolete guidance, remove incorrect entries, narrow overbroad decisions, reconsider rejected approaches deliberately, and keep future agent context aligned with the project as it exists now.

Forgetting is not the opposite of persistence. It is the process that prevents persistence from becoming accidental permanence.

That process should be explicit about intent, previewable before execution, bounded by semantic structure, and planned across every affected file. When a change cannot be performed mechanically without damaging meaning, the system should stop and require review. When execution fails partially, it should report the actual state. When deletion reaches the edge of the managed repository, it should state that boundary honestly.

These constraints make forgetting slower than a generic string deletion.

That is intentional.

Durable memory can influence engineering work long after the interaction that created it. The fact that the memory is stored in Markdown does not make it disposable. Plain-text entries can still carry high-impact project policy, product constraints, and architectural reasoning.

A trustworthy system should therefore be conservative about destroying them.

> **A memory system is not mature when it can remember everything. It is mature when it can forget the right thing without damaging what should remain.**

## Key Takeaways

* Forgetting is a governed state transition, not a generic string deletion.
* Soft, hard, and purge modes represent meaningfully different outcomes.
* Users should review the semantic effect and all affected files before mutation.
* Complete entries, recovery material, and honest partial-failure reports protect the memory that remains.

## Frequently Asked Questions

### What is the difference between soft, hard, and purge forgetting?

Soft forgetting removes active guidance while retaining topic-bearing evidence. Hard forgetting removes the topic from active guidance and replaces it with a generic guard. Purge also searches and removes the topic from managed archives.

### Does purge erase the topic everywhere?

No. It removes the topic from active and archived memory managed by MemoryCustodian. It cannot erase prior Git commits, forks, clones, backups, caches, external chats, or exported copies.

### Why preview a forgetting operation?

A preview lets a person or agent verify the intended outcome, semantic entry boundaries, and every affected file before destructive writes begin. It also creates a clear basis for recovery if execution is interrupted.

* [Start with the series overview](/2026/07/01/memory-custodian/)
* [Read Part 2: Why Project Memory Should Be Plain Text and Repo-Native](/2026/07/20/memory-custodian-tech-design/)
* [View the implementation on GitHub](https://github.com/waittim/MemoryCustodian)

**Deliberate forgetting. Reviewable change. Bounded memory.**
