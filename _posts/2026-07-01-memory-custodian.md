---
layout:     post
title:      "MemoryCustodian: Durable Project Memory for Coding Agents"
subtitle:   "Memory can grow; context must stay small."
date:       2026-07-01
author:     Zekun
header-img: img/headers/post-bg-data-center.jpeg
catalog: true
tags:
    - Coding Agent
    - Agent Memory
    - AI
    - Developer Tools
    - CLI
    - Local First
    - Markdown
    - Project
    - Agent
---

Coding agents are getting better at writing code, tracing bugs, and navigating unfamiliar repositories.

But every new session still tends to begin with the same problem:

> **The agent can read the code, but it does not remember why the project looks the way it does.**

It may not know that an architectural choice was deliberate. It may suggest an approach that was already tested and rejected. It may overlook an offline requirement, a compatibility boundary, or a product constraint that never appeared directly in the source code.

So developers repeat themselves.

They paste the same background into new conversations. They add more instructions to `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`. Over time, those files become increasingly large collections of decisions, preferences, warnings, and historical context.

The project gains memory, but every task pays the full context cost.

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) takes a different approach:

> **Memory can grow; context must stay small.**

MemoryCustodian gives coding agents durable project memory using plain Markdown files stored inside the repository. Instead of loading the entire project history into every session, it selects only the decisions, constraints, and rejected approaches relevant to the current task.

Record important knowledge once. Let future sessions, different coding agents, and the rest of the team recover it from the repository.

