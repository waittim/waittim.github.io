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
header-mask: 0.5
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

Code describes what a system does today, but it rarely explains why the system must remain that way. A repository may reveal that an application stores data in JSON, yet fail to disclose why JSON was chosen over SQLite. It may show that the application has no external dependencies, without recording that offline operation is a non-negotiable product constraint. It may show that an earlier subsystem was removed, but omit the fact that the same approach was already tested twice, failed under specific edge cases, and should not quietly return.

This missing layer is project memory: the decisions behind the code, the constraints that must remain true, the rejected approaches that should not be rediscovered as new ideas, and the context that matters to some tasks but not every task.

The difficult question is not merely how to store that information. It is how to preserve it without turning every future task into an exercise in loading the project’s entire history.

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) is built around a deliberately restrained premise: project memory should be plain text, stored directly inside the repository, routed explicitly by task, and interpreted semantically by the model. This design rests on four pillars: Markdown provides durable and inspectable storage; Git turns memory into a governed project artifact; a manifest separates stored memory from active context; and language models interpret meaning while deterministic tools enforce structure. The result is not an invisible intelligence layer, but a transparent memory system the project can own, inspect, review, and operate without external services.

---

## Code Shows What. Memory Preserves Why.

Coding agents can reconstruct an impressive amount from source code alone: tracing execution paths, inspecting dependencies, identifying architectural patterns, and inferring component interactions. But inference is fundamentally distinct from project knowledge. From a local JSON storage implementation, an agent can infer that the data model is lightweight and no relational database is configured. What it cannot reliably infer is that users must be able to inspect and edit those files manually, that routine operations must function completely offline, that SQLite was already evaluated and rejected for this specific subsystem, or under what conditions that decision should be reconsidered.

Without durable memory, every new conversation starts with partial evidence. An agent proposes an apparently sensible change that quietly violates an unwritten invariant or repeats an already failed experiment. Conversation history cannot solve this: it is fragmented across individual users, model providers, and developer workstations. Project memory must belong to the repository itself so that architectural rationale survives new agent sessions, branch switches, and team turnover.

---

## Why Project Memory Should Live in the Repository

Plain text is unglamorous infrastructure, which is precisely its greatest asset. Durable project knowledge should remain understandable when the original tool, hosted service, or proprietary embedding model is unavailable. Developers should not depend on external APIs merely to inspect the architectural reasoning behind their own codebase.

Markdown achieves this through several structural strengths:

* **Direct human readability**: A developer can open `docs/memory/decisions.md` in any editor, terminal, or pull request without querying a retrieval interface.
* **Native agent comprehension**: Headings, lists, fenced blocks, and short structured entries are native inputs for language models across different provider environments without proprietary serialization.
* **Standard developer workflows**: Reviewers can edit, correct, or narrow a proposed constraint using standard pull request reviews before an entry becomes trusted project law.
* **Graceful degradation**: Even if the MemoryCustodian CLI is removed, the Markdown files remain fully legible and useful.

Storing memory inside the repository also places it under the governance framework engineering teams already trust: Git. Decisions such as avoiding SQLite or requiring offline operation shape engineering behavior as forcefully as configuration files. Treating memory as first-class Git artifacts ensures that changes are proposed in pull requests, attributed in commit history, reviewed collaboratively, and easily reverted when assumptions evolve. The repository itself becomes the authoritative interoperability layer between humans and coding agents.

---

## Why One Giant Instruction File Fails

