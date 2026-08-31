---

layout: post
title: "A Memory System Should Explain What It Did Not Load"
subtitle: "Deterministic and inspectable context routing in MemoryCustodian v0.11.0"
date: 2026-09-15
updated: 2026-09-15
author: Zekun Wang
description: "Why selective agent-memory routing needs inspectable module dispositions, completeness diagnostics, strict gates, and explicit omission—not hidden retrieval guesses."
image: /img/headers/post-bg-computer-storage.jpeg
series: MemoryCustodian Design Series
series_nav_title: Explainable Routing
series_order: 5
header-img: img/headers/post-bg-computer-storage.jpeg
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

## A Bounded Context Pack Should Explain Its Omissions

A coding agent starts an implementation task.

The project has durable memory: architectural decisions, hard constraints, rejected approaches, subsystem-specific notes, personal workflow preferences, and historical context.

The agent receives four memory files.

That sounds useful.

But four files alone do not answer the more important questions:

* Why these four?
* Which other modules were considered?
* Which ones were skipped?
* Was something required but unavailable?
* Did the task provide enough scope to decide which subsystem memory should apply?
* Did a selected module contain an entry that could not fit within the context budget?

And, perhaps most importantly:

> Is this context pack complete enough to rely on before changing the code?

A memory system that can only explain what it loaded is showing half of its decision.

*For developers building governed context systems for coding agents. Implementation details in this article reflect MemoryCustodian v0.11.0 and Protocol 0.7.*

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) has always been built around one principle:

> **Memory can grow; context must stay small.**

Selective loading creates a second obligation.

If a system intentionally does not load everything, omission becomes part of the system's behavior. A trustworthy router therefore needs to make both sides of the selection visible.

This does not mean enumerating every repository file that might possibly be relevant. MemoryCustodian explains the routing boundary it actually governs: manifest-managed modules, explicit policy exclusions, missing routed modules, and complete entries omitted from the selected pack because of budget.

The central idea in v0.11.0 is:

> **A bounded context pack should be deterministic, inspectable, and explicit about what it leaves out.**

---

## 1. Persistent Memory Still Has a Selection Problem

Persistent memory solves one problem and immediately creates another.

Suppose a repository remembers all of the following:

* A storage subsystem must remain human-readable.
* An authentication module has a compatibility workaround.
* The deployment pipeline must avoid a particular provider.
* The documentation uses a specific terminology convention.
* A frontend subsystem rejected one state-management library.
* A developer personally prefers concise commit summaries.

All of these facts may be worth preserving.

That does not mean all of them belong in every coding task.

Loading the entire memory store into every session would turn durable memory into another oversized instruction file. The repository would remember more, but every task would pay for all of it.

The alternative is routing: preserve a larger body of project knowledge, then activate only a bounded subset for the current task.

That is the distinction behind MemoryCustodian's original design:

> **Memory is what the project preserves. Context is what the current task receives.**

But once routing exists, the router itself becomes part of the trust boundary.

Imagine an agent modifying an authentication module. The project has an authentication-specific constraint, but the router never loads it because the task was not scoped correctly.

Nothing in the resulting context pack may look obviously wrong.

Every file that was loaded may be valid.

The problem is what is absent.

Partial context can look authoritative. An agent can follow every instruction it received and still violate a decision it never had the opportunity to see.

So selective memory requires more than retrieval.

It requires **selection accountability**.

A useful context system should make it possible to inspect both sides of the result:

> These modules were loaded.

and:

> These modules were not loaded, for these reasons, under these inputs.

That negative evidence matters because omission is often where routing failures hide.

---

## 2. Routing Should Use Declared Inputs, Not Hidden Guesses

There are many ways a context router could try to determine relevance.

It could inspect the task description for keywords.

It could embed the prompt and compare it with stored memories.

It could scan source code and infer which subsystem seems related.

It could ask an LLM to choose which memory files "feel relevant."

Those approaches can be useful in discovery systems.

They are weaker foundations for a governed routing boundary.

If two equivalent routing requests can produce different context because a model interpreted the task differently, developers have a harder time answering a basic debugging question:

> Why did this memory affect this run but not the previous one?

MemoryCustodian v0.11.0 takes a deliberately narrower approach.

Routing is based on declared inputs.

