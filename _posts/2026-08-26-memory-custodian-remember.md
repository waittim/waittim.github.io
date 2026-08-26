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

A coding agent notices that every persistence file in a repository is JSON.

That observation may be correct.

But should every future coding agent now treat **“this project requires JSON-only persistence”** as project policy?

That is a different question.

*For developers designing governed project memory for coding agents. Implementation details in this article reflect MemoryCustodian v0.10.0.*

Persistent memory is often framed as a recall problem: how do we help an agent remember decisions across sessions? But once memory survives the session that created it, persistence becomes an authority problem too. A mistaken inference can outlive the conversation that produced it. A temporary workaround can quietly become a permanent constraint. An idea mentioned once can keep influencing implementation weeks later.

So the harder question is not simply:

> How should a coding agent remember?

It is:

> **What should a coding agent be allowed to remember as trusted project memory?**

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) v0.10.0 is built around that distinction.

The central idea is simple:

> **Persistence should not automatically grant authority.**

A statement may be worth preserving without yet being trusted enough to guide future work. That leads to a different model of agent memory—one based not only on storage and retrieval, but on **admission, identity, ownership, activation, lifecycle, and erasure**.

---

## 1. Observation Is Not Memory

Suppose an agent is debugging a storage subsystem. It notices that:

- every current persistence file is JSON
- there is no SQLite dependency
- the project works offline

From those facts, it may infer that the project requires JSON-only persistence.

That inference might be useful, and it may even turn out to be correct. But it is still an inference. Perhaps JSON is only the current implementation; perhaps SQLite was rejected for one subsystem but remains acceptable elsewhere; perhaps the architecture is about to change in an open pull request.

If the agent writes the conclusion directly into durable project memory, something subtle has happened. The next session no longer sees “a previous agent observed a pattern.” It sees “the project requires JSON.”

The observation has become authority.

That transition should not happen accidentally.

### Candidate first, active later

Protocol 0.6 makes this boundary explicit. A new formal active memory entry must have qualifying Evidence, which may come from:

- explicit user confirmation
- a safe repository-relative source
- a project document
- a test
- an issue or pull request reference

By contrast, evidence such as `agent-observed` or `conversation-unconfirmed` can support a **candidate**, but not a new active entry.

The important transition is not from “unknown” to “stored.”

It is from **candidate** to **active**.

![From Observation to Trusted Memory — observations remain candidates until qualifying evidence or confirmation admits them into active project memory.]({{ "/img/posts/2026-08-26-memory-custodian-remember/observation-to-trusted-memory.png" | relative_url }})

*Figure 1. Protocol 0.6 separates preserving an observation from admitting it into trusted project memory.*

MemoryCustodian therefore tries to make one thing easy and another deliberately harder:

> **It should be cheap to preserve an observation, but harder to turn that observation into authority.**

That is what the inbox is for. An idea can survive without immediately becoming project policy, and because candidates do not enter normal task context, a future coding agent does not automatically obey them.

### Evidence is not a truth machine

Calling this “evidence-backed memory” needs an important qualification. Evidence does not prove that a statement is eternally true. A repository file can become outdated, a test can encode obsolete behavior, a user can reverse a decision, and a pull request can later be reverted.

Evidence serves a narrower purpose:

> **It answers “why was this admitted?”, not “is this forever true?”**

That distinction matters. The system still needs semantic judgment and lifecycle management. But a new formal memory entry should at least be able to answer why it was allowed to become active project memory. That is a much stronger boundary than simply allowing any plausible statement to persist.

---

## 2. Memory Needs Identity, Not Just Text

Admission solves only the first problem. Even trusted memory becomes unreliable if identity depends only on wording.

Imagine a project initially calls a dependency `Library X`, later documents it as `library-x`, while a developer abbreviates it as `libx`.

Those three names may refer to one underlying thing—or they may not. A system based only on text therefore has two bad options: treat each spelling as a new entity and accumulate duplicate or conflicting memory, or use fuzzy similarity to guess that they refer to the same thing and risk merging unrelated concepts.

MemoryCustodian v0.10.0 takes a more explicit approach.

### Subject: what are we talking about?

A **Subject ID** represents the project entity a memory concerns. A Subject can have a stable identifier, a canonical reference, and explicit aliases.

The display name may change.

The identity does not have to.

This lets the system distinguish between **what something is called** and **what project entity it actually represents**.

MemoryCustodian intentionally does not infer semantic identity from fuzzy names, timestamps, or entry bodies. If two Subjects should be unified, that is an explicit decision.

