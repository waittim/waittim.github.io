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

Safe forgetting makes deletion intent explicit, previews the complete semantic effect before writing, and plans every affected file as one mutation. It removes whole memory entries rather than matching text fragments, respects a clearly defined erasure boundary, and reports honestly when execution is incomplete.

*For developers building reviewable deletion and mutation workflows over durable agent memory. The CLI examples and three forgetting modes reflect MemoryCustodian v0.9.x. The stronger transaction, recovery, and structured erasure-reporting behaviors described as requirements below represent the design direction for upcoming releases.*

Most memory systems are judged by what they can retain.

Can they preserve context across sessions? Can they retrieve an old decision? Can they prevent an agent from repeating the same mistake?

Those questions matter. But a durable memory system should also be judged by what it can safely stop retaining.

A project decision may become obsolete. A constraint may no longer apply. A rejected approach may deserve reconsideration. An entry may have been promoted too early, written too broadly, or preserved without enough context.

Once memory becomes durable, forgetting is no longer a simple text-editing operation. Removing the wrong line can change the meaning around it. Deleting active guidance while retaining another managed copy may leave the project in an ambiguous state. Replacing a removed entry with a detailed tombstone may preserve the topic that was supposed to disappear. Updating several files independently can produce a partially mutated memory store that matches none of the user’s intended outcomes.

A trustworthy project-memory system must therefore do more than store and retrieve information. It must govern how memory changes.

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) approaches this problem through four related design choices:

* Explicit forgetting modes
* Preview-first mutation
* Complete semantic entries
* Precomputed multi-file plans

Together, these choices treat forgetting as a governed state transition rather than an invisible side effect.

<img class="theme-surface" src="{{ "/img/posts/2026-07-21-memory-custodian-safe/gallery-safe-forgetting.png" | relative_url }}" alt="Safe forgetting workflow: Preview generates a dry-run plan, Review checks semantic units and blockers, Apply re-runs with --apply; supports soft, hard, and purge modes over plain Markdown" title="Memory you can review—and safely forget" width="1270" height="760" loading="lazy" decoding="async">

---

## Forgetting Is a Governance Problem

Remembering is usually additive.

A new decision can be added to `decisions.md`. A new constraint can be recorded in `constraints.md`. A rejected approach can be placed in `do-not-use.md`. Existing memory remains intact while the project gains a new entry.

Forgetting is destructive.

It must alter existing information without damaging what should remain. Depending on the request, it may need to remove active guidance, update tombstones, search archived memory, preserve unrelated reasoning, and coordinate changes across several files.

This creates a fundamental asymmetry:

> **Remembering can add information without disturbing existing meaning. Forgetting must change existing meaning without corrupting its surroundings.**

A generic delete command cannot safely express every forgetting intention.

When a user says “forget this,” they may mean that active guidance should stop while evidence of its deliberate removal remains. They may instead want both the guidance and its subject removed from active managed memory. In the strongest mode, they may want the topic removed from all active and archived memory managed by the system.

These requests have different semantic outcomes.

Treating them as equivalent creates two bad defaults. The system may delete too little: the active entry disappears, but archived copies, topic-bearing tombstones, or generated metadata remain. Or it may delete too much: useful governance context disappears, allowing an obsolete or rejected idea to return without review.

Safe forgetting begins by making the intended outcome explicit.

---

## Three Levels of Forgetting

MemoryCustodian represents three forgetting intentions through `soft`, `hard`, and `purge` modes.

| Mode  | Active entries | Topic-bearing tombstones      | Managed archives     | Git history | Distributed copies |
| ----- | -------------- | ----------------------------- | -------------------- | ----------- | ------------------ |
| Soft  | Removed        | Retained or created           | Preserved            | Unchanged   | Outside control    |
| Hard  | Removed        | Replaced with a generic guard | Preserved            | Unchanged   | Outside control    |
| Purge | Removed        | Removed                       | Searched and removed | Unchanged   | Outside control    |

> **All three modes operate only within MemoryCustodian-managed files. None rewrites Git history or revokes copies already present in clones, forks, backups, caches, or external systems.**

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

A soft forget can remove the active decision while leaving a structured tombstone:

```markdown
## Tombstone: legacy export format

Do not reintroduce unless the user explicitly reverses this.

Reason: the user asked MemoryCustodian to forget this topic.  
Mode: soft.  
Date: YYYY-MM-DD.
```

The tombstone still contains the topic. That is intentional.

Soft forgetting prioritizes continuity. It records that the project stopped applying a particular memory and that restoring it should require an explicit decision.

### Hard forgetting

Hard forgetting removes matching active entries and stops preserving their subject in active managed tombstones.

