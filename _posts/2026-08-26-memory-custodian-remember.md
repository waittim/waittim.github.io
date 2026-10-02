---
layout: post
title: "What Should a Coding Agent Be Allowed to Remember?"
subtitle: "From persistent context to governed project memory in MemoryCustodian v0.10.0"
date: 2026-08-26
updated: 2026-08-26
author: Zekun Wang
description: "Why coding-agent memory should earn authority through admission, identity, routing, mutation safety, and bounded erasure—not mere persistence."
image: /img/headers/post-bg-hacker.jpg
series: MemoryCustodian Design Series
series_nav_title: Governed Memory
series_order: 4
header-img: img/headers/post-bg-hacker.jpg
header-mask: 0.5
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

## Persistence Should Not Automatically Grant Authority

When a coding agent inspects a repository and notices that every data file uses JSON, that observation is factually correct. But should every subsequent session treat **“this project requires JSON-only persistence”** as permanent project policy? 

This highlights the core boundary often missed in persistent agent systems: persistence is not merely a recall problem, but an authority problem. Without explicit governance, a mistaken inference outlives the conversation that spawned it, a temporary workaround quietly hardens into an immutable rule, and offhand remarks continue steering implementation weeks down the line.

*For developers designing governed project memory for coding agents. Implementation details in this article reflect MemoryCustodian v0.10.0.*

