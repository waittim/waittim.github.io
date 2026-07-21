---
layout: post
title: Designing Memory That Can Safely Forget
subtitle: Persistent memory is only trustworthy when deletion is deliberate, bounded, and reviewable.
date: 2026-07-21
author: Zekun
header-img: img/headers/2026-07-01-memory-custodian.png
catalog: true
tags:
- Coding Agent
- Agent Memory
- AI Safety
- Developer Tools
- Local First
- Data Governance
- Software Architecture
- Project
---


Most memory systems are judged by what they can retain.

Can they preserve context across sessions? Can they retrieve an old decision? Can they prevent an agent from repeating the same mistake?

Those questions matter. But a durable memory system should also be judged by what it can safely stop retaining.

A project decision may become obsolete. A constraint may no longer apply. A rejected approach may deserve reconsideration. An entry may have been promoted too early, written too broadly, or preserved without enough context.

Once memory becomes durable, forgetting is no longer a simple text-editing operation.

Removing the wrong line can change the meaning of the content around it. Deleting an active decision while retaining its archived copy may leave the project in an ambiguous state. Replacing a removed entry with a detailed tombstone may preserve the very topic that was supposed to disappear. Updating several files independently can produce a partially mutated repository that matches none of the user’s intended outcomes.

A trustworthy project-memory system must therefore do more than store and retrieve information.

It must govern how memory changes.

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

When a user says “forget this,” they may mean:

* Stop applying this guidance, but retain evidence that it was deliberately removed
* Remove the guidance and stop preserving its subject in active tombstones
* Remove the topic from all active and archived memory managed by the system

These requests have different semantic outcomes.

Treating them as equivalent forces the system into one of two bad defaults.

It may delete too little: the active entry disappears, but archived copies, topic-bearing tombstones, or generated metadata remain. The system claims to have forgotten something while continuing to preserve it elsewhere.

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

The tombstone still contains the topic.

That is intentional.

Soft forgetting prioritizes continuity. It records that the project stopped applying a particular memory and that restoring it should require an explicit decision.

This mode is appropriate when:

* The active guidance should stop
* The removal itself should remain visible
* The project wants protection against accidental reintroduction
* Retaining the subject of the removed memory is acceptable

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

This mode is appropriate when:

* The active guidance should stop
* Topic-bearing tombstones should not remain
* A generic warning against reconstruction is still useful
* Managed archives do not need to be rewritten

Hard forgetting is stronger than soft forgetting, but it is still not a complete managed-memory purge. Archived copies remain outside the scope of the operation.

### Purge

Purge is the strongest operation within MemoryCustodian’s managed-memory boundary.

It searches active and archived managed memory and removes entries and tombstones that preserve the requested topic.

Conceptually, it means:

> Remove this topic from the active and archived memory managed by MemoryCustodian.

A purge may examine:

* Confirmed decisions
* Active constraints
* Rejected approaches
* Inbox candidates
* Managed archives
* Earlier soft-forget tombstones
* Related generated records

This is no longer a single-file edit. It is a repository-level mutation.

Purge is appropriate when:

* The topic should disappear from active managed memory
* Earlier topic-bearing tombstones should disappear
* Archived managed copies should also be searched and removed
* The caller understands the limits of repository-scoped deletion

Those limits matter.

A purge can govern MemoryCustodian-managed files. It cannot claim to erase prior Git commits, remote forks, backups, existing clones, editor caches, provider-side records, or conversation histories outside the repository.

A trustworthy deletion model must state both what it can remove and what remains outside its control.

---

## Preview the Semantic Effect Before Writing

Deletion is one of the easiest operations to describe and one of the hardest to reverse safely.

That makes immediate mutation a poor default.

MemoryCustodian therefore separates planning from application.

A command such as:

```bash
memory-custodian forget "legacy deployment note" --mode soft
```

first produces a plan. It does not immediately change the repository.

The caller can inspect:

* Which files contain candidate matches
* Which complete entries would be removed
* Which tombstones would be created, preserved, replaced, or deleted
* Which archives would be affected
* Whether any match is ambiguous
* Whether the selected mode produces the intended outcome

Only an explicit apply operation performs the mutation:

```bash
memory-custodian forget "legacy deployment note" \
  --mode soft \
  --apply
```

This separation distinguishes two different decisions:

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

The purpose of preview is not merely to ask for confirmation.

It is to make the proposed state transition inspectable.

> **The caller should be able to disagree with the plan before the first write occurs.**

Preview also creates space for deliberate friction when the requested topic is too broad.

Consider:

```bash
memory-custodian forget "Go" --mode soft
```

`Go` might refer to the programming language, a product name, a heading, a package, or a common verb appearing throughout unrelated prose.

Automatically applying such a match would create unacceptable deletion risk.