Conceptually, it means:

> Remove the active memory and stop naming the forgotten topic in the governance record.

A soft tombstone can still reveal the subject of the removed memory. That may be acceptable under soft forgetting, but not when the goal is to stop retaining the topic inside active managed memory.

A hard forget therefore replaces a topic-bearing tombstone with a generic guard:

```text
A previous memory entry was deliberately removed.
Do not reconstruct or restore it without explicit user direction.
```

The guard preserves the governance boundary without preserving the forgotten subject. Managed archives remain outside the scope of hard mode.

### Purge

Purge is the strongest operation within MemoryCustodian’s managed-memory boundary.

It searches active and archived managed memory and removes entries and tombstones that preserve the requested topic.

Conceptually, it means:

> Remove this topic from the active and archived memory managed by MemoryCustodian.

A purge may examine confirmed decisions, active constraints, rejected approaches, inbox candidates, managed archives, earlier soft-forget tombstones, and related managed records. It is therefore not a single-file edit but a managed-memory-wide mutation.

Purge does not mean “erase this everywhere.” Git history and previously distributed copies remain outside the protocol’s control.

Choosing a mode can be reduced to a short decision tree:

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

The purpose of preview is not merely to ask for confirmation. It is to make the proposed state transition inspectable.

> **The caller should be able to disagree with the plan before the first write occurs.**

Preview also creates deliberate friction when the requested topic is broad. A request such as:

```bash
memory-custodian forget "Go" --mode soft
```

might refer to a programming language, product name, heading, package, or common verb. A safe system should surface the wider matching risk and require additional acknowledgment before applying the plan.

The broader rule is simple:

> **Mutation should be planned before it is performed.**

---

## Delete Complete Meaning, Not Matching Text

Memory stored in Markdown is not a collection of independent lines.

A decision may include a heading, selected direction, reasoning, nested bullets, scope limitations, examples, and references. Together, those elements form one semantic entry.

As described in the [technical design article](/2026/07/20/memory-custodian-tech-design/), scoped decisions must stay complete when loaded into context. Forgetting applies the same rule to mutation: remove complete meaning, not matching tokens.

Consider:

```markdown
- Do not use the legacy deployment token in new environments.
  - Existing installations still require a migration path.
  - This restriction does not apply to local development.
```

Removing only the matching first line would leave structurally broken reasoning. Removing only the final scope limitation would leave apparently valid text whose meaning had silently changed.

> **Safety requires preserving the boundaries that carry meaning.**

MemoryCustodian therefore treats complete semantic entries as the minimum unit for mechanical mutation. If a match belongs to a structured entry, the preview should identify the entire affected unit.

Not every match can be handled mechanically. A topic may appear inside an ordinary paragraph containing unrelated information. Removing only the phrase would damage the prose, while deleting the entire paragraph would discard information that should remain.

In such cases, the safe response is:

```text
Manual rewrite required.

The matching topic appears inside an unstructured paragraph containing
unrelated information. No files have been modified.
```

Refusing an ambiguous mutation is not a failure of automation. It shows that the system recognizes the limits of deterministic editing.

String matching can locate candidates. It cannot decide which surrounding meaning should survive.

---

## Plan the Whole Mutation Before the First Write

Many forgetting operations affect more than one file.

A soft forget may remove an entry from `decisions.md` and add a tombstone to `do-not-use.md`. A hard forget may also replace an earlier topic-bearing tombstone with a generic guard. A purge may search managed archives and remove related active, archived, and tombstone entries.

These steps form one logical state transition. If files are edited independently, an error can leave the memory store in a state that matches none of the intended modes.

Multi-file memory operations are transactions in disguise.

A local Markdown tool may not provide database-level transactions, but it can still adopt the most important discipline: build and validate the complete operation before the first destructive write.

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

Before writing, the system should determine every file that may change, every complete entry that will be removed, every tombstone that will be created or replaced, every archive that will be searched, and every validation that must pass.

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

Recovery behavior must respect the selected mode.

Soft forgetting may preserve ordinary recovery material because the mode intentionally retains topic-bearing governance evidence and managed archives. Hard and purge operations, however, should not create new topic-bearing backups, journals, or archives that contradict the requested removal scope.

For purge, recoverability and removal intent may conflict. The tool should make that tradeoff explicit rather than silently retaining another copy:

```text
Recovery behavior for purge:
- no persistent topic-bearing recovery copy will be created
- structural operation metadata will remain generic
```

This does not eliminate every runtime failure. Storage can become unavailable, permissions can change, or a process can be interrupted. But complete preflight validation moves preventable failures from the middle of execution to before the first write.

---

