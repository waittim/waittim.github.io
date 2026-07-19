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

The agent may understand the code in front of it, yet still miss the decisions behind that code. It may not know that a particular architecture was chosen deliberately, that an obvious alternative already failed, or that a hard constraint cannot be relaxed.

The result is familiar:

- You explain the same project context again
- The agent proposes an approach that was already rejected
- Important constraints are copied into larger instruction files
- Every task loads information that may not be relevant
- Different agents develop different understandings of the same repository

At first, the natural response is to keep adding more context to `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or the prompt itself.

That works until the instruction file becomes a memory dump.

The project now has “memory,” but every task pays the full context cost.

**[MemoryCustodian](https://github.com/waittim/MemoryCustodian) takes a different approach: project memory can grow, while the context loaded for each task stays small.**

> Updated for MemoryCustodian v0.9.1.

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

With MemoryCustodian, the project records the decision once.

For a planning task, the agent may load:

```text
manifest.md
brief.md
decisions.md
constraints.md
do-not-use.md
```

The rejected approach is visible. The constraint is visible. The current direction is visible.

For an unrelated documentation task, the agent may load a much smaller set.

The memory remains in the repository, but the active context changes with the task.

That is the central idea:

> **Durable memory should not mean permanent full-context loading.**

---



## What MemoryCustodian Is

MemoryCustodian is a local-first, repo-native project memory protocol, agent skill, and CLI for coding agents.

It stores durable memory as plain Markdown under:

```text
docs/memory/
```

The memory belongs to the project rather than to one conversation, one developer machine, or one AI platform.

That makes it usable across:

- Separate sessions
- Different coding agents
- Different developer machines
- Individual and team workflows
- Human review and version control

MemoryCustodian is not intended to archive every conversation.

It does not try to remember everything an agent has ever seen.

Instead, it preserves the small amount of project knowledge that should continue to influence future work:

- What the project is trying to become
- Which decisions are currently active
- Which constraints must remain true
- Which approaches should not be reintroduced
- Which knowledge applies only to a subsystem or workflow
- Which new observations still require semantic review

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

Together, they separate kinds of project knowledge that are often mixed into one oversized instruction file.

`brief.md` contains the shortest useful summary of the project's current purpose, direction, and system context.

`decisions.md` records confirmed architecture, product, and implementation choices.

`constraints.md` contains hard requirements, invariants, and compatibility boundaries.

`do-not-use.md` records rejected approaches, known failure paths, and tombstones that should not quietly return in later sessions.

`inbox.md` temporarily holds memory candidates that still require semantic review.

The most important file is `manifest.md`.

The manifest tells the agent which memory files apply to each supported task category.

A planning task may need decisions and rejected approaches. An implementation task may need constraints and area-specific knowledge. A user-facing writing task may need output preferences but not infrastructure history.

Instead of treating every memory file as permanently active context, the manifest turns memory loading into an explicit routing problem.

---



## Design Principle 1: Memory Can Grow; Context Must Stay Small

Most approaches to persistent agent context eventually face the same tradeoff:

- Keep more memory and increase context cost
- Keep context small and lose continuity

MemoryCustodian separates those two concerns.

The repository memory may grow over time. Decisions, subsystem notes, preferences, rejected paths, and archived material can remain available without being loaded into every task.

The active context pack for one task should contain only the files relevant to that task and project scope.

This is why the manifest matters.

It is not merely an index for humans. For initialized projects, it is the authoritative routing source used by the skill.

The skill first selects a supported task category, then resolves its memory files exclusively through the current project manifest.

Missing, malformed, ambiguous, or unsafe routes fail clearly instead of silently falling back to guessed files or hidden defaults.

This gives the project an explicit answer to a critical question:

> What should the agent remember for this task?

Selective loading also keeps platform instruction files thin.

`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` only need to point the agent toward the shared memory protocol. They do not need to contain the entire history of the project.

---



## Design Principle 2: Project Memory Should Be Reviewable Like Code

A project decision can influence months of work.

That kind of memory should not live only in an opaque platform store.

MemoryCustodian uses Markdown because project memory should be:

- Readable without special tools
- Editable by humans
- Diffable in Git
- Reviewable in pull requests
- Reversible
- Portable across agent platforms
- Available offline

This creates an important governance property: memory changes can be reviewed with the same discipline as code changes.

A team can see when a constraint was added. A developer can challenge an outdated decision. A rejected approach can be removed deliberately rather than disappearing inside an inaccessible retrieval system.

The format is intentionally ordinary.

There is no requirement for embeddings, vector databases, cloud-hosted memory, or a background service.

Those technologies may be useful for document search or large-scale retrieval, but they are not required for a small, durable set of project decisions and constraints.

The simplicity is part of the product.

---



## Design Principle 3: Agents Decide Meaning; the CLI Enforces Structure

One of the most important changes in MemoryCustodian v0.9 was clarifying the boundary between semantic intelligence and deterministic tooling.

Earlier versions allowed limited keyword-based classification of inbox candidates.

That looked convenient, but it gave a deterministic script responsibility for judgments it could not reliably make.

A phrase appearing in a candidate does not necessarily determine whether that candidate is:

- A project-wide decision
- A subsystem-specific decision
- A hard constraint
- A temporary observation
- A duplicate
- A contradiction
- Too uncertain to preserve

Those decisions require context and semantic reasoning.

MemoryCustodian now makes that boundary explicit:

- The agent or user decides meaning
- The CLI validates and applies exact operations

The agent or user is responsible for candidate scope, type, confidence, overlap, and whether the candidate should be promoted into durable memory.

The CLI remains responsible for tasks it can perform predictably:

- Validating file paths and structures
- Resolving routes through the manifest
- Checking context budgets
- Detecting exact duplicates
- Detecting exact tombstone matches
- Previewing mutation plans
- Applying bounded file changes

Compaction no longer pretends to understand the semantic meaning of inbox candidates through keyword rules.

It reports candidates for review and automatically applies only mechanically verifiable cleanup.

This division is more conservative, but also more trustworthy.

> **The agent understands meaning. The CLI enforces the resulting operation safely.**

---



## Design Principle 4: Memory Operations Must Preserve Meaning

Storing Markdown is easy.

Maintaining trustworthy Markdown memory is harder.

A memory system becomes dangerous when it silently damages meaning while appearing to work correctly.

For example:

- A raw token limit may include the title of a decision but omit its reason
- A constraint may lose a continuation paragraph
- A top-level bullet may be separated from its nested details
- A fenced example may be split from the entry it explains
- A deletion command may remove one matching line while leaving a misleading fragment

MemoryCustodian avoids making changes at arbitrary text boundaries.

### Complete-entry context packing

Context budgets are applied to complete semantic entries.

If an entry does not fit, MemoryCustodian may omit it and report the omission, but it does not cut a decision, constraint, tombstone, or top-level bullet in half.

### Structure-preserving compaction

Version 0.9.1 treats complete column-zero top-level bullets as atomic units.

A unit includes its continuation paragraphs, nested bullets, indentation-sensitive content, and fenced examples.

The same structural rule is used when counting inbox candidates and displaying them in preview output.

### Preview-first mutations

Forgetting, compaction, migration, and full replacement are preview-first operations.

The user or agent can inspect the proposed mutation before it changes the repository.

This is slower than blind string replacement.

It is also much safer.

---



## Forgetting Is Part of Memory Governance

Persistent memory is not trustworthy unless it can also forget.

MemoryCustodian supports three levels of forgetting:

- `soft` removes matching active entries but keeps a topic-bearing tombstone so the rejected idea is not reintroduced
- `hard` removes matching active entries and replaces prior topic-bearing soft tombstones with a generic redacted guard
- `purge` searches active and archived managed memory and removes matching topic-bearing tombstones

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

They also handle prior soft tombstones. A later hard forget replaces topic-bearing tombstones with a generic redacted guard, while purge removes them completely.

If matching content appears inside a plain body paragraph or document preamble, MemoryCustodian does not delete the surrounding section automatically.

It reports:

```text
Manual rewrite required
```

The apply operation stops before the first write until the ambiguous text is rewritten semantically.

MemoryCustodian does not claim to erase Git history, backups, caches, or external copies. It is explicit about the boundary of managed memory rather than presenting deletion as stronger than it is.

This approach treats forgetting as a governed project operation, not as an unreviewed text mutation.

---



## Safe Initialization and Repair

Initialization becomes more complicated once a project contains curated memory.

A command that is safe for an empty directory may be dangerous when decisions and constraints have already been written by humans.

MemoryCustodian therefore separates three different operations.

### Initialize a new project

```bash
memory-custodian init \
  --project-root /path/to/project \
  --agent all