A safe system should recognize short or broad topics, surface the risk, and require an additional acknowledgment before applying the plan. The extra step is not a complete semantic safety mechanism. It is an explicit signal that the caller accepts a wider matching surface.

This kind of friction is not accidental inconvenience.

It is part of making destructive behavior visible.

The same preview-first principle can extend beyond forgetting to other high-impact memory operations, including compaction, protocol migration, archive movement, route restructuring, bulk renaming, and scaffold replacement.

The broader rule is simple:

> **Mutation should be planned before it is performed.**

---

## Delete Complete Meaning, Not Matching Text

Memory stored in Markdown is not a collection of independent lines.

A decision may include a heading, a selected direction, supporting reasoning, nested bullets, scope limitations, examples, and references to related constraints.

Together, those elements form one semantic entry.

Consider:

```markdown
- Do not use SQLite for the current session store.
  - Existing files must remain human-readable.
  - The current data model does not require relational queries.
  - This restriction does not apply to future analytics storage.
```

A naïve line-based deletion might remove only the first line:

```markdown
  - Existing files must remain human-readable.
  - The current data model does not require relational queries.
  - This restriction does not apply to future analytics storage.
```

The remaining content is structurally broken. The reasoning has lost the statement it was intended to explain.

A different deletion might remove only the final scope limitation:

```markdown
- Do not use SQLite for the current session store.
  - Existing files must remain human-readable.
  - The current data model does not require relational queries.
```

This version still looks valid, but its meaning has changed. Future agents may interpret the restriction as more permanent or more general than the project intended.

The command may have succeeded syntactically while failing semantically.

> **Safety requires preserving the boundaries that carry meaning.**

MemoryCustodian therefore treats complete semantic entries as the minimum unit for mechanical mutation.

If a match belongs to a structured entry, the preview should identify the entire affected unit. The heading, reasoning, nested content, and scope should remain attached to one another.

This follows the same design principle used when loading memory into context: a scoped decision should not be truncated into a broader, misleading fragment. Forgetting applies that rule to mutation. The system should remove complete meaning, not matching tokens.

Not every match can be handled mechanically.

A topic may appear inside an ordinary paragraph:

```markdown
The first prototype used SQLite, but after testing several storage approaches,
the project moved toward human-readable files while retaining some of the old
migration utilities for compatibility.
```

Suppose the user asks to forget `SQLite`.

Removing only the matching word would produce damaged prose. Removing the entire paragraph would discard unrelated information about migration utilities and compatibility.

The correct result requires understanding and rewriting the paragraph.

That is a semantic task, not a deterministic deletion.

In such cases, the safe response is:

```text
Manual rewrite required.

The matching topic appears inside an unstructured paragraph containing
unrelated information. No files have been modified.
```

The operation should stop before the first write.

Refusing an ambiguous mutation is not a failure of automation. It is evidence that the system recognizes the limits of mechanical editing.

A trustworthy tool should distinguish between:

* Complete entries it can remove safely
* Structured regions it can transform predictably
* Ambiguous prose that requires semantic review

String matching can locate candidates.

It cannot, by itself, decide which surrounding meaning should survive.

---

## Plan the Whole Mutation Before the First Write

Many forgetting operations affect more than one file.

A soft forget might:

1. Remove an entry from `decisions.md`
2. Add a tombstone to `do-not-use.md`
3. Preserve an archived copy
4. Record operation metadata

A hard forget might also:

5. Locate an earlier topic-bearing soft tombstone
6. Replace it with a generic guard

A purge might additionally:

7. Search managed archives
8. Remove archived entries
9. Remove prior tombstones
10. Update archive references or generated indexes

These steps form one logical state transition.

If the system edits each file independently, an error can leave the repository in a state that matches none of the intended modes.

For example:

* The active decision is removed
* The tombstone is not created
* The archived copy remains
* The command exits with an error

The project has neither completed a soft forget nor preserved its original state.

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

Before writing, the system should determine:

* Every file that may change
* Every complete entry that will be removed
* Every tombstone that will be created, replaced, or deleted
* Every archive that will be searched or modified
* Every validation that must pass
* Whether any target requires a manual rewrite
* Whether the current protocol and file structure are supported

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

Preflight validation removes an important class of partial failures.

Consider a four-file operation where the fourth file is malformed.

Without complete-plan validation:

1. File one is changed
2. File two is changed
3. File three is changed
4. File four fails validation
5. The operation stops

The repository is now partially updated.

With preflight validation:

1. All four targets are inspected
2. The malformed file is detected
3. The operation stops
4. No files have changed

This does not eliminate every possible runtime failure. A disk can become unavailable, permissions can change, or a process can be interrupted after writing begins.

But it changes the most preventable failures from:

> We discovered the problem after modifying the repository.

to:

> We discovered the problem before the operation began.

When recovery material is appropriate, it should be created before destructive mutation.

A safe sequence is:

1. Build the complete plan
2. Validate every target
3. Create required recovery material
4. Apply bounded file changes
5. Revalidate the resulting structure
6. Report the exact outcome

An archive created after deletion is not a reliable recovery mechanism if the operation fails between the delete and archive steps.

The recovery path must exist before the action that may require recovery.

---

## Be Honest About Failure and Erasure Boundaries

Even a carefully planned filesystem operation cannot promise perfect atomicity in every environment.

Unexpected failures may still occur:

* Storage becomes unavailable
* Permissions change
* A file is externally modified
* A process is interrupted
* A rename fails
* Disk capacity is exhausted

A trustworthy tool should not hide that possibility behind a generic error.

If only part of a mutation completes, the report should explain the actual repository state:

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

The caller needs to know:

* Which files changed
* Which files did not change
* Which planned replacements were applied
* Which steps remain incomplete
* Where recovery material was written
* Whether the final memory structure passes validation

“Operation failed” is not enough when some writes may already have occurred.

The same honesty is required when describing deletion scope.

The word “purge” can imply stronger guarantees than a repository-local tool can provide.

MemoryCustodian can govern:

* Active managed memory
* Managed archives
* Managed tombstones
* Generated memory metadata
* Repository files inside its configured scope

It cannot guarantee removal from:

* Prior Git commits
* Remote repositories and forks
* Existing clones
* Filesystem backups
* Editor or operating-system caches
* CI artifacts
* Terminal history
* Model-provider records
* Conversation histories outside the repository
* Screenshots and exported copies

A purge removes the topic from MemoryCustodian’s managed-memory boundary.

It is not a claim of universal erasure.

This distinction should be part of the product model rather than hidden in a disclaimer.

Trust grows when a system describes its power accurately.

It also grows when the system refuses to invent the user’s intent.

The user or agent must decide:

* Which topic should be removed
* Which scope applies
* Whether soft, hard, or purge matches the desired outcome
* Whether similarly worded entries refer to the same concept
* Whether an ambiguous paragraph should be rewritten
* Whether the removal conflicts with current project policy

The CLI can then locate candidates, group complete entries, build the multi-file plan, validate the structure, create recovery material, apply approved changes, and report the result.

The semantic and deterministic responsibilities remain separate:

> **Humans and agents govern meaning. Deterministic tooling governs execution.**

---

## A Memory System Should Know How to Let Go

A memory system that can only accumulate information will eventually become less reliable.

Old decisions remain active after their assumptions change. Temporary workarounds become permanent rules. Contradictions multiply. Rejected approaches remain blocked after the reasons for rejecting them disappear. Unwanted information continues influencing future work because there is no safe mechanism for retiring it.

At that point, more memory produces less trust.

Safe forgetting is part of maintaining durable memory.

It allows a project to:

* Retire obsolete guidance
* Remove incorrect entries
* Narrow overbroad decisions
* Reconsider rejected approaches deliberately
* Separate active policy from historical records
* Remove topics from managed archives when necessary
* Keep future agent context aligned with the current project

Forgetting is not the opposite of persistence.

It is the process that prevents persistence from becoming accidental permanence.

A mature project-memory system should therefore make several guarantees.

Forgetting intentions should be explicit. Soft, hard, and purge should produce predictable and visibly different outcomes.

Destructive changes should be preview-first. The caller should understand the complete semantic effect before any file is modified.

Memory should be changed at semantic boundaries. Headings, reasoning, nested content, and scope limitations should remain attached to the entries they explain.

Ambiguous prose should require semantic review. A tool should stop rather than performing a confident-looking edit that damages unrelated meaning.

Multi-file changes should be planned as one operation. Every affected target should be known and validated before the first write.

Recovery should be prepared before destructive execution, and partial failures should be reported precisely.

Finally, deletion boundaries should be honest. Managed-memory purge is a bounded repository operation, not universal erasure.

These constraints make forgetting more deliberate and less automatic.

That is intentional.

Durable memory can influence future engineering work long after the interaction that created it. A system should not destroy that memory casually merely because it happens to be stored in Markdown.

The safer default is not to treat plain text as disposable.

It is to recognize that plain-text memory can carry high-impact project policy.

> **A memory system is not mature when it can remember everything. It is mature when it can forget the right thing without damaging what should remain.**

* [View MemoryCustodian on GitHub](https://github.com/waittim/MemoryCustodian)
* [Explore the NightNotes example](https://github.com/waittim/MemoryCustodian/tree/main/examples/nightnotes-video-demo)

**Deliberate forgetting. Reviewable change. Bounded memory.**