### Entry: which claim are we talking about?

A Subject identifies the thing; an **Entry ID** identifies a particular memory record about that thing. The distinction matters because project knowledge changes.

Suppose a project has an active decision to support Python 3.10+. Months later, the support policy changes. The correct model is not necessarily to erase the old text and pretend it never existed. The new entry can explicitly supersede the previous one, so the system can distinguish an older historical assertion from the current active assertion.

That gives memory a lifecycle. Without stable Entry IDs, old project knowledge tends to linger as ambiguous prose. With them, a later entry can explicitly say that **this replaces that**.

### Facet: which dimension does the claim govern?

One Subject can legitimately have many active memories. A dependency might have separate policies for adoption, versioning, architecture, compatibility, security, performance, and lifecycle.

Those are different dimensions.

Protocol 0.6 represents them using controlled **Facets**, such as `adoption-policy`, `version-policy`, `architecture`, `behavior`, `compatibility`, `security`, `performance`, `data-model`, `interface`, `workflow`, and `lifecycle`.

![Stable Identity and Active Ownership — Subject IDs identify the entity, Entry IDs identify claims, while Scope and Facet define the active ownership boundary.]({{ "/img/posts/2026-08-26-memory-custodian-remember/stable-identity-active-ownership.jpg" | relative_url }})

*Figure 2. Subject identity stays stable across names, while `Scope + Subject ID + Facet` defines the active ownership boundary.*

That gives the system a deterministic conflict boundary. Two project-level entries should not independently own the same `version-policy` for the same Subject. If the policy changes, the replacement should explicitly supersede the earlier owner. At the same time, a `security` entry and a `version-policy` entry can coexist because they govern different dimensions.

This is where the model becomes more than “structured Markdown.” It gives persistent project memory a notion of **ownership**.

---

## 3. Authority Should Be Traceable

Once a memory entry has been admitted and assigned identity, there is still another question:

> When should it actually influence an agent?

A repository may eventually contain hundreds of durable memories, and loading all of them into every task would defeat the purpose. MemoryCustodian has always worked from a simple principle:

> **Memory can grow; context must stay small.**

The distinction becomes clearer when memory is treated as governed authority. There are now three separate questions. Admission asks whether something can become trusted memory. Identity asks what that memory governs. Activation asks when it should enter active context.

For activation, `manifest.md` remains the runtime routing authority. A supported canonical task determines which memory modules should be loaded, with explicit profile or area inputs able to add scoped context.

The key point is not that routing is “smart.”

It is that routing is **inspectable**.

A loaded module can have a recordable reason such as:

```text
always-load
canonical-task
explicit-profile
explicit-area
```

Likewise, an omitted module can have an explicit reason. That lets a developer ask:

> Why did this memory affect the agent?

and receive an answer grounded in project configuration rather than an opaque similarity score.

I covered the broader distinction between routing and retrieval in [Part 2](/2026/07/20/memory-custodian-tech-design/). The v0.10.0 change is that this provenance becomes more structured. The broader design principle remains:

> **Search can discover what might matter. Routing should declare what must matter.**

That distinction becomes especially important once persistent memory is allowed to govern future behavior.

---

## 4. Durable Authority Needs Safe Mutation

If project memory can influence future agents, modifying it is no longer a trivial file edit. It is shared project state: two agents may attempt to update it at the same time, a user may apply a previously reviewed mutation after the underlying files have changed, or a migration may install project identity while another writer still believes it is operating on the earlier state.

Plain text makes memory visible and diffable.

It does not make concurrency disappear.

### Preview should describe the state that will actually change

v0.10.0 strengthens mutation safety around a preview-first model. The system builds a preview from the current memory state, assigns a plan ID, and waits for review. Only after acquiring a mutation guard does it re-read the current state, rebuild the plan, and apply the change if the confirmation is still valid.

If a target changed after the preview, the old confirmation no longer applies and the operation refuses. That is important because confirmation should authorize a **specific state transition**, not merely a command name.

The project ID introduced by Protocol 0.6 helps coordinate mutation locks and distinguish initialized projects. But that identity is not permission. A remembered project entry cannot use persistence to grant itself new authority.

Memory cannot authorize:

- destructive operations
- secret access
- external uploads
- commits
- pushes
- merges
- releases
- privilege escalation

Project memory can constrain project work. It cannot elevate itself above current instructions, safety rules, or permission boundaries.

> **Memory is context, not a capability token.**

---

## 5. Erasure Should Describe the State the System Actually Controls