```



### Repair an existing setup

```bash
memory-custodian init \
  --project-root /path/to/project \
  --repair
```

`init --repair` creates missing components and refreshes recognized generated metadata or managed bootstrap blocks.

It does not overwrite curated project memory.

### Replace existing generated content

Full replacement is separate and preview-first:

```bash
# Preview
memory-custodian init \
  --project-root /path/to/project \
  --replace-existing

# Apply after review
memory-custodian init \
  --project-root /path/to/project \
  --replace-existing \
  --apply
```

The older memory-file `--force` behavior is intentionally not supported.

An existing memory directory without a valid `manifest.md` is treated as incomplete or corrupted instead of having routes inferred from filenames.

This prevents a repair command from silently creating a configuration that appears valid but does not reflect the project's intended routing.

---



## Protocol Compatibility Should Fail Safely

A project may contain protocol metadata created by a newer version of MemoryCustodian.

An older installed CLI should not silently rewrite that metadata or pretend it understands a newer protocol.

Version 0.9.1 refuses `init --repair` and `migrate` when the project's protocol metadata:

- Is newer than the installed CLI supports
- Cannot be parsed reliably

This avoids false compatibility through metadata downgrade.

The current MemoryCustodian Protocol remains at version `0.5` because the v0.9 releases strengthen enforcement without changing the manifest schema.

The version number does not need to change every time implementation safety improves.

---



## Multi-File Mutations Need a Complete Plan

Commands such as initialization, migration, forgetting, and compaction may affect several files.

Writing files one at a time without validating the full operation can leave memory in a partially updated state.

MemoryCustodian now precomputes multi-file mutation plans.

Before the first write, it validates the planned targets and checks whether the operation can proceed safely.

Where appropriate, archive creation happens before destructive mutation.

If an unexpected filesystem failure still causes only part of a plan to complete, the CLI reports the completed and incomplete portions explicitly.

Expected input and filesystem errors are reported cleanly, while unexpected programming failures remain visible for debugging.

The goal is not to claim that failure is impossible.

The goal is to make failure bounded, visible, and recoverable.

---



## The Agent Workflow

Once installed, MemoryCustodian is designed to become part of the agent's normal project workflow.

Before substantial work, an agent should:

1. Read `docs/memory/manifest.md`
2. Read `docs/memory/brief.md`
3. Select a supported task category
4. Resolve applicable memory files through the manifest
5. Load only the required decisions, constraints, tombstones, areas, rules, or preferences
6. Respect active rejected paths
7. Propose or write memory updates only after meaningful decisions or repeated corrections

The user should not need to manually assemble project context for every session.

The protocol gives the agent a repeatable way to recover the project's durable state.

At the same time, it avoids turning every conversation into a memory-writing event.

Temporary thoughts, speculative ideas, and low-confidence observations should not automatically become durable project knowledge.

Memory is curated, not accumulated blindly.

---



## A 60-Second Start

Install or check out MemoryCustodian, then initialize it inside a project:

```bash
memory-custodian init \
  --project-root /path/to/project \
  --agent all
