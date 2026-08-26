---
layout: post
title: "Why Project Memory Should Be Plain Text and Repo-Native"
subtitle: "Durable coding-agent memory should live with the code, survive the tool, and load only when relevant."
date: 2026-07-20
updated: 2026-07-23
author: Zekun Wang
description: "Why durable coding-agent memory should use repo-native Markdown, Git review, manifest routing, and semantic entry boundaries."
image: /img/headers/post-bg-computer-storage.jpeg
series: MemoryCustodian Design Series
series_nav_title: Technical Design
series_order: 2
header-img: img/headers/post-bg-computer-storage.jpeg
catalog: true
tags:
    - Agent
    - Agent Memory
    - Developer Tools
    - Software Architecture
    - Local-First
    - Markdown
    - Git
    - AI
    - Project
---

## Why Use Plain Text for Project Memory?

Plain-text, repo-native memory remains readable without the original tool, travels with the code, participates in ordinary review, and works across agent platforms. A manifest can then activate only the memory relevant to a task instead of loading the repository’s full history.

*For developers designing durable context and memory protocols for coding agents. Implementation details in this article reflect MemoryCustodian v0.9.x.*

Code tells an agent what a system does.

It rarely tells the agent why the system must stay that way.

A repository may reveal that an application stores data in JSON. It may not reveal why JSON was chosen instead of SQLite. It may show that the application has no external dependencies, but not that offline operation is a product requirement. It may show that an earlier subsystem was removed, but not that the same approach was already tested twice, failed for specific reasons, and should not quietly return.

This missing layer is project memory: the decisions behind the code, the constraints that must remain true, the rejected approaches that should not be rediscovered as new ideas, and the context that matters to some tasks but not every task.

The difficult question is not merely how to store that information. It is how to preserve it without turning every future task into an exercise in loading the project’s entire history.

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) is built around a deliberately restrained answer:

> **Project memory should be plain text, stored inside the repository, routed explicitly, and interpreted semantically.**

This design rests on four ideas. Markdown provides durable and inspectable storage. Git turns memory into a governed project artifact. A manifest separates stored memory from active context. Language models interpret meaning while deterministic tools enforce structure.

The result is not an invisible intelligence layer. It is a memory system the project can own, inspect, review, and survive without.

---

## Code Shows What. Memory Preserves Why.

Coding agents can reconstruct a surprising amount from source code. They can inspect dependencies, trace execution paths, identify architectural patterns, and infer how components interact.

But inference is not the same as project knowledge.

From a local JSON storage implementation, an agent may infer that the data model is simple and that no relational database is installed. It cannot reliably infer that users must be able to inspect those files manually, that routine operation must work offline, that SQLite was already rejected for this session store, or the condition under which that choice should be reconsidered.

Without durable memory, each new conversation begins with partial evidence. An agent may propose an apparently reasonable change that violates an old requirement or repeats an already rejected experiment.

Conversation history is not a reliable solution. It may be tied to one user, one model provider, one interface, or one agent platform. Another developer may never see it. Another coding agent may not have access to it. It may also contain far more information than the project should preserve.

Private agent memory and durable project memory are therefore different things.

Private memory belongs to a user, session, provider, or application. Project memory should belong to the project.

That distinction matters because project knowledge may need to survive a new conversation, a different coding agent, a new developer machine, a teammate joining the repository, a branch or release cycle, or the departure of the person who originally made the decision.

A project-specific decision should remain attached to the project it governs.

---

## Why Project Memory Should Live in the Repository

Plain text is not exciting infrastructure.

That is one of its strengths.

Durable project knowledge should remain understandable even when the original tool is unavailable. Developers should not need a proprietary application, database client, embedding model, or hosted memory service merely to inspect the reasoning behind their own codebase.

Markdown provides several useful properties at once.

It is directly readable by humans. A developer can open `docs/memory/decisions.md` in an editor, terminal, pull request, or repository browser. The meaning of the stored information is visible without first querying a retrieval interface.