The system receives a canonical task category. It can receive planned or touched paths. It can receive explicitly requested rules, profiles, or areas. The manifest defines how those inputs map to memory modules.

For the same manifest and the same declared routing inputs, the routing result is deterministic.

That means the router does not need to inspect implementation code and guess which area the task belongs to.

It does not need to score natural-language similarity between the prompt and every stored memory.

It does not need an LLM to secretly rank project rules by relevance.

Paths can activate areas through declared path patterns.

Rules can activate through declared tasks or explicit selection.

Profiles remain explicit.

Root constraints remain part of the shared project safety baseline.

The distinction is important.

A deterministic router is not claiming to understand the task better than an intelligent retrieval model.

It is making a smaller claim:

> **Given these declared inputs and this manifest, this is the context the project says should be loaded.**

That claim is easier to inspect, reproduce, test, and review.

It also puts uncertainty in the right place.

If the task has not provided enough scope to choose between path-routed areas, the system should not compensate by silently reading source files and guessing.

It should say that the routing input is incomplete.

I covered the broader distinction between routing and retrieval in [Part 2](/2026/07/20/memory-custodian-tech-design/). v0.11.0 makes the omission side of that boundary explicit.

![Explainable context routing in MemoryCustodian]({{ "/img/posts/2026-09-15-memory-custodian-explainable-routing/memorycustodian-explainable-routing.svg" | relative_url }})

*Figure 1. Explainable routing accounts for both selected context and explicit omissions. The manifest resolves declared task and scope inputs deterministically; completeness and budget diagnostics remain separate from semantic relevance.*

---

## 3. Complete Does Not Mean Semantically Correct

The word *complete* can be misleading in a memory system.

Suppose a task declares that it will modify:

```text
cli/memory_custodian/read.py
```

The manifest has an area whose path matcher covers that file.

The canonical task is supported.

The required root memory exists.

The applicable optional modules can all be resolved.

The router may now describe the routing input as complete.

But what has actually been proven?

Not that every loaded memory is semantically relevant.

Not that the developer chose the correct path.

Not that the task description is truthful.

Not that the memory itself is factually correct.

Not even that no useful project knowledge exists elsewhere.

What has been established is narrower:

> **The declared routing inputs were sufficient to resolve the routing policy defined by the current manifest.**

MemoryCustodian v0.11.0 separates this structural property from semantic correctness.

Protocol 0.7 defines routing states including `COMPLETE`, `INCOMPLETE`, `AMBIGUOUS`, and `INVALID`.

`COMPLETE` means the supplied valid inputs were sufficient to evaluate the applicable routing policy.

`INCOMPLETE` means the router is missing scope needed to resolve that policy. A common example is substantial work in a project with path-routed areas when the caller supplies neither paths nor an explicit area.

`INVALID` means the routing request or routing metadata violates the protocol rather than merely lacking scope.

`AMBIGUOUS` is reserved in Protocol 0.7 for a future versioned policy or documented compatibility behavior. The current schema does not use it as permission to fall back to natural-language guessing.

This distinction prevents a diagnostic from claiming more than it knows.

A structurally complete routing decision is not proof of semantic relevance.

A skipped module is not proof that the module is irrelevant.

A valid memory entry is not proof that its contents are factually correct.

Those are different layers of uncertainty. Combining them under one vague "confidence" score would make the system harder to reason about.

The router should report what it can actually establish.

Nothing more.

---

## 4. Every Module Needs a Disposition

Consider a context pack that contains:

```text
brief.md
constraints.md
decisions.md
areas/storage.md
```

A traditional retrieval interface might stop there.

Those are the loaded files.

But suppose the project also has:

```text
rules/output.md
profiles/docs.md
areas/auth.md
areas/frontend.md
```

What happened to them?

Were they not activated?

Did their path matchers fail?

Were they explicit-only modules that were never requested?

Did one match the routing policy but fail to exist?

Was its declaration invalid?

Without that information, the result is difficult to audit.

MemoryCustodian v0.11.0 therefore treats the routing result as more than a list of selected files.

With routing explanation enabled, every enabled module receives a disposition and a stable reason describing how it reached that state.

Protocol 0.7 uses dispositions including:

* `loaded`
* `skipped`
* `missing-required`
* `missing-optional`
* `invalid`

The exact reason matters.

"Not loaded" is not one condition.