```

Review the generated scaffold:

```bash
memory-custodian status \
  --project-root /path/to/project

memory-custodian check \
  --project-root /path/to/project
```

Preview the memory that would be loaded for planning:

```bash
memory-custodian read \
  --project-root /path/to/project \
  --task planning
```

Record a confirmed decision:

```bash
memory-custodian add \
  "Use manifest-first loading." \
  --type decision \
  --reason "Keep task context small as project memory grows." \
  --project-root /path/to/project
```

The generated `brief.md` should be curated from authoritative project files before it is treated as trusted memory.

From that point forward, the project has a durable memory structure that future sessions and agents can use.

---



## What Changed in v0.9.1

Versions 0.8.0 through 0.9.1 focused on making MemoryCustodian trustworthy under real repository conditions.

The most important changes are:

### Clear semantic boundary

Keyword-based inbox classification was removed.

The agent or user now makes semantic decisions, while the CLI applies only exact, verifiable operations.

### Safer initialization

Conservative `init --repair` replaces destructive memory-file force behavior.

Full replacement is a separate preview-first operation.

### Multi-file mutation planning

Commands compute and validate their mutation plans before the first write and report partial completion explicitly when necessary.

### Privacy-safe forgetting

Soft, hard, and purge transitions no longer leave sensitive topic-bearing tombstones in managed memory.

### Complete-entry context packing

Memory is packed at semantic boundaries rather than being truncated mechanically.

### Structure-preserving compaction

Top-level bullet entries remain attached to their continuation paragraphs, nested content, and fenced examples.

### Protocol downgrade protection

Repair and migration refuse project metadata that is newer than the installed CLI or cannot be parsed.

### Manifest-authoritative routing

The skill selects a supported task category and resolves the applicable files exclusively through the project's current manifest.

### Cross-platform assurance

The project includes automated checks across supported Python versions and a Windows Python 3.13 CLI smoke test.

The underlying product direction remains the same:

- Plain Markdown
- Local execution
- Explicit operations
- Thin platform bootstraps
- No required retrieval infrastructure

---



## Who Is It For?

MemoryCustodian is useful when:

- A project spans many coding-agent sessions
- Agents repeatedly forget previous decisions
- The same repository is used with multiple agent platforms
- Instruction files are becoming too large
- Important constraints must survive across sessions
- Rejected approaches keep returning
- A team wants memory changes to be reviewable
- Local, transparent, version-controlled memory matters

It is especially useful for long-running projects where continuity matters more than remembering every detail.

MemoryCustodian is not a general-purpose document search engine.

It is not a replacement for source documentation.

It is not a system for archiving every conversation.

It is a governance layer for the small set of project knowledge that should reliably shape future agent behavior.

---



## Memory Should Make the Next Session Better

Coding agents do not need an unlimited archive of everything that happened before.

They need trustworthy answers to a smaller set of questions:

- What is this project trying to do?
- What decisions are already settled?
- What constraints must not be broken?
- What approaches should not be proposed again?
- What context is relevant to this task?
- Which new observations deserve to become durable memory?

MemoryCustodian keeps those answers inside the repository, where people and agents can inspect them.

Its design is intentionally restrained:

- Store memory as plain Markdown
- Keep platform files thin
- Route context through a manifest
- Load only what the task needs
- Let agents decide meaning
- Let deterministic tooling enforce structure
- Preserve complete semantic entries
- Make updates and forgetting deliberate
- Keep the system local and reviewable

MemoryCustodian is not a smarter black box.

It is a disciplined way to help coding agents carry a project forward instead of repeatedly relearning it.