It is also naturally readable by coding agents. Headings, lists, fenced examples, links, and short structured entries are already familiar inputs for language models. The same memory can be interpreted by different agent environments without first being converted into a vendor-specific representation.

Markdown is editable through ordinary development workflows. A developer can correct an outdated constraint directly. An agent can propose a patch. A reviewer can narrow an overly broad decision, add missing reasoning, or reject a speculative entry before it becomes trusted memory.

It is portable across operating systems, editors, repository hosts, and agent platforms. More importantly, it degrades gracefully. Even if the MemoryCustodian CLI disappears, the information remains readable.

That provides a useful test for durable project knowledge:

> **Does the memory survive the tool that created it?**

With repo-native plain text, the answer can be yes.

Storing memory inside the repository also gives it a governance model that engineering teams already understand: Git.

A statement such as `Do not introduce SQLite for the current session store` may influence future implementation proposals as strongly as a configuration file. A constraint such as `Routine operation must work without network access` may eliminate an entire class of solutions.

These are not casual notes. They shape engineering behavior.

They should therefore be reviewable with similar discipline to code.

A pull request can show that a new architectural decision was added. Reviewers can ask whether the decision is actually settled, whether its scope is too broad, whether it contradicts an existing constraint, or whether temporary information is being made permanent.

Git also makes memory reversible. A decision can be reverted. A constraint can be narrowed when the product changes. A rejected approach can be deliberately reconsidered when the assumptions behind its rejection no longer hold.

History makes changes attributable. It records when an entry was introduced and how it evolved. That does not make every memory entry correct, but it makes the memory accountable.

Most importantly, repo-native memory gives teams and agents a shared authority. It avoids creating a separate private version of project history for every developer, model provider, or coding environment.

The repository becomes the interoperability layer.

---

## Why One Giant Instruction File Fails

Many projects already use files such as:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
```

These files are useful for bootstrap instructions and stable operating rules. They can tell an agent how to run tests, where important documentation lives, which commands are safe, and how project-specific workflows should begin.

They become less effective when they are also expected to contain the project’s entire accumulated memory.

Over time, a single instruction file may collect product direction, architecture history, formatting preferences, deployment rules, dependency restrictions, rejected experiments, subsystem-specific decisions, temporary workarounds, and user-facing language preferences.

The project now has persistent context, but every task loads all of it.

A documentation edit may receive database migration history. A frontend copy change may receive infrastructure tombstones. A localized storage task may inherit unrelated authentication decisions. The information is not necessarily useless; its relevance simply depends on the task.

A single large instruction file collapses two separate questions:

1. What does the project remember?
2. What does the current task need to know?

Those questions should not have the same answer.

MemoryCustodian separates stored memory from active context. The repository may preserve a growing body of durable knowledge while each task receives only a bounded, relevant subset.

> **Memory can grow; context must stay small.**

This distinction also prevents a common failure mode in agent systems: treating persistence as if it automatically implies relevance.

The correct goal is not maximum recall in every interaction.

It is predictable access to the smallest set of project knowledge needed for the current task.

---

## Manifest Routing: Memory Is Not Context

<img class="theme-surface" src="{{ "/img/posts/2026-07-20-memory-custodian-tech-design/gallery-how-it-works.png" | relative_url }}" alt="How MemoryCustodian works: a coding agent reads manifest.md and brief.md, identifies the task type, then loads only task-matched memory into focused context while optional files such as archive stay out by default" title="Manifest routing for task-matched memory" width="1270" height="760" loading="lazy" decoding="async">

Plain text alone does not solve the problem.

A single `memory.md` file can become the same kind of unstructured dump as an oversized instruction file. Durable memory needs visible organization and explicit activation rules.

A MemoryCustodian project may use a structure such as:

```text
docs/memory/
  manifest.md
  brief.md
  decisions.md
  constraints.md
  do-not-use.md
  preferences.md
  inbox.md
  areas/
    authentication.md
    storage.md
    deployment.md