The central design premise of [MemoryCustodian](https://github.com/waittim/MemoryCustodian) v0.10.0 is that **persistence should not automatically grant authority**. Preserving an observation is cheap, but granting it the power to constrain future development requires admission evidence, stable identity, clear ownership boundaries, inspectable routing, and bounded erasure.

---

## 1. Observation Is Not Memory

Suppose an agent is debugging a storage subsystem. It notices that:

- every current persistence file is JSON
- there is no SQLite dependency
- the project works offline

From those facts, it may infer that the project requires JSON-only persistence.

That inference might be useful, and it may even turn out to be correct. But it is still an inference. Perhaps JSON is only the current implementation; perhaps SQLite was rejected for one subsystem but remains acceptable elsewhere; perhaps the architecture is about to change in an open pull request.

If the agent writes that observation straight into `constraints.md`, a temporary note quietly turns into a permanent rule. The next session doesn't see 'an earlier agent noticed JSON files'—it sees 'this project forbids relational databases.'

That jump from observation to project policy shouldn't happen by accident. An agent can notice patterns, but it shouldn't promote its own inferences into active constraints without human review or qualifying evidence.


### Candidate first, active later

Protocol 0.6 makes this boundary explicit. A new formal active memory entry must have qualifying Evidence—such as explicit user confirmation, repository-relative documentation, test fixtures, or issue references. Unverified signals, including `agent-observed` or conversation transcripts, are restricted to candidate status.

The critical architectural transition is not from “unknown” to “stored”, but from candidate to active policy. As illustrated in Figure 1, candidate observations are staged in `docs/memory/inbox.md`. Because candidate files are excluded from default task context, downstream agent sessions do not inadvertently obey speculative constraints. It remains cheap to record an observation for review, but intentionally harder to elevate that observation into project authority.

![From Observation to Trusted Memory — observations remain candidates until qualifying evidence or confirmation admits them into active project memory.]({{ "/img/posts/2026-08-26-memory-custodian-remember/observation-to-trusted-memory.svg" | relative_url }})

*Figure 1. Protocol 0.6 separates preserving an observation from admitting it into trusted project memory.*

### A Concrete Walkthrough: Intercepting Speculative Memory

Suppose an agent observes that the current data files use JSON and attempts to turn that observation into a permanent project constraint.

For the following command, `SUBJECT_ID` must contain an existing active Subject ID from `subjects.md`. MemoryCustodian generates Subject IDs in the form `MC-SUBJ-YYYYMMDD-XXXXXXXX`; a display name such as `storage-engine` is not a valid replacement for the registered ID.

```bash
# SUBJECT_ID contains an existing active Subject ID from subjects.md.
memory-custodian add \
  "All persistent storage must use JSON; relational databases are prohibited." \
  --type constraint \
  --subject "$SUBJECT_ID" \
  --facet architecture \
  --evidence agent-observed
```

In v0.10.0, this attempt exits with code `2` and reports the following error on stderr:

```text
Error: agent-observed evidence cannot create active memory. Use --candidate or provide user-confirmed/source-backed evidence.
```

The rejection leaves the managed memory unchanged. It does not automatically save the observation in `inbox.md`. Preserving the observation requires a separate, explicit candidate write:

```bash
memory-custodian add \
  "All persistent storage must use JSON; relational databases are prohibited." \
  --type constraint \
  --candidate \
  --evidence agent-observed
```

This command records the observation as a candidate in `docs/memory/inbox.md`, with its unverified Evidence preserved. It does not create an active constraint, and normal planning or implementation context does not load that candidate.

Creating a formal active constraint later requires semantic review, qualifying Evidence, a registered Subject, and a controlled Facet. Qualifying Evidence may be explicit user confirmation (`user-confirmed`) or an existing project source such as `doc:docs/architecture/storage.md`. The evidence reference records why admission is allowed; it does not itself prove the claim's meaning or continued correctness.

### Evidence is not a truth machine

Calling this “evidence-backed memory” requires an important qualification. Evidence does not prove that a statement remains eternally true; documentation rots, requirements evolve, tests get rewritten, and pull requests get reverted. Rather than asserting timeless ground truth, admission evidence answers an operational governance question: *why was this entry permitted to become active project memory?* Grounding active constraints in inspectable provenance provides a concrete audit trail when policies inevitably conflict or need retirement.

---

## 2. Memory Needs Identity, Not Just Text

Admission solves only the first problem. Even trusted memory becomes unreliable if identity depends only on wording.

Imagine a project initially calls a dependency `Library X`, later documents it as `library-x`, while a developer abbreviates it as `libx`.

Those three names may refer to one underlying thing—or they may not. A system based only on text therefore has two bad options: treat each spelling as a new entity and accumulate duplicate or conflicting memory, or use fuzzy similarity to guess that they refer to the same thing and risk merging unrelated concepts.

MemoryCustodian v0.10.0 takes a more explicit approach based on structured identity.

### Subject: what are we talking about?

A **Subject ID** represents the stable project entity governed by a memory record. While display names and informal abbreviations may shift across teams and refactors—from `Library X` to `library-x` or `libx`—the Subject identity remains constant. MemoryCustodian intentionally avoids guessing entity equivalence from heuristics or word embeddings; aliases and identity unifications must be declared explicitly so that renames never silently spawn conflicting rules.

### Entry: which claim are we talking about?

While a Subject identifies the entity, an **Entry ID** identifies a specific, versioned claim about that entity. When a project updates its baseline from Python 3.10 to Python 3.12, the original decision should not quietly vanish without history. A new entry explicitly supersedes the older Entry ID, allowing the system to distinguish historical context from the currently active rule without losing the rationale behind the transition.

### Facet: which dimension does the claim govern?

A single Subject often accumulates multiple active policies across distinct engineering concerns—such as adoption, versioning, architecture, compatibility, security, and performance. Protocol 0.6 models these dimensions as controlled **Facets**.

![Stable Identity and Active Ownership — Subject IDs identify the entity, Entry IDs identify claims, while Scope and Facet define the active ownership boundary.]({{ "/img/posts/2026-08-26-memory-custodian-remember/stable-identity-active-ownership.svg" | relative_url }})

*Figure 2. Subject identity stays stable across names, while `Scope + Subject ID + Facet` defines the active ownership boundary.*

This structure establishes a deterministic conflict boundary: two project-level entries cannot independently claim ownership over the same `version-policy` facet for the same Subject without an explicit supersede relation. Conversely, a `security` constraint and a `version-policy` entry can safely coexist on the same Subject because they govern orthogonal concerns. This gives persistent memory explicit ownership rather than loose Markdown notes.

---

## 3. Authority Should Be Traceable

Once memory has been admitted and assigned an identity, the system must decide when it should actually enter prompt context. A repository may eventually accumulate hundreds of durable memories; injecting all of them into every prompt exhausts context budgets and dilutes model focus. MemoryCustodian balances this through a core architectural constraint: **memory can grow arbitrarily large, but active context must remain compact**.

Under this model, `manifest.md` acts as the runtime routing authority. Supported canonical tasks, explicit profiles, and scoped domain areas determine which memory modules load into a session. Crucially, routing is inspectable rather than probabilistic: every loaded module carries a recordable provenance flag:

```text
always-load
canonical-task
explicit-profile
explicit-area
```

Likewise, omitted modules can be diagnosed with equal clarity. When a developer asks why a particular memory affected an agent—or why an architectural rule was excluded—the answer is grounded in project configuration rather than an opaque similarity threshold. As explored in [Part 2](/2026/07/20/memory-custodian-tech-design/), search discovers what might matter, but deterministic routing declares what must matter.

---

## 4. Durable Authority Needs Safe Mutation

Because project memory governs subsequent agent runs, modifying it is an update to shared repository state rather than an ordinary file edit. Two concurrent agents, or an agent applying an outdated diff after files have shifted, can easily corrupt project invariants. Plain text makes memory human-readable and diffable in Git, but it does not eliminate concurrency hazards.

### Safe state transitions and preview workflows

While routine `add` commands directly append validated entries once admission checks pass, structural and destructive operations—such as `compact` and `forget`—enforce a preview-first mutation model. The CLI computes an execution plan against current disk state, issues a plan ID, and pauses for review. When `--apply` is invoked, the system verifies that the target files have not drifted since the plan was generated and aborts if stale state is detected. This guarantees that confirmation authorizes a specific state transition rather than an unchecked modification.

Crucially, memory entries carry context, not capability tokens. An admitted memory entry can document constraints on project architecture, but it can never grant an agent authorization to bypass security boundaries, access secrets, upload code externally, push commits, or execute privileged operations.

---

## 5. Erasure Should Describe the State the System Actually Controls

Persistent memory also introduces retirement challenges. When information becomes obsolete, users need a dependable mechanism to withdraw its influence. MemoryCustodian supports soft forget, hard forget, and purge modes, but v0.10.0 strictly bounds what those operations promise.

In distributed software development, promising universal deletion is impossible: code resides across Git clones, CI runners, remote forks, and offline backups. MemoryCustodian therefore contracts only what it directly manages: matching information is reliably removed from managed repository files (`docs/memory/`) and local archives. It explicitly does not claim to rewrite Git history or revoke external copies. Grounding deletion guarantees in bounded, inspectable scope builds far more operational trust than impossible claims of universal erasure.

Stable Subject IDs make ownership and references inspectable, but they do not turn forgetting into an alias-aware cascade. In v0.10.0, `forget TOPIC` uses literal, case-insensitive matching against supported Markdown units. If removing a Subject would leave retained entries referring to it, the mutation plan is blocked. Retiring all guidance associated with a Subject therefore requires explicit review of the relevant entries; aliases do not automatically expand a forgetting request into deletion of every reference.

---

## 6. NightNotes: One Example End to End

The NightNotes fixture makes the whole model easier to see. The project has several pieces of durable knowledge:

- session persistence should use human-readable local JSON
- routine operation must work without network access
- routine operation should use only the Python standard library
- existing note files should remain human-readable
- SQLite should not be introduced for the current session store

It also contains another idea: consider encrypting exported notes with a user-provided passphrase.

The important part is that those statements do not all have the same authority.

![NightNotes end-to-end example — trusted JSON, offline, standard-library, and no-SQLite memory enters task context through manifest routing while the encryption candidate stays in the inbox.]({{ "/img/posts/2026-08-26-memory-custodian-remember/nightnotes-end-to-end.svg" | relative_url }})

*Figure 3. NightNotes routes trusted project memory into the task while keeping the unconfirmed encryption idea preserved but outside normal context.*

Now imagine a fresh coding-agent session receives only this prompt:

> Plan how to implement persistent session state.  
> Before proposing changes, use the repository's project memory.  
> Do not modify any files.

The prompt mentions none of them—JSON, SQLite, offline operation, or standard library restrictions. Those constraints already belong to the project. A useful memory system must recover important project knowledge, but it must also prevent uncertain information from quietly acquiring authority merely because an agent noticed it in a previous turn. That distinction is the core change in v0.10.0.

---

## The Hard Part of Memory Is Not Remembering

Agent memory is often evaluated strictly by recall: whether the system can recover an earlier decision, carry context across sessions, and stop the agent from repeating work. While those are necessary capabilities, once memory becomes durable, operational governance questions become equally critical:

- Why was this information admitted?
- Is it confirmed or merely observed?
- What project entity does it refer to?
- Which entry currently owns this policy?
- Where does the policy apply?
- Why was it activated for this task?
- Can a mutation be reviewed before it changes durable state?
- What exactly happens when the memory is retired?
- What remains outside the system's erasure boundary?

These are fundamental governance questions that grow more critical as agent capabilities expand. While a stateless agent forgets an erroneous inference as soon as its session ends, an unconstrained persistent agent risks institutionalizing that bad inference into permanent project law. Restraint and explicit verification gates prevent durable context from degenerating into durable technical debt.

---

## From Persistent Memory to Governed Memory

Designing effective agent memory requires shifting perspective from simple recall (*how do we help the agent remember?*) to active governance (*what information has earned the authority to influence future work?*). This shift transforms every layer of the architectural stack:

| System Component | Role in Conventional Persistent Recall | Role in Governed Project Memory |
|---|---|---|
| **Inbox (`inbox.md`)** | Staging buffer for unorganized notes | Hard authority boundary isolating unverified candidates |
| **Evidence Metadata** | Optional descriptive comment | Formal prerequisite for active policy admission |
| **Subject & Entry IDs** | Markdown header strings | Stable semantic identity across renames and lifecycle replacements |
| **Facets** | Arbitrary tags | Deterministic ownership and collision boundaries |
| **Manifest Routing** | Heuristic context inclusion | Verifiable provenance declaring why context entered prompt |
| **Mutation Previews** | Dry-run text diff | Transactional state-transition guard preventing concurrent drift |
| **Bounded Erasure** | Unbounded string deletion | Explicit, auditable retirement boundary over managed files |

MemoryCustodian v0.10.0 implements this trust model on top of ordinary, durable primitives: Markdown files, Git repositories, explicit manifests, and a local CLI. The objective is not to build a complex memory engine, but to ensure that stored knowledge remains inspectable: future developers and agents should always understand why an entry was admitted, what scope it governs, why it entered context, and when it should safely be retired.

---

## Key Takeaways

- **Persistent memory creates an authority problem, not only a storage problem.**
- **Observations may be preserved as candidates, while active memory requires inspectable admission evidence.**
- **Stable Subject, Entry, Scope, and Facet identity separate what a memory says from what project policy it actually governs.**
- **Trustworthy project memory should make admission, activation, mutation, and erasure explainable.**

---

## Frequently Asked Questions

### How does MemoryCustodian decide what becomes active memory?

Under Protocol 0.6, new formal active entries require qualifying Evidence. Explicit user confirmation and supported project sources can support active memory. Agent observations and unconfirmed conversation content remain candidate-only until stronger evidence or confirmation exists.

### How does MemoryCustodian decide what memory enters a task?

`manifest.md` is the runtime routing authority. Memory is activated through explicit canonical task routes and explicit profile or area inputs rather than hidden embedding or keyword relevance scores.

### Can users see why memory was loaded or omitted?

That is the goal of structured routing provenance. Loaded modules can be traced to explicit reasons such as default loading, a canonical task route, an explicit profile, or an explicit area. Omission should likewise be explainable rather than silently hidden.

### Why not just use embeddings to detect relevance and conflicts?

Semantic similarity is useful for discovery. It is a weaker basis for authority. Two contradictory rules may be highly similar, while an important hard constraint may share little wording with the current task. MemoryCustodian therefore uses explicit routing, Subject identity, Scope, Facets, and supersede relationships for governance.

### What does purge actually erase?

It removes matching information from the managed MemoryCustodian state covered by the operation, including managed archive content when applicable. It does not rewrite Git history or revoke clones, forks, backups, caches, or previously distributed copies.

---

MemoryCustodian v0.10.0 marks a transition from open-ended persistence to governed project memory: rather than attempting to remember everything, it preserves the specific architectural constraints that deserve to influence future work, making that authority inspectable and reviewable.

* [Start with the series overview](/2026/07/01/memory-custodian/)
* [Read Part 2: Why Project Memory Should Be Plain Text and Repo-Native](/2026/07/20/memory-custodian-tech-design/)
* [Read Part 3: Designing Memory That Can Safely Forget](/2026/07/21/memory-custodian-safe/)
* [Read Part 5: A Memory System Should Explain What It Did Not Load](/2026/09/15/memory-custodian-explainable-routing/)
* [Read Part 6: A Memory System Should Survive an Interrupted Write](/2026/10/01/memory-custodian-crash-recovery/)
* [View the implementation on GitHub](https://github.com/waittim/MemoryCustodian)