## Be Honest About Failure and Erasure Boundaries

Even a carefully planned filesystem operation cannot guarantee perfect atomicity in every environment. A trustworthy tool should report the actual state rather than hide partial completion behind a generic error.

For example:

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

The user needs to know whether active guidance is already gone, whether the intended guard exists, and whether the memory store currently represents any valid forgetting mode.

The same honesty is required when describing deletion scope:

> **MemoryCustodian forgetting controls what remains available to future agents through its managed memory. It is not a guarantee of erasure from Git history or previously distributed copies.**

Even rewriting a remote repository’s history cannot revoke every clone, fork, cache, backup, or exported copy. That limitation should be part of the product model rather than buried in a disclaimer.

### Repo-native memory is not a secret store

Repo-native memory inherits Git’s distribution and retention model. Credentials, private keys, personal data, full contract terms, and unnecessarily specific vendor information should not be written into project memory.

Store the minimum operational constraint needed by the agent, and reference a protected source when more detail is required.

Instead of:

```markdown
Vendor Z limits account ABC-8291 to 12,500 requests under our contract with Company Y.
```

prefer:

```markdown
This integration must respect the externally defined vendor rate limit.

Evidence: internal/vendor-policy.md
```

The precise evidence location should itself be included only when sharing that reference is appropriate for the repository.

The boundary between semantic and deterministic work must also remain explicit. A human or agent decides which topic should be removed, which mode matches the desired outcome, and whether similarly worded entries refer to the same concept. Deterministic tooling can then locate candidates, group complete entries, validate the multi-file plan, apply approved changes, and report the final state.

> **Humans and agents govern meaning. Deterministic tooling governs execution.**

---

## A Memory System Should Know How to Let Go

A memory system that can only accumulate information will eventually become less reliable.

Old decisions remain active after their assumptions change. Temporary workarounds become permanent rules. Contradictions multiply. Rejected approaches remain blocked even after the reasons for rejecting them disappear. Unwanted information continues influencing future work because there is no safe mechanism for retiring it.

At that point, more memory produces less trust.

Safe forgetting allows a project to retire obsolete guidance, remove incorrect entries, narrow overbroad decisions, and reconsider rejected approaches deliberately. Forgetting is not the opposite of persistence. It is the process that prevents persistence from becoming accidental permanence.

That process should be explicit about intent, previewable before execution, bounded by semantic structure, and planned across every affected managed file. It should stop when meaning cannot be changed safely, report partial execution honestly, and state where its erasure authority ends.

These constraints make forgetting slower than generic string deletion. That is intentional.

Durable Markdown memory can influence engineering work long after the interaction that created it. Plain text is inspectable, but it is not disposable. It can carry high-impact policy, product constraints, architectural reasoning, and occasionally information that should never have been committed in the first place.

A trustworthy memory system should therefore be conservative about both retaining and destroying information.

> **A memory system is not mature when it can remember everything. It is mature when it can forget the right thing without damaging what should remain—or claiming to erase what it cannot control.**

## Key Takeaways

* Forgetting is a governed state transition, not generic string deletion.
* Soft, hard, and purge represent different outcomes within managed memory.
* Preview and validation should cover the complete semantic and multi-file effect.
* Hard and purge operations should not create new topic-bearing recovery copies.
* Forgetting does not rewrite Git history or revoke distributed copies.
* Repo memory should preserve minimal operational constraints, not raw sensitive material.

## Frequently Asked Questions

### What is the difference between soft, hard, and purge forgetting?

Soft forgetting removes active guidance while retaining topic-bearing evidence. Hard forgetting removes the topic from active guidance and replaces its active tombstone with a generic guard. Purge also searches and removes the topic from managed archives.

### Does purge erase the topic everywhere?

No. Purge extends forgetting into MemoryCustodian-managed archives, but it does not rewrite Git history or revoke copies in clones, forks, backups, caches, or external systems.

### Can MemoryCustodian safely store secrets or detailed contract information?

No. Repo-native memory inherits the repository’s distribution and retention model. Store only the minimum operational constraint needed by the agent and keep sensitive source material in an appropriately protected system.

### Why preview a forgetting operation?

A preview lets a person or agent verify the intended mode, semantic entry boundaries, affected files, recovery behavior, and erasure boundary before destructive writes begin.

* [Start with the series overview](/2026/07/01/memory-custodian/)
* [Read Part 2: Why Project Memory Should Be Plain Text and Repo-Native](/2026/07/20/memory-custodian-tech-design/)
* [View the implementation on GitHub](https://github.com/waittim/MemoryCustodian)

**Deliberate forgetting. Reviewable change. Bounded memory.**
