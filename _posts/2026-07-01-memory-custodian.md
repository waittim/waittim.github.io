---
layout:     post  
title:      MemoryCustodian Skill - Project Memory for Coding Agents  
subtitle:   Durable memory. Minimal context.  
date:       2026-07-01  
author:     Zekun  
header-img: img/headers/2026-07-01-memory-custodian.png  
catalog: true  
tags:
    - Coding Agent
    - AI
    - Developer Tools
    - CLI
    - LLM
    - Skill
    - Project
    - Memory
---


Coding agents are becoming better at writing code, tracing bugs, and navigating unfamiliar repositories.

But one problem still appears in almost every long-running project:

**A new session starts with no reliable memory of why the project looks the way it does.**

The agent may understand the code in front of it, yet still miss the decisions behind that code. It may not know that a particular architecture was chosen deliberately, that a seemingly obvious alternative already failed, or that a hard constraint cannot be relaxed.

The result is familiar:

* You explain the same project context again
* The agent proposes an approach that was already rejected
* Important constraints are copied into larger and larger instruction files
* Every task begins by loading information that may not be relevant
* Different agents develop different understandings of the same repository

At first, the natural response is to keep adding more context to `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or the prompt itself.

That works until the instruction file becomes a memory dump.

The project now has “memory,” but every task pays the full context cost.

**[MemoryCustodian](https://github.com/waittim/MemoryCustodian) takes a different approach: project memory can grow, while the context loaded for each task stays small.**

> Updated for MemoryCustodian v0.8.1.

---

## Before and After

Consider a project that previously rejected a server-side vector database in favor of a local, plain-text architecture.

Without durable project memory, a new session may look like this:

```text
A new coding-agent session starts.

The agent reads the repository.
It notices that the project needs persistent memory.
It proposes adding a vector database.

You explain that this was already considered and rejected.
You restate the offline requirement.
You restate the need for human-reviewable storage.
The same discussion happens again next week.
```

With MemoryCustodian, the project records that decision once.

For a planning task, the agent loads:

```text
manifest.md
brief.md
decisions.md
constraints.md
do-not-use.md
```

The rejected approach is visible. The constraint is visible. The current direction is visible.

For an unrelated documentation task, the agent may load a much smaller set.

The memory remains in the repository, but the context changes with the task.

That is the central idea:

> **Durable memory should not mean permanent full-context loading.**

---

## What MemoryCustodian Is

MemoryCustodian is a local-first, repo-native project memory protocol, skill, and CLI for coding agents.

It stores durable memory as plain Markdown under:

```text
docs/memory/
```

The memory belongs to the project rather than to one conversation or one AI platform.

That makes it usable across:

* Separate sessions
* Different coding agents
* Different developer machines
* Individual and team workflows
* Human review and version control

MemoryCustodian is not intended to archive every conversation. It does not try to remember everything an agent has ever seen.

Instead, it preserves the small amount of project knowledge that should continue to influence future work:

* What the project is trying to become
* Which decisions are currently active
* Which constraints must remain true
* Which approaches should not be reintroduced
* Which details matter only to a particular subsystem or task

The goal is not maximum memory.

The goal is **useful continuity with controlled context cost**.

---

## The Memory Structure

A default MemoryCustodian project begins with six core files:

```text
docs/memory/
  manifest.md
  brief.md
  decisions.md
  constraints.md
  do-not-use.md
  inbox.md
