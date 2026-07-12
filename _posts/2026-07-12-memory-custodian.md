---

layout:     post  
title:      MemoryCustodian Skill: Project Memory for Coding Agents  
subtitle:   Durable memory. Minimal context.  
date:       2026-07-12  
author:     Zekun  
header-img: img/headers/2026-07-12-memory-custodian.png  
catalog: true  
tags:  
    - Coding Agent  
    - AI  
    - Developer Tools  
    - CLI  
    - LLM
    - Skill
- Project

---

When working with coding agents such as Codex, Claude Code, Gemini CLI, or similar tools, one problem appears again and again:

**Every new session starts as if the agent has never seen the project before.**

It does not know why a previous architecture was chosen. It does not know which approaches were already rejected. It does not know the project's constraints, preferred workflows, or current direction. As a result, you end up repeating the same context, correcting the same mistakes, and pasting more and more instructions into prompts or platform files.

That works for a while, but it does not scale.

Over time, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and other instruction files become bloated. They mix durable project knowledge with temporary task guidance. They are hard to review, hard to keep current, and easy for agents to overload into context.

**MemoryCustodian is designed to solve this problem by giving coding agents durable, repo-native project memory.**

---



## The Problem: Agents Need Memory, but Context Must Stay Small

Most coding agents are good at working within a session. The harder problem is continuity across sessions.

A real project contains many pieces of knowledge that should survive beyond a single chat:

- Current project direction
- Architecture decisions
- Hard constraints
- Rejected approaches
- Known failure paths
- User or team preferences
- Task-specific rules
- Area-specific context for large repositories

Without a dedicated memory system, this knowledge usually ends up in one of three places:

1. Hidden in old conversations
2. Repeated manually by the user
3. Dumped into always-loaded instruction files

None of these is ideal.

Old conversations are not reliable project memory. Manual repetition wastes time. Always-loaded instruction files make every task heavier, even when most of the information is irrelevant.

MemoryCustodian takes a different approach:

> Project memory should live in the repository, be readable by humans, and be loaded by agents only when relevant.

---



## What MemoryCustodian Is

MemoryCustodian is a local-first, plain-text memory protocol, skill, and CLI for coding agents.

It stores durable project memory as Markdown files under:

```text
docs/memory/
```

This makes memory:

- Easy to read
- Easy to edit
- Easy to review in pull requests
- Easy to diff
- Easy to commit and roll back
- Portable across agents and platforms

It is not a chat history archive. It is not a cloud memory service. It is not a vector database or RAG system.

It is project memory.

The goal is simple:

> Durable memory. Minimal context.

---



## How It Works

By default, MemoryCustodian initializes a small core memory structure:

```text
docs/memory/
  manifest.md
  brief.md
  decisions.md
  constraints.md
  do-not-use.md
  inbox.md
```

Each file has a specific role.

`brief.md` is the short current summary of the project. It is the default file agents read before substantial work.

`decisions.md` records confirmed project and architecture decisions.

`constraints.md` stores hard requirements and limits.

`do-not-use.md` captures rejected approaches, failed paths, and tombstones so agents do not keep reintroducing ideas that have already been ruled out.

`inbox.md` is a temporary holding area for memory candidates that need later review or compaction.

The most important file is `manifest.md`.

The manifest acts as the routing layer. It tells the agent which memory files are relevant for which type of task. Instead of loading everything, the agent first reads the manifest, then reads `brief.md`, then loads only the task-specific files needed for the current work.

For example:

- Planning or architecture tasks may load `decisions.md`, `constraints.md`, and `do-not-use.md`
- Implementation or debugging tasks may load `constraints.md`, `do-not-use.md`, and relevant preferences
- User-facing output tasks may load output rules and preferences
- Memory maintenance tasks may load `inbox.md` or `changelog.md`
- Archived material stays out of context unless explicitly requested

This is the core design principle behind MemoryCustodian:

> Memory can grow; context must stay small.

---



## Why Plain Markdown?

MemoryCustodian intentionally avoids unnecessary infrastructure.

It does not require:

- RAG
- Embeddings
- Vector databases
- Cloud-hosted memory
- Opaque platform-specific stores
- Chat log archiving
- A background daemon
- Automatic full-context loading