A profile may be skipped because profiles are explicit-only and none was requested.

An area may be skipped because none of the supplied paths matched it.

An area may be unresolved because the task supplied no path scope at all.

A required shared module may be missing from disk.

A declaration may fail protocol validation.

These conditions should not collapse into the same invisible absence.

This is where stable reason codes become useful.

Human-readable prose can improve over time. CLI formatting can change. But a stable machine-readable reason allows tests, agents, integrations, and future tooling to distinguish routing outcomes without scraping explanatory sentences.

The result becomes inspectable at two levels.

Humans can ask:

> Why wasn't this module loaded?

Tools can ask:

> Which exact routing condition produced this disposition?

That makes routing behavior testable rather than merely observable.

### Budget omission is a different question

There is another important kind of absence.

A module may be correctly routed into the context pack, but one of its entries may not fit within the configured context budget.

That is not a routing skip.

The module was selected under the declared routing policy. The system simply could not include every complete entry within the bounded pack.

MemoryCustodian treats semantic entries atomically rather than truncating them into potentially misleading fragments.

v0.11.0 reports those entry-level budget omissions separately from module disposition.

This matters because:

> The router did not select this module.

and:

> The router selected this module, but this complete entry did not fit.

are fundamentally different explanations.

A trustworthy context system should preserve that distinction.

---

## 5. Strict Routing Before Substantial Work

Inspection and execution do not need the same safety threshold.

Suppose an implementation task is working in a repository with multiple path-routed areas.

The caller says only:

```text
task = implementation
```

but provides no planned paths and no explicit area.

The system may still know enough to provide some shared context.

It can load the project brief.

It can load root constraints that form the project-wide safety baseline.

That partial pack can be useful for inspection.

But should an agent begin changing code from it?

Probably not.

The missing scope could determine whether an authentication constraint, storage decision, frontend rule, or deployment restriction should have been loaded.

So MemoryCustodian distinguishes ordinary inspection from strict routing.

A non-strict `INCOMPLETE` read can expose the safely available context together with structured diagnostics describing what is missing.

That is useful when a developer is trying to understand or repair the routing request.

Strict routing takes a different position.

For substantial work, incomplete scope should stop the workflow rather than silently degrade into partial authority.

The principle is:

> **Partial context may be useful for diagnosis. It should not quietly become sufficient context for implementation.**

This boundary matters for coding agents because they are very good at continuing.

If a tool returns three valid memory files, an agent can easily proceed without asking whether a fourth file was supposed to exist.

A strict routing gate changes that behavior.

Before substantial planning, implementation, artifact generation, or history work that depends on scoped memory, the routing boundary must be sufficiently resolved.

This is not about making the system inflexible.

It is about preventing a dangerous ambiguity:

> No additional memory was needed.

versus:

> The system could not determine whether additional memory was needed.

Those are not the same statement.

Strict routing forces the difference into the open.

---

## 6. Private Context Without Private Authority

Not every useful memory belongs in Git.

A developer may prefer a particular output style.

One machine may have a local workflow convention.

A personal profile may be useful across sessions without being appropriate as shared project policy.

Putting that information directly into the repository creates unnecessary team-level state.

But keeping it entirely outside the project creates another risk: private memory can become an invisible authority layer that changes what the agent does.

MemoryCustodian v0.11.0 introduces local overlays to make this boundary explicit.

Local memory lives outside the repository.

It is bound to an explicit normalized project root.

A copied repository that happens to share the same public project identity does not automatically inherit the private overlay.

The local state uses private filesystem permissions on supported systems, and `--no-local` can produce a reproducible shared-only context pack.

But privacy does not grant authority.

That is the more important design rule.

Local preferences cannot override shared hard constraints.

They cannot override shared tombstones.

They cannot redefine project routing.

They cannot replace shared project decisions merely because they are closer to the current user.

And local state is not a secret-management system.

The precedence boundary remains asymmetric.

Shared project memory governs the project.

Local memory can personalize behavior inside those boundaries.

For example, a shared project constraint might say:

```text
All generated migration files must remain deterministic.
```

A local preference might say:

```text
Prefer concise explanations before showing code.
```

Those statements can coexist.

But a local preference saying:

```text
Ignore the deterministic migration requirement on this machine.
```

must not become stronger simply because it is private.