```

Together, they separate different kinds of project knowledge that are often mixed together in one oversized instruction file.

`brief.md` contains the shortest useful summary of the project's current purpose, direction, and system context.

`decisions.md` records confirmed architecture and implementation choices.

`constraints.md` contains hard requirements, invariants, and compatibility boundaries.

`do-not-use.md` records rejected approaches, known failure paths, and tombstones that should not quietly return in later sessions.

`inbox.md` temporarily holds memory candidates that still need review or compaction.

The most important file is `manifest.md`.

The manifest tells an agent which memory files are relevant for a particular task.

A planning task may need decisions and rejected approaches. An implementation task may need constraints and area-specific context. A user-facing writing task may need output preferences but not infrastructure history.

Instead of treating every memory file as permanently active context, the manifest turns memory loading into a routing problem.

---

## Design Principle 1: Memory Can Grow; Context Must Stay Small

Most approaches to persistent agent context eventually face the same tradeoff:

* Keep more memory and increase context cost
* Keep context small and lose continuity

MemoryCustodian separates those two concerns.

The memory store may grow over time. Old decisions, subsystem notes, preferences, and archived material can remain available in the repository.

But the active context pack for one task should include only the files that are relevant to that task and scope.

This is why the manifest matters.

It is not merely an index for humans. It is the authoritative runtime routing source for the CLI. Missing, malformed, ambiguous, or unsafe routes fail clearly instead of silently falling back to a hidden default.

This gives the project a deterministic answer to a critical question:

> What should the agent remember for this task?

Selective loading also keeps platform instruction files thin. `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` only need to point the agent toward the memory protocol. They do not need to contain the entire history of the project.

---

## Design Principle 2: Project Memory Should Be Reviewable Like Code

A project decision can change the direction of months of work.

That kind of memory should not live only in an opaque platform store.

MemoryCustodian uses Markdown because project memory should be:

* Readable without special tools
* Editable by humans
* Diffable in Git
* Reviewable in pull requests
* Reversible
* Portable across agent platforms
* Available offline

This creates an important governance property: memory changes can be reviewed with the same discipline as code changes.

A team can see when a constraint was added. A developer can challenge an outdated decision. A rejected approach can be removed deliberately rather than disappearing inside an inaccessible retrieval system.

The format is intentionally ordinary.

There is no requirement for embeddings, vector databases, cloud-hosted memory, or a background service. Those technologies may be useful for other problems, but they are not necessary for a small, durable set of project decisions and constraints.

The simplicity is part of the product.

---

## Design Principle 3: Memory Operations Must Preserve Meaning

Storing Markdown is easy.

Maintaining trustworthy memory is harder.

A memory system becomes dangerous when it silently damages meaning while appearing to work correctly.

For example, a raw token limit might cut a decision after its title but before its reason. A constraint could lose a negation. A deletion command could remove one matching line while leaving the rest of the entry intact.

MemoryCustodian avoids these operations at arbitrary text boundaries.

Context budgets are applied to complete semantic entries. If an entry does not fit, MemoryCustodian may omit it and report the omission, but it does not cut a decision, constraint, tombstone, or top-level bullet in half.

Forgetting follows the same principle.

The CLI removes complete H2 entries or top-level bullets rather than isolated matching lines. Forgetting is preview-first, so the user or agent can inspect the complete plan before applying it.

Short topics and plans that match multiple entries require explicit broad-match confirmation.

If matching content appears in a plain body or preamble, MemoryCustodian does not delete the whole section automatically. It reports:

```text
Manual rewrite required
```

The apply operation is blocked until the content is rewritten semantically.

This is slower than blind string replacement.

It is also much safer.

---

## Forgetting Is Part of Memory Governance

Persistent memory is not trustworthy unless it can also forget.

MemoryCustodian supports three levels of forgetting:

* `soft` removes matching active entries but keeps a topic-bearing tombstone so the rejected idea is not reintroduced
* `hard` removes matching active entries and replaces prior topic-bearing soft tombstones with a generic redacted guard
* `purge` searches active and archived memory and removes matching topic-bearing tombstones

The commands are preview-first:

```bash
# Preview
memory-custodian forget "old deployment note" --mode soft