```

Each file represents a different kind or scope of project knowledge.

`brief.md` contains the shortest useful explanation of the project’s current purpose, direction, and system shape. It is not a replacement for the README or full architecture documentation. It gives a new agent enough orientation to understand what kind of project it is working on.

`decisions.md` contains confirmed choices that should guide future work. A useful decision records not only the selected direction but also its reasoning and scope:

```markdown
## Use local JSON for session persistence

Persist session notes in human-readable JSON files.

Reasoning:
- Users must be able to inspect and edit stored notes manually.
- Routine use must remain portable across supported environments.
- The current data model does not require a relational database.

Scope:
- This applies to the current session store.
- Reconsider the decision if relational queries become a core requirement.
```

The reasoning and scope are part of the decision. Without them, a future agent may follow the conclusion mechanically or apply it more broadly than intended.

`constraints.md` records requirements and invariants that must remain true, such as privacy restrictions, offline-operation requirements, compatibility boundaries, dependency policies, file-format guarantees, or performance limits.

Constraints differ from decisions. A constraint defines a boundary. A decision records a selected direction within the available boundaries.

`do-not-use.md` records rejected approaches and active tombstones. Rejected ideas often look reasonable when rediscovered without historical context. A useful tombstone explains what was rejected, why it was rejected, which scope it applies to, and what conditions would justify reconsideration.

`inbox.md` contains candidate memory awaiting review. Not every observation deserves immediate promotion into trusted project knowledge. A candidate may be speculative, incomplete, duplicated, contradictory, too broad, too narrow, or missing reasoning.

The inbox creates a boundary between “possibly worth remembering” and “trusted enough to guide future work.”

The final piece is `manifest.md`, the routing authority.

Suppose an agent receives this task:

```text
Change how NightNotes stores user sessions.
```

The task is classified as `storage-implementation`. The manifest defines the route:

```markdown
## storage-implementation

Load:
- brief.md
- decisions.md
- constraints.md
- do-not-use.md
- areas/storage.md
```

The resulting flow is straightforward:

```text
Task
  ↓
Task category
  ↓
manifest.md
  ↓
Required memory files
  ↓
Bounded context pack
  ↓
Coding agent
```

The agent receives the project brief, global decisions and constraints, active tombstones, and storage-specific context. It does not automatically receive copywriting preferences, authentication history, unrelated deployment notes, or unreviewed inbox entries.

From the routed files, the agent may learn:

```text
Decision:
Use human-readable JSON for the current session store.

Constraint:
Routine operation must work without network access.

Tombstone:
Do not introduce SQLite unless the data model materially changes.