Instead, it uses plain Markdown files and a deterministic CLI.

That makes it especially suitable for coding workflows. Project memory stays close to the code. Humans can inspect it. Teams can review changes. Agents can use it without depending on a hidden retrieval system.

This also makes MemoryCustodian portable. The same memory directory can be used by different coding agents, different platforms, and different sessions.

---



## Thin Platform Files, Durable Project Memory

MemoryCustodian separates platform entry points from durable memory.

Files like `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` should stay small. Their job is only to tell the agent where project memory lives and how to load it.

They should not become giant memory dumps.

The durable knowledge belongs in `docs/memory/`.

This separation matters because each agent platform has its own conventions, but the project's memory should not be locked to one of them. A project may use Codex today, Claude Code tomorrow, and another agent later. The memory should remain stable across all of them.

MemoryCustodian provides adapters and snippets for common agent environments while keeping the core protocol platform-neutral.

---



## The Agent Workflow

Once MemoryCustodian is installed and initialized, the normal workflow is agent-operated.

Before substantial planning, implementation, debugging, or review, a capable agent should:

1. Read `docs/memory/manifest.md`
2. Read `docs/memory/brief.md`
3. Identify the current task type
4. Load only the files allowed by the manifest and relevant to the task
5. Respect `do-not-use.md` before proposing plans or implementations
6. Update or propose memory changes after meaningful decisions, repeated corrections, or rejected approaches

The user should not need to manually run a memory read command before every task. The CLI exists for setup, inspection, maintenance, and deterministic operations.

---



## The Easiest Way to Use It

The easiest way to start is to ask your coding agent:

```text
Install the MemoryCustodian skill from https://github.com/waittim/MemoryCustodian, then initialize it.
```

After installation, initialize MemoryCustodian once inside each target project:

```bash
memory-custodian init --project-root /path/to/project --agent all
```

The `--agent all` option creates thin bootstrap entries for supported agents such as Codex, Claude Code, and Gemini-style agents.

You can also target a specific agent:

```bash
memory-custodian init --project-root /path/to/project --agent codex
memory-custodian init --project-root /path/to/project --agent claude
memory-custodian init --project-root /path/to/project --agent gemini
```

After initialization, the project will contain its `docs/memory/` directory and the relevant lightweight platform entry files.

From that point on, the agent should use the manifest to load memory before important work.

---



## Useful CLI Commands

Check the current memory state:

```bash
memory-custodian status
memory-custodian check
```

Preview what context would be loaded for a task:

```bash
memory-custodian read --task planning
memory-custodian read --task implementation
memory-custodian read --task artifact
```

Add a durable decision:

```bash
memory-custodian add "We chose manifest-first loading." --type decision
```

Forget an outdated or unwanted memory topic:

```bash
memory-custodian forget "old deployment note" --mode soft
```

Compact accumulated memory candidates:

```bash
memory-custodian compact
memory-custodian compact --apply
```

The CLI is not meant to replace the agent workflow. It exists to make memory operations explicit, inspectable, and repeatable.

---



## Who Is This For?

MemoryCustodian is useful if:

- You use coding agents across many sessions
- Your agents keep forgetting project decisions
- You use multiple agent platforms
- Your `AGENTS.md` or `CLAUDE.md` is becoming too large
- Your project has important constraints agents must remember
- Your team wants to review memory changes like code
- You want project memory to be local, transparent, and version-controlled

It is especially helpful for long-running projects where the cost of re-explaining context keeps growing.

MemoryCustodian is not trying to be a general knowledge base, a document search engine, or a chat archive. It is a memory governance layer for agent-assisted software development.

---



## Summary

MemoryCustodian is built around a simple observation:

**Coding agents need durable project memory, but they should not load the entire project history into every task.**

Its solution is intentionally simple:

- Store memory as Markdown in the repository
- Keep platform instruction files thin
- Use a manifest to route task-specific context
- Load only what is relevant
- Make updates deliberate
- Keep memory inspectable, diffable, and portable

This gives coding agents enough continuity to work effectively without turning every session into a giant prompt.

MemoryCustodian is not a smarter black box. It is a more disciplined way to manage what agents should remember.

For teams and developers who rely on coding agents every day, that discipline can make the difference between an agent that constantly relearns the project and one that actually carries the project forward.