Many projects already use files such as:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
```

Many projects attempt to preserve context through files like `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`. While effective for bootstrap commands, repository structure, and basic operating guidelines, they quickly degrade when expected to store the project’s entire accumulated history. Over time, product direction, architectural choices, formatting preferences, dependency restrictions, rejected experiments, and temporary workarounds pile into a single monolithic document.

Because every task loads the entire file, a simple documentation edit receives database migration history, while a frontend copy change inherits backend infrastructure tombstones. This collapses two distinct concerns: *what does the project remember* versus *what does the current task need to know*. MemoryCustodian separates stored memory from active context: the repository preserves a growing body of durable knowledge, while each task receives only the bounded, relevant subset routed to it. Memory can grow without limit; prompt context must stay small and focused.

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

The agent now receives the exact reasons and boundaries relevant to storage work without loading the project’s entire accumulated history. This ensures that context selection remains entirely inspectable: developers can review route definitions directly in Git, challenge task classifications, and audit why specific files were provided or omitted. 

Crucially, explicit routing demands explicit failures. If a task category is unrecognized, if a route targets a missing file, or if the manifest is malformed, the system must fail loudly rather than attempting silent fallbacks. In production agent environments, silently proceeding with incomplete memory is often far more dangerous than visibly halting on missing context.

---

## Routing and Retrieval: When Vector Search Wins and Why Invariants Differ

Semantic retrieval and vector databases are powerful tools when searching large, unstructured collections of documents. In systems navigating thousands of heterogeneous files, customer support transcripts, or sprawling research archives, embedding-based retrieval and Graph RAG shine. They excel at fuzzy discovery: answering queries where phrasing is unpredictable, entity relationships are loosely defined, and the goal is to discover *what information might be relevant*.

Manifest routing answers a fundamentally different question: what context is strictly required for this supported task category? That distinction matters because curated project memory has a completely different structural profile from a document corpus:

| Dimension | Vector / Semantic Retrieval | Manifest-Based Plain Text Routing |
|---|---|---|
| Primary domain | Unstructured document discovery & corpus search | Governed architectural decisions & project constraints |
| Query paradigm | Probabilistic fuzzy similarity (cosine distance) | Deterministic task category mapping (`manifest.md`) |
| Edge-case failure | Negations and short constraints drop below top-$k$ | Omissions are explicit and auditable via diagnostics |
| Infrastructure | Vector database, embedding models, index sync | Plain Markdown files checked directly into Git |
| Governance | Opaque similarity score thresholds | Git commits, branch review, and line-level diffs |

### Why Invariants Break Under Similarity Cutoffs

Curated project memory is usually small, sharp, and binary: ten confirmed decisions, five hard constraints, and a few subsystem invariants. The problem is not discovering text that feels vaguely related to the prompt; it is reliably enforcing rules that must not be broken.

Using vector similarity to retrieve project invariants breaks down in three practical ways:

1. **Short negations lose to affirmative descriptions:** A short constraint like *"Never introduce SQLite for session storage"* has very low embedding similarity to a prompt like *"Design a persistent session store with fast lookups."* In practice, embedding models often assign higher cosine similarity to paragraphs explaining how SQLite works than to a short rule forbidding it.
2. **Fixed top-$k$ cutoffs silently drop policy:** If your retrieval pipeline takes the top 5 chunks, an active constraint ranked 6th because of a lower similarity score simply disappears. The agent violates the project rule not because it reasoned poorly, but because the retrieval step treated a hard rule as a loose suggestion.
3. **Failures are hard to debug:** When an agent proposes a forbidden design, you cannot easily explain to a teammate why an embedding score landed at 0.72 instead of 0.75 without inspecting vector drift. With manifest routing, file inclusion is deterministic, committed to Git, and visible in a pull request.

This does not mean semantic search has no place in developer tooling. Search discovers candidate text across an unfamiliar codebase, while deterministic routing declares strictly required context across known project boundaries. Inside a codebase where continuity and invariants matter, deterministic routing gives coding agents the predictability they actually need.

MemoryCustodian therefore treats project memory less like an unstructured document corpus and more like semantic configuration: the routing policy is explicit and auditable, while the underlying content conveys nuanced engineering intent. This leads to a critical division of labor between semantic judgment and structural enforcement.

---

## Meaning Belongs to the Agent. Structure Belongs to the CLI.

## Meaning Belongs to the Agent. Structure Belongs to the CLI.

Consider a candidate memory entry:

```text
Consider encrypting exported notes with a user-provided passphrase.
```

Depending on context, this could be a confirmed product requirement, a speculative future feature, a temporary debugging observation, or something that should never enter durable memory. The keyword "encrypting" cannot resolve the ambiguity; determining its status requires understanding architectural context and project intent. Simple lexical heuristics—such as treating "must" as a constraint, "decided" as a decision, or "avoid" as a tombstone—inevitably fail on real engineering discussions, such as `We must consider whether SQLite is appropriate after the data model changes`.

This is why MemoryCustodian enforces a strict division of responsibility: **the agent evaluates semantic meaning, while the CLI enforces structural invariants**. Evaluating what kind of knowledge an entry represents, whether it conflicts with existing decisions, and whether it warrants admission requires the contextual judgment of a language model or human reviewer. Once that semantic choice is made, deterministic tooling takes over: validating file targets, resolving routes, enforcing entry schemas, preventing duplicate insertions, and generating diff previews. The agent is never permitted to mutate repository state unconstrained, and the CLI never attempts to invent meaning it cannot comprehend.

This distinction also governs context assembly. A decision is an atomic semantic unit—it consists of a heading, a chosen direction, explicit reasoning, and bounded scope limitations:

```markdown
## Use JSON for session storage

Use local JSON files for persistence.

Reasoning:
- Files must remain human-readable.
- The application must work offline.

Scope:
- This decision applies only to the current session store.
```

Arbitrary token cutoffs introduce severe risks: truncating an entry mid-paragraph might preserve the directive to use JSON while discarding the scope limitation that restricts it to session storage, mistakenly elevating a local decision into a global mandate. MemoryCustodian therefore treats complete semantic entries as indivisible units when constructing context. If an entry exceeds the remaining budget, it is omitted entirely and logged in diagnostics rather than silently fractured into a misleading snippet.

---

## Visible Memory, Explicit Routing

Repo-native memory is not a mandate to record everything. Uncurated memory is actively harmful: storing temporary debugging notes, unvetted brainstorming, or rejected proposals can mislead future agent sessions long after original assumptions expire. A reliable heuristic is straightforward: *should this invariant continue to guide a capable agent weeks from now?* If uncertain, candidate entries belong in `inbox.md`; if transient, they should stay out of the repository entirely.

Plain-text, repo-native memory does not aim to replace enterprise-scale knowledge graphs or cross-application user preferences. It focuses specifically on software repository governance: how a codebase preserves an auditable set of decisions, constraints, rejected paths, and task-relevant context. For this domain, Markdown, Git, and manifest routing provide the optimal engineering balance:

* Low infrastructure overhead and zero runtime dependency
* High transparency through line-level Git diffs and branch review
* Deterministic task-specific context activation
* Graceful degradation that survives the CLI itself

The most trustworthy memory system is rarely the one with the most intricate vector retrieval stack; it is the one developers and agents can inspect, understand, and debug directly in their standard development workflow. By pairing plain Markdown storage with explicit manifest routing and deterministic CLI boundaries, MemoryCustodian ensures that the project remembers why it was built, the agent loads only what is relevant, and the reasoning behind the code remains permanently reviewable.

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
* [Read Part 5: A Memory System Should Explain What It Did Not Load](/2026/09/15/memory-custodian-explainable-routing/)
* [View the implementation on GitHub](https://github.com/waittim/MemoryCustodian)
* [Return to the series overview](/2026/07/01/memory-custodian/)