Storage-specific context:
Session files must remain manually recoverable.
```

The agent now has the reasons and boundaries relevant to storage work without loading the project’s entire accumulated history.

This creates a critical property:

> **Context selection is inspectable.**

The project can show exactly why a file was included. The route can be reviewed in Git. A developer can challenge the classification or change the policy. The system does not need to conceal context selection behind an opaque retrieval process.

Explicit routing is useful only if failures are also explicit.

If a task category is unsupported, the system should report it. If a route references a missing file, validation should fail. If the manifest is malformed, the project should not quietly infer policy from filenames.

Silent fallback creates a dangerous failure mode: the agent appears to have loaded project memory, some expected constraints are absent, and the task continues with incomplete context.

Incorrectly loaded memory can be more dangerous than obviously missing memory.

---

## Routing and Retrieval Solve Different Problems

Semantic retrieval is useful when searching large collections of documents.

It answers a question such as:

> What information might be relevant to this query?

Manifest routing answers a different question:

> What context is required for this supported task category?

That distinction matters because curated project memory usually has a different shape from a general document corpus.

The important knowledge is often small, high-impact, structurally distinct, and expected to apply predictably. A project may have ten confirmed architectural decisions, five active constraints, and several subsystem-specific notes. The main challenge is not discovering vaguely similar text. It is reliably applying the correct rules.

Similarity-based retrieval can create uncertain boundaries. A short but critical constraint may rank below a longer note. A rejected approach may not share vocabulary with the new proposal. A subsystem decision may be retrieved outside its intended scope. A semantically similar but non-authoritative observation may outrank the confirmed entry.

The problem becomes especially serious when retrieval is treated as policy. A low similarity score should not determine whether an offline requirement applies. A top-k cutoff should not decide whether an active architectural tombstone is visible.

Explicit routing does not make semantic search unnecessary in every system. It recognizes that search and policy are different abstractions.

> **Search discovers potentially relevant information. Routing declares required context.**

A large research archive may need semantic search. A cross-company knowledge platform may need indexing, permissions, and distributed retrieval. A project’s curated set of decisions and constraints may instead need deterministic activation.

MemoryCustodian therefore treats project memory less like a document corpus and more like configuration with meaning.

The configuration is visible, but its contents are semantic. That leads to another boundary: the system must distinguish deciding what information means from enforcing how it is stored and loaded.

---

## Meaning Belongs to the Agent. Structure Belongs to the CLI.

Consider this candidate memory:

```text
Consider encrypting exported notes with a user-provided passphrase.
```

It could be a confirmed product decision, a future feature idea, a security requirement, a temporary observation, a user request awaiting validation, a subsystem-specific constraint, or something that should not become durable memory at all.

The word “encrypting” does not answer the question.

The sentence requires context, judgment, and an understanding of project intent.

It is tempting to classify memory using simple keyword rules:

* Sentences containing “must” become constraints
* Sentences containing “decided” become decisions
* Sentences containing “avoid” become rejected approaches
* Sentences containing “consider” remain ideas

These rules fail quickly.

`We must consider whether SQLite is still inappropriate after the data model changes` does not establish SQLite as a constraint.

`We decided to investigate encryption, but no product decision has been made` does not make encryption an accepted architecture.

`Avoid describing the old API as deprecated until migration dates are confirmed` may be a temporary communication rule rather than an architectural tombstone.

Meaning depends on status, scope, context, and relationship to existing knowledge.

The semantic layer must evaluate what kind of knowledge an entry represents, whether it is confirmed, which part of the project it affects, whether it conflicts with existing memory, whether it is already documented elsewhere, and whether it is important enough to influence future sessions.

Those are appropriate tasks for a capable language model or a human reviewer.

A deterministic script should not pretend to make them.

Once the meaning and destination have been decided, however, deterministic tooling becomes valuable. The CLI can validate the destination file, resolve the manifest route, detect exact duplicates, preserve Markdown structure, preview a bounded change, apply the approved mutation, and report which files changed.

This division of responsibility is intentionally conservative.

The agent is not trusted to mutate durable files without structural controls. The CLI is not trusted to invent meaning it cannot understand.

> **The agent decides what the memory means. The CLI ensures the repository changes predictably.**

This boundary also makes failures easier to diagnose. When something goes wrong, it is clearer whether the problem came from semantic judgment or mechanical execution.

The same principle applies when memory is loaded into context.

A decision is not an arbitrary sequence of tokens. It may contain a heading, a selected direction, supporting reasoning, scope limitations, nested bullets, fenced examples, and references to related constraints.

Consider:

```markdown
## Use JSON for session storage

Use local JSON files for persistence.

Reasoning:
- Files must remain human-readable.
- The application must work offline.