This separation lets project memory remain collaborative while still allowing individual workflows.

The local overlay can influence personal operating context.

It cannot privately rewrite what the project has already declared authoritative.

---

## 7. What the System Still Does Not Claim

Adding diagnostics creates a temptation to overstate what the system understands.

MemoryCustodian v0.11.0 intentionally avoids several such claims.

It does not claim complete natural-language contradiction detection.

Two memories can disagree semantically without sharing a structural identity that deterministic tooling can prove is conflicting.

It does not claim that a skipped module is irrelevant.

A skip means the declared routing policy did not activate that module under the supplied inputs. It is not a semantic judgment about every possible interpretation of the task.

It does not claim that `COMPLETE` means the context pack contains all knowledge that could possibly help.

Completeness describes the declared routing inputs and protocol policy, not omniscient retrieval.

It does not claim that a valid Evidence record proves a memory is factually true.

Evidence makes admission and provenance inspectable. It does not transform the CLI into a fact-checking system.

It does not automatically choose winners between structurally conflicting hard memories.

Protocol 0.7 can detect exact structural conditions such as duplicate ownership of the same `Scope + Subject + Facet`, Subject registry collisions, invalid exception relationships, and inconsistent reconciliation records.

But names, timestamps, prose similarity, Evidence counts, and file order do not automatically become authority.

If selected hard memory remains structurally unresolved, strict substantial reads can reject the pack rather than silently choosing a winner.

Merge-aware review extends the same principle across branches through an explicit, read-only merge-base comparison. It can surface structural collisions and concurrent hard-memory changes for review without claiming to reason over all Git history or automatically decide the correct resolution.

The identity and governance model behind those checks is covered in [Part 4](/2026/08/26/memory-custodian-remember/).

Finally, private local state does not become a stronger policy layer than shared repository memory.

These limitations are not gaps to hide behind a "smart retrieval" label.

They define the trust boundary.

A system becomes easier to reason about when it distinguishes:

* what it can determine mechanically
* what an agent can interpret semantically
* what still requires human judgment

---

## 8. A Reproducible Routing Example

The NightNotes fixture used throughout the MemoryCustodian project provides a small example.

NightNotes is intentionally incomplete.

Its current note store does not persist state across instances. The implementation task is to add persistent session storage.

The repository already remembers several relevant facts:

* persistence should use human-readable local JSON
* routine operation must work without network access
* the implementation should use only the Python standard library
* existing note files should remain human-readable
* SQLite was rejected for the current session store

The task prompt does not need to repeat those decisions.

A new coding-agent session can recover them from project memory.

With v0.11.0, however, we can ask a more precise question than:

> What memory does the planning task load?

We can inspect the routing decision itself.

From the MemoryCustodian repository:

```bash
scripts/memory-custodian read \
  --project-root examples/nightnotes-video-demo \
  --task planning \
  --explain
```

![NightNotes read explain output in MemoryCustodian v0.11.0]({{ "/img/posts/2026-09-15-memory-custodian-explainable-routing/memorycustodian-nightnotes-read-explain.svg" | relative_url }})

*Figure 2. A clean-environment NightNotes `read --explain` excerpt in MemoryCustodian v0.11.0. Output ends before the rendered context contents.*

The important result is not just the four loaded files.

The routing explanation tells us why each one appeared, whether anything configured was skipped or missing, whether the declared scope was sufficient, and whether complete entries were omitted by budget.

The NightNotes fixture has no enabled optional rules, profiles, or areas, so there is nothing optional to account for in this particular run.

That itself is an inspectable fact.

Now consider implementation work in a larger project with path-routed areas.

A more scoped call might look like:

```bash
memory-custodian read \
  --task implementation \
  --path cli/memory_custodian/read.py \
  --explain \
  --strict-routing
```

Here the path is not evidence that the selected memory is semantically correct.

It is an explicit routing input.

The manifest declares which areas, if any, that path activates.

The CLI evaluates that declaration.

The explanation exposes the resulting dispositions and reasons.

Strict routing determines whether the resulting pack is structurally approved for substantial work.

No hidden source-code scan is required.

No embedding score becomes authority.

No LLM needs to guess which project area probably matters.

That is the value of deterministic routing.

Not that it knows everything.

That developers can tell exactly what it decided.

---

## From Memory Retrieval to Context Accountability