* [Watch the demo](https://www.youtube.com/watch?v=mYKzzATlOPw)
* [View MemoryCustodian on GitHub](https://github.com/waittim/MemoryCustodian)
* [Explore the NightNotes example](https://github.com/waittim/MemoryCustodian/tree/main/examples/nightnotes-video-demo)

---

## The Problem Is Not Missing Code

Source code is good at describing what a system does today.

It is much less reliable at explaining:

* Why one design was chosen over another
* Which constraints must remain true
* Which alternatives were already rejected
* Which decisions apply only to one subsystem
* Which temporary ideas should not become permanent
* Which corrections should carry into future sessions

That knowledge often lives in old chats, pull-request discussions, personal notes, or the memory of the developer who made the decision.

A new coding-agent session does not automatically inherit any of it.

Consider a small application that needs persistent session storage.

The agent inspects the repository and proposes SQLite. That sounds reasonable—but the project already rejected SQLite because stored files must remain human-readable and portable.

You explain the decision.

A week later, a different session proposes SQLite again.

The problem is not that the agent cannot understand SQLite. The problem is that the project’s reasoning was never stored somewhere the next session could reliably recover.

---

## See It in Action

The MemoryCustodian repository includes an intentionally incomplete example project called [NightNotes](https://github.com/waittim/MemoryCustodian/tree/main/examples/nightnotes-video-demo).

NightNotes is a small command-line application for storing session notes. Its initial implementation keeps notes only in memory, while an acceptance test documents the missing persistence behavior.

The repository already contains several durable project decisions:

* Persistent state should use human-readable local JSON
* Routine operation must work without network access
* The application should use only the Python standard library
* Existing note files must remain human-readable
* SQLite should not be introduced for the current session store

Now imagine starting a completely new coding-agent session with this prompt:

```text
Plan how to implement persistent session state.

Before proposing changes, use the repository's project memory. Explain which
existing decisions, constraints, and rejected approaches influenced your plan.

Do not modify any files.
```

The prompt does not mention JSON.

It does not mention SQLite.

It does not mention offline operation or dependency restrictions.

The agent must recover those facts from the repository’s project memory.

That is the central promise of MemoryCustodian:

> **A new session can recover the project’s durable reasoning without loading an entire conversation history.**

---

## How MemoryCustodian Works

MemoryCustodian stores project knowledge under:

```text
docs/memory/
```

A typical project begins with a small set of Markdown files:

```text
docs/memory/
  manifest.md
  brief.md
  decisions.md
  constraints.md
  do-not-use.md
  inbox.md
```

Each file has a clear purpose.

* `brief.md` describes the current project direction
* `decisions.md` records confirmed choices and their reasoning
* `constraints.md` stores requirements that must remain true
* `do-not-use.md` preserves rejected approaches
* `inbox.md` holds candidates that still require review
* `manifest.md` determines which memory files apply to each type of task

The key is the manifest.

A planning task may need the project brief, architectural decisions, constraints, and rejected approaches.

A documentation task may need the project brief and writing preferences, but not infrastructure history.

A subsystem-specific task may require one area file without loading the memory of the entire repository.

MemoryCustodian turns memory loading into an explicit routing decision:

> **What should the agent remember for this task?**

The repository may accumulate more knowledge over time, while the active context remains small and task-specific.

---

## Before MemoryCustodian

A typical long-running coding-agent workflow looks like this:

```text
A new session starts.

The agent reads the repository.

It proposes a previously rejected architecture.

You explain the old decision again.

You restate the project constraints.

You add another paragraph to an instruction file.

The same discussion returns in a later session.
```

Different tools may also receive different versions of the project context.

Codex knows one set of rules. Claude Code knows another. A teammate’s environment contains neither. Important decisions remain tied to a particular conversation or local setup.

---

## After MemoryCustodian

The project records durable knowledge once.

Before beginning substantial work, the agent:

1. Reads the project manifest
2. Identifies the current task category
3. Loads the relevant memory files
4. Respects active decisions, constraints, and rejected paths
5. Proposes memory updates only when new knowledge deserves to persist

The result is a shared project memory that can survive across:

* Separate agent sessions
* Different coding-agent platforms
* Different developer machines
* Individual and team workflows
* Pull-request review
* Version-control history

The memory belongs to the repository—not to a single chat window or proprietary memory store.

---

## Review Memory Like Code

A project decision may influence months of future work.

That decision should be visible.

MemoryCustodian uses ordinary Markdown because project memory should be:

* Human-readable
* Easy to edit
* Diffable in Git
* Reviewable in pull requests
* Reversible
* Portable across tools
* Available offline

A team can see when a constraint was introduced. A developer can challenge an outdated decision. A rejected approach can be deliberately reconsidered rather than silently disappearing inside an opaque retrieval system.

MemoryCustodian does not require a separate memory service or retrieval stack for routine use.

It works with tools developers already understand:

> **Files, folders, Markdown, and Git.**

The simplicity is not a limitation of the product. It is part of the product.

---

## Store Decisions, Not Conversations

MemoryCustodian is not designed to archive everything an agent has ever seen.

Most conversation content should not become permanent project memory.

Temporary thoughts, unfinished ideas, speculative suggestions, and one-off debugging observations can quickly turn a memory system into another unstructured context dump.

MemoryCustodian focuses on a smaller set of durable knowledge:

* Current project direction
* Confirmed architectural and product decisions
* Constraints that must remain true
* Rejected approaches that should not quietly return
* Subsystem-specific knowledge
* Repeated corrections and stable preferences
* Candidate memories awaiting review

The goal is not maximum memory.

The goal is:

> **Useful continuity with controlled context cost.**

---

## Agents Decide Meaning; the CLI Enforces Structure

Determining whether a statement is a decision, constraint, idea, or rejected approach requires semantic judgment.

Consider this candidate:

```text
Consider encrypting exported notes with a user-provided passphrase.
```

Is it a confirmed requirement?

A possible future feature?

A security constraint?

A speculative idea?

A deterministic script cannot reliably answer that from keywords alone.

MemoryCustodian keeps the boundary clear:

* The agent or user decides what the information means
* The CLI validates and applies the operation safely

The agent handles interpretation, scope, confidence, overlap, and contradictions.

The CLI handles deterministic work such as route resolution, structural validation, exact duplicate detection, context budgets, previews, and bounded file updates.

> **The agent understands meaning. The CLI enforces the resulting operation safely.**

This makes the system conservative by design. Memory is curated rather than accumulated automatically.

---

## Durable Memory Without Permanent Full-Context Loading

Many approaches to persistent agent context appear to require a tradeoff:

* Keep more memory and increase context usage
* Keep context small and lose continuity

MemoryCustodian separates stored memory from active context.

The repository may contain decisions, constraints, subsystem notes, rejected paths, preferences, and archived material.

A single task does not need all of them.

For example, a planning task might load:

```text
manifest.md
brief.md
decisions.md
constraints.md
do-not-use.md
```

A user-facing writing task might load:

```text
manifest.md
brief.md
preferences.md
```

A task scoped to one component might load only:

```text
manifest.md
brief.md
areas/payments.md
```

The exact routes belong to the project and remain visible in `manifest.md`.

This also keeps platform-specific instruction files thin. `AGENTS.md`, `CLAUDE.md`, and similar files only need to point the agent toward the shared memory protocol instead of duplicating the project’s entire history.

---

## A 60-Second Start

MemoryCustodian requires Python 3.10 or later.

Clone the repository:

```bash
git clone https://github.com/waittim/MemoryCustodian.git
cd MemoryCustodian
```

Initialize memory in a project:

```bash
scripts/memory-custodian init \
  --project-root /path/to/project \
  --agent all
```

Check the generated memory structure:

```bash
scripts/memory-custodian check \
  --project-root /path/to/project
```

Inspect the context selected for a planning task:

```bash
scripts/memory-custodian read \
  --project-root /path/to/project \
  --task planning
```

The initializer creates a scaffold rather than pretending to understand the repository automatically.

Review the generated files, then curate `brief.md`, decisions, constraints, and rejected approaches from authoritative project information.

Once initialized, the project itself becomes the source of durable agent context.

---

## Try the NightNotes Example

Clone MemoryCustodian and inspect the included demo:

```bash
git clone https://github.com/waittim/MemoryCustodian.git
cd MemoryCustodian
```

Validate the NightNotes memory:

```bash
scripts/memory-custodian check \
  --project-root examples/nightnotes-video-demo
```

Read the planning context:

```bash
scripts/memory-custodian read \
  --project-root examples/nightnotes-video-demo \
  --task planning
```

The resulting context should recover:

* The JSON persistence decision
* The offline-operation constraint
* The standard-library restriction
* The rejected SQLite approach

A separate encryption idea remains in the inbox because it has not yet been promoted into trusted project memory.

The example is deliberately incomplete. Its failing acceptance test defines the task that the coding agent must plan and implement.

MemoryCustodian supplies the reasoning the new session would otherwise be missing.

---

## Who Is MemoryCustodian For?

MemoryCustodian is useful when:

* A project spans many coding-agent sessions
* You repeatedly explain the same decisions
* Rejected approaches keep returning
* Instruction files are becoming too large
* Multiple coding agents work on the same repository
* Important constraints must survive across sessions
* A team wants memory changes to be reviewable
* Local, transparent, version-controlled memory matters

It is especially useful for long-running projects where continuity matters more than remembering every detail.

MemoryCustodian is not a replacement for source documentation, a general-purpose document search engine, or an archive of every conversation.

It is a governance layer for the small set of project knowledge that should reliably shape future agent behavior.

---

## Make the Next Session Better

Coding agents do not need an unlimited transcript of everything that happened before.

They need trustworthy answers to a smaller set of questions:

* What is this project trying to do?
* What decisions are already settled?
* What constraints must not be broken?
* What approaches should not be proposed again?
* What context is relevant to this task?
* Which new observations deserve to persist?

MemoryCustodian keeps those answers inside the repository, where developers, teammates, and agents can inspect them.

Its design is intentionally restrained:

* Store durable memory as plain Markdown
* Keep platform instruction files thin
* Route context through a manifest
* Load only what each task needs
* Let agents decide meaning
* Let deterministic tooling enforce structure
* Keep memory changes deliberate and reviewable
* Keep routine operation local and portable

MemoryCustodian is not a smarter black box.

It is a disciplined way to help coding agents carry a project forward instead of repeatedly relearning it.

> **Record the decision once. Let every future session inherit it.**

* [Watch the demo](https://www.youtube.com/watch?v=mYKzzATlOPw)
* [View the project on GitHub](https://github.com/waittim/MemoryCustodian)
* [Try the NightNotes example](https://github.com/waittim/MemoryCustodian/tree/main/examples/nightnotes-video-demo)

**Durable memory. Minimal context.**