Scope:
- This decision applies only to the current session store.
```

A raw token cutoff might preserve the instruction to use JSON while omitting the line that limits the decision to the current session store.

The shortened version is not merely incomplete. It changes the effective meaning by making a scoped decision appear global.

MemoryCustodian therefore treats complete semantic entries as atomic units when building context. If a full entry does not fit within the context budget, it can be omitted and reported. It should not be silently truncated into a misleading fragment.

Plain text does not mean unstructured. A Markdown-based system can still define file roles, task categories, entry boundaries, routing rules, validation requirements, context budgets, review workflows, and mutation previews.

The difference is that the structure remains visible.

Humans and agents can inspect both the stored knowledge and the rules used to activate it.

The same semantic boundaries must also govern deletion and mutation, which the [next article](/2026/07/21/memory-custodian-safe/) explores in detail.

---

## Visible Memory, Explicit Routing

Repo-native memory should not become a justification for storing everything.

Every trusted entry may influence future work. Poorly curated memory can preserve outdated assumptions, temporary opinions, or incorrect conclusions long after their original context has disappeared.

Early brainstorming, unverified hypotheses, one-off debugging observations, short-lived task status, full conversation transcripts, and suggestions that were never accepted should usually remain outside trusted project memory.

A useful test is:

> **Should this information continue to influence a capable agent in a future session?**

If the answer is uncertain, the candidate may belong in the inbox. If the answer is no, it should remain outside the durable memory system.

The goal is not to maximize stored context. It is to preserve the smallest reliable set of knowledge that prevents future developers and agents from repeating avoidable mistakes.

Plain-text, repo-native memory is also not the ideal architecture for every memory problem. A large enterprise knowledge base may require access controls, distributed indexing, document permissions, and semantic retrieval. A personal assistant may need preferences that span applications and do not belong in a single repository. A research system may need to search thousands of documents by meaning.

MemoryCustodian focuses on a narrower problem:

> **How should a software project preserve a curated set of decisions, constraints, rejected paths, and task-relevant context for coding agents?**

For that problem, Markdown, Git, and manifest routing offer a strong set of tradeoffs:

* Low infrastructure complexity
* High transparency
* Clear project ownership
* Native review and history
* Predictable context activation
* Cross-agent portability
* Graceful degradation
* Visible semantic structure

The most trustworthy project-memory system may not be the one with the most elaborate retrieval architecture.

It may be the one developers can still understand after the original demo is over.

A durable system should make it easy to answer where the memory is stored, which entries affected a task, why a decision was recorded, who changed it, whether it can be reviewed or reverted, and what happens when the original tooling is no longer available.

Plain Markdown provides visible storage; Git provides review, attribution, and history; the manifest provides explicit context routing; and semantic boundaries separate language-model judgment from deterministic CLI execution.

Together, these choices create a system that is intentionally ordinary at the storage layer and disciplined at the workflow layer.

> **Project memory should not be a hidden intelligence layer. It should be a visible project artifact.**

The project remembers more.

The agent loads less.

And the reasoning behind the code remains somewhere future developers and future agents can actually inspect.

## Key Takeaways

* Project memory should belong to the repository rather than one agent provider or conversation.
* Markdown offers portable storage; Git adds review, attribution, and history.
* A manifest separates everything the project remembers from what a task needs now.
* Semantic entries should remain complete when context is selected or shortened.

## Frequently Asked Questions

### Why not use a vector database for coding-agent memory?

Vector retrieval is useful at larger knowledge scales, but it adds infrastructure and can obscure why a particular memory was activated. For a curated set of project decisions and constraints, explicit Markdown files and manifest routing make ownership and behavior easier to inspect.

### Is Markdown structured enough for reliable memory?

Yes, when the system defines file roles, semantic entry boundaries, validation rules, routing, and context budgets. Plain text keeps that structure visible rather than eliminating it.

### What is the difference between storage and context?

Storage is the full set of durable project knowledge. Context is the smaller subset intentionally loaded for one task. Treating them separately lets memory grow without forcing every agent session to read all of it.

* [Read Part 3: Designing Memory That Can Safely Forget](/2026/07/21/memory-custodian-safe/)
* [Read Part 4: What Should a Coding Agent Be Allowed to Remember?](/2026/08/26/memory-custodian-remember/)
* [View the implementation on GitHub](https://github.com/waittim/MemoryCustodian)
* [Return to the series overview](/2026/07/01/memory-custodian/)

**Visible memory. Explicit routing. Project-owned context.**