Persistent memory also creates a deletion problem. If information can keep influencing future work, users need a way to stop that influence.

MemoryCustodian already distinguishes soft forget, hard forget, and purge. I covered that design in more depth in [Part 3](/2026/07/21/memory-custodian-safe/). v0.10.0 sharpens the boundary around what those operations actually control.

The useful question is not whether the system can promise that the information no longer exists anywhere—it usually cannot. The more useful question is:

> Which managed state can this operation reliably remove?

Managed active memory is in scope. Managed archive content is also in scope when purge is used. Git history, existing clones, forks, backups, caches, and previously distributed copies are not.

That distinction is more important than it may appear. “Purge” should not imply universal deletion if the tool does not control every copy of the repository.

A more trustworthy contract is:

> The matching information has been removed from the managed MemoryCustodian scope covered by the operation.

That means future agents using that managed state will no longer receive it. It does **not** mean Git history was rewritten or external copies were revoked.

> **An honest erasure boundary is more trustworthy than an impossible promise of universal deletion.**

The same identity model that helps admission also helps erasure. If a dependency has been called `Library X`, `library-x`, and `libx`, stable Subject identity provides a stronger maintenance anchor than wording alone. Identity therefore affects not only how memory is created, but also how reliably it can be retired.

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

![NightNotes end-to-end example — trusted JSON, offline, standard-library, and no-SQLite memory enters task context through manifest routing while the encryption candidate stays in the inbox.]({{ "/img/posts/2026-08-26-memory-custodian-remember/nightnotes-end-to-end.jpg" | relative_url }})

*Figure 3. NightNotes routes trusted project memory into the task while keeping the unconfirmed encryption idea preserved but outside normal context.*

Now imagine a fresh coding-agent session receives only this prompt:

> Plan how to implement persistent session state.  
> Before proposing changes, use the repository's project memory.  
> Do not modify any files.

The prompt mentions none of them—JSON, SQLite, offline operation, or the standard library.

Those constraints already belong to the project.

A useful memory system must recover important project knowledge. But it must also prevent uncertain information from quietly acquiring authority merely because an agent noticed it once.

That is the core change in v0.10.0.

---

## The Hard Part of Memory Is Not Remembering

Agent memory is often evaluated by recall: Can the system recover an earlier decision, carry context across sessions, and stop the agent from repeating work?

Those are important capabilities.

But once memory becomes durable, other questions become equally important:

- Why was this information admitted?
- Is it confirmed or merely observed?
- What project entity does it refer to?
- Which entry currently owns this policy?
- Where does the policy apply?
- Why was it activated for this task?
- Can a mutation be reviewed before it changes durable state?
- What exactly happens when the memory is retired?
- What remains outside the system's erasure boundary?

Those are governance questions, and they become more important as the agent becomes more capable.

A stateless agent can forget a bad inference when the session ends.

A persistent agent can institutionalize it.

That makes restraint a feature.

---

## From Persistent Memory to Governed Memory

The first question in an agent-memory system is usually:

> How do we make the agent remember?

The next one should be:

> What information has earned the right to influence future work?

That second question changes the architecture.

It turns the inbox into an authority boundary.

It turns Evidence into an admission requirement.

It turns Subject IDs into stable semantic identity.

It turns Entry IDs into lifecycle anchors.

It turns Facets into ownership boundaries.

It turns routing into provenance.

It turns mutation previews into state-transition controls.

And it turns forgetting into an explicit erasure scope rather than a vague promise.

MemoryCustodian v0.10.0 is a step in that direction. The implementation still uses intentionally ordinary primitives:

- Markdown
- local files
- Git
- explicit manifests
- a local CLI

What has become more structured is the trust model around them.

Because project memory is not useful merely when it survives.

It is useful when future developers and agents can understand:

> **why it survived, what it governs, why it applies, and when it should stop applying.**

Persistent memory should not automatically grant authority.

Memory should earn persistence.

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

MemoryCustodian v0.10.0 moves the project from persistent memory toward **governed project memory**.

The goal is not to remember everything.

It is to preserve the project knowledge that deserves to influence future work—and to make that influence inspectable.

* [Start with the series overview](/2026/07/01/memory-custodian/)
* [Read Part 2: Why Project Memory Should Be Plain Text and Repo-Native](/2026/07/20/memory-custodian-tech-design/)
* [Read Part 3: Designing Memory That Can Safely Forget](/2026/07/21/memory-custodian-safe/)
* [View the implementation on GitHub](https://github.com/waittim/MemoryCustodian)

**Memory should earn persistence.**