# Apply after review
memory-custodian forget "old deployment note" --mode soft --apply
```

A short or broad topic requires additional confirmation:

```bash
memory-custodian forget "Go" --mode soft
memory-custodian forget "Go" --mode soft --apply --allow-broad-match
```

Hard and purge operations avoid preserving the original topic in new records.

They do not rewrite Git history, backups, caches, or external copies. MemoryCustodian is explicit about that boundary rather than presenting deletion as stronger than it is.

This approach treats forgetting as a governed project operation, not as an unreviewed text mutation.

---

## The Agent Workflow

Once installed, MemoryCustodian is designed to become part of the agent's normal project workflow.

Before substantial work, an agent should:

1. Read `docs/memory/manifest.md`
2. Read `docs/memory/brief.md`
3. Identify the task type and relevant project scope
4. Load only the required decisions, constraints, tombstones, areas, rules, or preferences
5. Respect active rejected paths
6. Update memory only after meaningful decisions, repeated corrections, or confirmed changes in direction

The user should not have to manually assemble context for every session.

The protocol gives the agent a repeatable way to recover the project's durable state.

At the same time, it avoids turning every conversation into a memory-writing event. Temporary thoughts, speculative ideas, and low-confidence observations should not automatically become durable project knowledge.

Memory is curated, not accumulated blindly.

---

## A 60-Second Start

Initialize MemoryCustodian inside a project:

```bash
memory-custodian init --project-root /path/to/project --agent all
```

Review the generated scaffold:

```bash
memory-custodian status
memory-custodian check
```

Preview the memory that would be loaded for planning:

```bash
memory-custodian read --task planning
```

Record a confirmed decision:

```bash
memory-custodian add \
  "Use manifest-first loading." \
  --type decision \
  --reason "Keep task context small as project memory grows."
```

The generated `brief.md` should then be curated from authoritative project files before it is treated as trusted memory.

From that point forward, the project has a durable memory structure that future sessions and agents can use.

---

## What Changed in v0.8.1

MemoryCustodian v0.8 and v0.8.1 focused on correctness rather than adding more memory types.

The release made four changes that matter most to users:

### Safer forgetting

Forget operations are preview-first, remove complete semantic entries, protect broad matches, and handle prior tombstones correctly during hard and purge operations.

### Complete-entry context packing

Memory files are packed at semantic boundaries instead of being mechanically truncated.

### Authoritative manifest routing

The manifest determines runtime task routing, and invalid routes fail visibly.

### Idempotent platform bootstraps

Generated MemoryCustodian sections in Agent instruction files are managed blocks, so repeated initialization does not create duplicate instructions.

Behind these user-facing changes, the project also added atomic managed-file writes and automated contract checks.

The underlying design remains the same: plain Markdown, local execution, explicit operations, and no hidden retrieval infrastructure.

---

## Who Is It For?

MemoryCustodian is useful when:

* A project spans many coding-agent sessions
* Agents repeatedly forget previous decisions
* The same repository is used with multiple agent platforms
* Instruction files are becoming too large
* Important constraints must survive across sessions
* Rejected approaches keep returning
* A team wants memory changes to be reviewable
* Local, transparent, version-controlled memory matters

It is especially useful for long-running projects where continuity matters more than remembering every detail.

MemoryCustodian is not a general-purpose document search engine or a replacement for source documentation.

It is a governance layer for the small set of project knowledge that should reliably shape future agent behavior.

---

## Memory Should Make the Next Session Better

Coding agents do not need an unlimited archive of everything that happened before.

They need a trustworthy answer to a smaller set of questions:

* What is this project trying to do?
* What decisions are already settled?
* What constraints must not be broken?
* What approaches should not be proposed again?
* What context is relevant to this task?

MemoryCustodian keeps those answers inside the repository, where people and agents can inspect them.

Its design is intentionally restrained:

* Store memory as plain Markdown
* Keep platform files thin
* Route context through a manifest
* Load only what the task needs
* Preserve complete semantic entries
* Make updates and forgetting deliberate
* Keep the entire system local and reviewable

MemoryCustodian is not a smarter black box.

It is a disciplined way to help coding agents carry a project forward instead of repeatedly relearning it.