Persistent agent memory is often evaluated by recall.

Did the system recover the decision?

Did it remember the constraint?

Did it prevent an old mistake from returning?

Those questions matter.

But a selective memory system needs another dimension of trust.

It should also be possible to ask:

* Why was this memory loaded?
* Why was that module not loaded?
* Were the routing inputs sufficient?
* Was an entry omitted because of routing or because of budget?
* Did private context influence the pack?
* Was selected hard memory structurally unresolved?
* Could another developer reproduce the same routing result?

These questions move the system from memory retrieval toward **context accountability**.

That is the larger change in MemoryCustodian v0.11.0.

Protocol 0.7 adds deterministic routing from explicit task and scope inputs, complete module dispositions, stable reason codes, routing completeness diagnostics, strict routing gates, private local overlays with shared-memory precedence, structural conflict review, migration boundaries, and stronger validation.

The release also expands the project's automated coverage from 151 tests to 393 unit, integration, migration, and determinism tests.

But the design principle behind those changes is simpler than the feature list:

> **If a system decides what an agent is allowed to remember for a task, that decision should itself be inspectable.**

A memory system should show what it loaded.

It should show what it skipped.

It should distinguish insufficient routing input from a module that simply did not activate.

It should distinguish routing omission from budget omission.

It should refuse to pretend that structural completeness proves semantic correctness.

And when it does not know enough to route safely, it should be able to say so before an agent begins substantial work.

The goal is not perfect retrieval.

It is a context boundary developers can understand.

---

## Key Takeaways

* **Persistent memory and active context are separate problems.** Storing useful knowledge does not mean loading all of it into every task.

* **Deterministic routing should depend on declared task and scope inputs rather than hidden semantic guesses.**

* **`COMPLETE` describes routing sufficiency, not semantic relevance, factual correctness, or perfect recall.**

* **Every enabled module should have an inspectable disposition and reason, while budget omissions should be reported separately.**

* **Strict routing prevents incomplete scope from silently becoming sufficient authority for substantial work.**

* **Private local memory can personalize context without overriding shared project constraints, tombstones, decisions, rules, or routing authority.**

* **Structural diagnostics should surface exact governance conflicts without using prose similarity, timestamps, or hidden heuristics to choose winners.**

* **A trustworthy memory system should explain not only what the agent received, but what governed context it did not receive and why.**

---

## Frequently Asked Questions

### Does deterministic routing mean semantic search is never useful?

No.

Semantic search can be useful for discovery across large or weakly structured corpora.

MemoryCustodian uses deterministic routing for governed project context because the activation boundary itself needs to be reproducible and inspectable.

The two approaches solve different problems.

### What does `COMPLETE` actually mean?

`COMPLETE` means the supplied routing inputs were sufficient to evaluate the routing policy defined by the current manifest.

It does not mean every loaded entry is semantically relevant.

It does not mean no useful information exists elsewhere in the repository.

And it does not mean the contents of the loaded memory are factually correct.

### What happens when routing is `INCOMPLETE`?

A normal inspection can still expose safely available context together with diagnostics describing the unresolved scope.

Strict routing is different.

For substantial work, it rejects a context pack whose routing boundary is not sufficiently resolved rather than silently treating partial context as complete authority.

### Can local memory override repository memory?

No.

Local overlays can personalize private preferences and workflows, but they cannot override shared hard constraints, tombstones, decisions, rules, or routing authority.

Local state is also not a secret store.

---

## Continue the Series

* [Start with the series overview](/2026/07/01/memory-custodian/)
* [Read Part 2: Why Project Memory Should Be Plain Text and Repo-Native](/2026/07/20/memory-custodian-tech-design/)
* [Read Part 3: Designing Memory That Can Safely Forget](/2026/07/21/memory-custodian-safe/)
* [Read Part 4: What Should a Coding Agent Be Allowed to Remember?](/2026/08/26/memory-custodian-remember/)
* [View MemoryCustodian on GitHub](https://github.com/waittim/MemoryCustodian)
* [View MemoryCustodian v0.11.0](https://github.com/waittim/MemoryCustodian/tree/v0.11.0)
* [Read the v0.11.0 release notes](https://github.com/waittim/MemoryCustodian/blob/v0.11.0/RELEASE-NOTES.md)

**Absence is part of the output.**
