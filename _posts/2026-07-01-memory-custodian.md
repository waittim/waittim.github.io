---
layout:     post
title:      "MemoryCustodian: Durable Project Memory for Coding Agents"
subtitle:   "Memory can grow; context must stay small."
date:       2026-07-01
updated:    2026-07-21
author:     Zekun Wang
description: "MemoryCustodian gives coding agents durable, reviewable project memory using repo-native Markdown, Git history, and task-specific context routing."
image: /img/headers/2026-07-01-memory-custodian.png
series: MemoryCustodian Design Series
series_nav_title: Overview
header-img: img/headers/post-bg-data-center.jpeg
catalog: true
tags:
    - Agent
    - Agent Memory
    - Developer Tools
    - Software Architecture
    - Local-First
    - CLI
    - AI
---

## What Is MemoryCustodian?

MemoryCustodian is a repo-native memory protocol and CLI for coding agents. It stores durable project decisions and constraints in plain Markdown, keeps their history in Git, and loads only the files relevant to the current task.

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

* [Watch the demo](#demo)
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

## Before and After MemoryCustodian

| Without project memory | With MemoryCustodian |
|---|---|
| Each session reconstructs old decisions | Decisions are recovered from the repository |
| Rejected approaches return | Tombstones preserve rejected paths |
| Instruction files keep growing | Bootstrap files stay thin |
| Every task receives the same context | The manifest loads task-relevant memory |
| Context differs across agents | Agents share one repo-native authority |

The memory belongs to the repository—not to a single chat window or proprietary memory store.

---

## Review Memory Like Code

MemoryCustodian stores project memory as ordinary Markdown so changes remain visible, diffable, and reviewable in Git.

The architectural reasoning behind this choice—including manifest routing and the boundary between semantic judgment and deterministic enforcement—is explored in the [technical design article](/2026/07/20/memory-custodian-tech-design/).

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

Deciding whether a statement is a decision, constraint, idea, or rejected approach requires semantic judgment, so the agent (or user) decides what the information means while the CLI validates and applies the operation safely. This keeps memory curated rather than accumulated automatically. How that boundary works—and why it makes the system conservative by design—is covered in the [technical design article](/2026/07/20/memory-custodian-tech-design/).

---

## A 60-Second Start

The simplest way to begin is to let your coding agent install and initialize MemoryCustodian for you:

```text
Install the MemoryCustodian skill from
https://github.com/waittim/MemoryCustodian,
then initialize it for this project.
```

You can also install it directly for your platform:

* Codex local marketplace
* Claude Code plugin
* Gemini Agent Skill
* Source checkout / CLI

However you install it, the entry point after installation is the same:

```bash
memory-custodian init \
  --project-root /path/to/project \
  --agent all
```

The initializer creates a scaffold rather than pretending to understand the repository automatically. Review the generated files, then curate `brief.md`, decisions, constraints, and rejected approaches from authoritative project information.

For the current per-platform installation steps, see the [README](https://github.com/waittim/MemoryCustodian). Once initialized, the project itself becomes the source of durable agent context.

---

## Try the NightNotes Example

The MemoryCustodian repository ships with the demo under `examples/nightnotes-video-demo`.

Validate the NightNotes memory:

```bash
memory-custodian check \
  --project-root examples/nightnotes-video-demo
```

Read the planning context:

```bash
memory-custodian read \
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

## Key Takeaways

* Project memory should preserve decisions and constraints, not entire conversations.
* Durable memory and active context are separate concerns.
* Markdown and Git keep agent memory portable, inspectable, and reviewable.
* Manifest-based routing keeps the context for each task intentionally small.

## Frequently Asked Questions

### Does MemoryCustodian work across coding agents?

Yes. Its durable memory is plain Markdown stored in the repository, so the same project knowledge can be used by Codex, Claude Code, Gemini CLI, and other agents that can read repository files.

### Why not put everything in one instruction file?

A single growing file makes every task pay the context cost of every stored decision. MemoryCustodian keeps platform instructions thin and routes task-specific memory through a manifest.

### Does MemoryCustodian require a hosted database or embeddings?

No. Routine operation is local and repo-native. The design favors transparent files and deterministic structure over a proprietary storage or retrieval layer.

<p id="demo">
<iframe width="700" height="393" src="https://www.youtube-nocookie.com/embed/mYKzzATlOPw" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</p>

* [Install MemoryCustodian](https://github.com/waittim/MemoryCustodian)
* [Read the technical design](/2026/07/20/memory-custodian-tech-design/)
* [Read the memory governance design](/2026/07/21/memory-custodian-safe/)

**Durable memory. Minimal context.**
