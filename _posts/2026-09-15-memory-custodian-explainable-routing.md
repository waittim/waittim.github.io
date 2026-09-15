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

## A Bounded Context Pack Should Explain Its Omissions

When an agent starts an implementation task with four memory files injected into its prompt, the context looks clean and focused. The trouble is what remains invisible: why those specific four were selected, whether an important security rule was omitted because the task scope was too narrow, or whether an API constraint was dropped because the token budget filled up. A memory system that only reports what it loaded leaves open the most critical operational question: whether the resulting context pack is actually complete enough to safely write code.

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) is built around the premise that while stored memory can grow indefinitely, prompt context must stay strictly bounded. Once a system begins selectively loading files, omission becomes an active part of its behavior. A trustworthy router must make both sides of that selection visible—not by enumerating every file across the repository, but by accounting for the boundary it directly governs: manifest-managed modules, explicit policy exclusions, missing dependencies, and entries dropped due to token budgets. In v0.11.0, a bounded context pack must be deterministic, inspectable, and explicit about what it leaves out.

*For developers building governed context systems for coding agents. Implementation details in this article reflect MemoryCustodian v0.11.0 and Protocol 0.7.*

---

## 1. Persistent Memory Still Has a Selection Problem

Persistent memory solves session amnesia, but it immediately introduces a selection problem. A mature repository accumulates dozens of disparate facts over time: storage subsystems requiring human-readable JSON, authentication compatibility workarounds, deployment provider exclusions, code conventions, rejected state libraries, and personal workflow preferences. While all of these facts may be worth recording, dumping the entire store into every session recreates the very problem memory was meant to solve: bloated prompts where routine tasks waste context on irrelevant background.

The solution is routing—preserving a large body of project knowledge while activating only a task-specific subset. In this framework, memory is what the project preserves, while context is what the current task actually receives. Once selective routing exists, however, the router itself becomes part of the correctness boundary. Consider an agent modifying an authentication endpoint. If the project maintains an authentication-specific constraint, but the router omits it because the task was inadequately scoped, the resulting context pack will still look authoritative. The agent follows every loaded instruction faithfully, yet introduces a subtle regression by violating a constraint it was never given.

Selective memory therefore requires more than basic retrieval; it requires **selection accountability**. Developers must be able to inspect both sides of the ledger: which modules were loaded, and exactly why omitted modules were left out. Omission is where silent architectural bugs hide.

---

## 2. Routing Should Use Declared Inputs, Not Hidden Guesses

A context router could attempt to infer relevance in several ways: parsing the prompt for keywords, embedding the task description to compute cosine similarity against stored memories, scanning the working tree to guess the active subsystem, or delegating file selection to an LLM. While probabilistic heuristics are fine for exploratory search, they are too fragile for an architectural routing boundary. If two runs with the same prompt load different constraints because a model interpreted the task differently, debugging regressions becomes guesswork.

MemoryCustodian v0.11.0 takes a deterministic approach based entirely on declared inputs:
1. **Canonical Task Category:** Declared explicitly (e.g., `planning`, `implementation`, `review`).
2. **Path Scope:** The files planned, touched, or inspected.
3. **Explicit Overlays:** Specific rules, profiles, or subsystem areas requested by the caller.

Given the same manifest and identical declared inputs, the routing outcome is guaranteed to be reproducible. The router never scans the codebase to guess a subsystem, computes no fuzzy semantic scores, and relies on no background LLM calls to rank rules by perceived relevance. Path patterns activate area modules, task categories activate standard rules, and root constraints automatically form the baseline safety envelope.

A deterministic router does not claim to understand a task better than an intelligent retrieval model. It makes a narrower, auditable guarantee: given these declared inputs and this manifest, this is the exact context the project configuration requires. When a task provides insufficient scope to select between path-routed subsystems, the router does not attempt to compensate by guessing; it reports the input as structurally incomplete, keeping operational uncertainty explicit.

I covered the broader distinction between routing and retrieval in [Part 2](/2026/07/20/memory-custodian-tech-design/). v0.11.0 makes the omission side of that boundary explicit.

![Explainable context routing in MemoryCustodian]({{ "/img/posts/2026-09-15-memory-custodian-explainable-routing/memorycustodian-explainable-routing.svg" | relative_url }})

*Figure 1. Explainable routing accounts for both selected context and explicit omissions. The manifest resolves declared task and scope inputs deterministically; completeness and budget diagnostics remain separate from semantic relevance.*

---

## 3. Complete Does Not Mean Semantically Correct

The term *complete* can easily be misunderstood in a memory system. Suppose a task declares that it will modify `cli/memory_custodian/read.py`. The manifest contains an area rule matching that path, the canonical task is supported, root constraints exist, and all optional modules resolve without error. At this point, the router marks the routing state as complete.

Crucially, marking a routing request complete does not prove that every loaded memory is semantically relevant, that the developer chose the right path, or that the memory entries themselves are factually accurate. It establishes something narrower and much more useful: the declared routing inputs were sufficient to evaluate the routing policy defined by the manifest.

Protocol 0.7 formalizes this by separating structural completeness from semantic judgment into explicit routing states:

* `COMPLETE`: The supplied inputs were sufficient to resolve all applicable manifest rules.
* `INCOMPLETE`: The router lacks the required scope to evaluate policy (e.g., modifying files in a path-routed repository without providing either file paths or an explicit area).
* `INVALID`: The request or underlying manifest violates the protocol schema.
* `AMBIGUOUS`: Reserved for versioned fallback policies; the router refuses to guess using natural language.

Separating these concerns keeps diagnostics honest. A structurally complete decision is not proof of relevance, just as a skipped module is not proof of irrelevance. Collapsing these distinct failure modes into a single heuristic confidence score would only obscure why an agent received what it did. The router reports exactly what it can verify.

---

## 4. Every Module Needs a Disposition

When an agent loads `brief.md`, `constraints.md`, `decisions.md`, and `areas/storage.md`, traditional tools simply list those four files. But if the repository also contains `rules/output.md`, `profiles/docs.md`, and `areas/auth.md`, developers face an immediate auditing problem: Why weren't the other modules included? Did their path matchers fail? Was a required module missing from disk? Or was an explicit profile simply not requested?

MemoryCustodian v0.11.0 accounts for every enabled module in the manifest by assigning it an explicit disposition:

* `loaded`: Successfully activated and injected into context.
* `skipped`: Evaluated by policy and intentionally omitted (e.g., path mismatch, unrequested profile).
* `missing-required`: Required by policy or task baseline, but not found on disk.
* `missing-optional`: Optional module matched by policy, but not found on disk.
* `invalid`: The module file or metadata failed protocol validation.

"Not loaded" is not a single state. An unrequested profile, an unmatched path pattern, an unresolved task scope, and a missing file on disk represent entirely different failure modes.

Instead of relying on unstable log strings, Protocol 0.7 attaches stable machine-readable reason codes to every disposition. This enables CI checks, test suites, and downstream agent integrations to verify routing behavior deterministically without scraping prose:

* Humans can inspect: *Why wasn't this module loaded?*
* Tools can verify: *Which exact routing rule produced this disposition?*

### Distinguishing Routing Skips from Budget Omissions

There is another critical absence that traditional retrieval obscures: budget exhaustion.

A module may be correctly selected under the active policy, but one of its entries may exceed the prompt's configured token budget. MemoryCustodian preserves atomic entries—it refuses to truncate markdown sections into broken, misleading snippets. When context budget runs out, full entries are omitted, and v0.11.0 reports them in a dedicated `budget_omissions` diagnostic.

This keeps two fundamentally different explanations distinct: *The router did not select this module* versus *The router selected this module, but a complete entry exceeded the context budget*. Preserving that distinction is essential for debugging why an agent missed a specific constraint.

---

## 5. Strict Routing Before Substantial Work

Inspection and execution demand different safety thresholds. Suppose an implementation task targets a repository with multiple path-routed areas, but the caller specifies only `task = implementation` without providing file paths or an explicit area. The system can still safely assemble a partial context pack—loading the project brief and root constraints that establish baseline security. While this partial pack is useful for inspection and debugging, allowing an agent to start writing code from it is dangerous: the missing path scope might omit an authentication constraint, storage decision, or deployment rule.

To prevent silent failures, MemoryCustodian separates exploratory reads from strict execution gates:
* **Non-strict reads (`memory-custodian read --explain`):** Expose available context alongside structured diagnostics detailing which path or area inputs remain unresolved. This helps developers diagnose routing requirements.
* **Strict routing (`--strict-routing`):** Refuses to produce an active context pack if routing state is `INCOMPLETE`. If a task lacks the scope required to evaluate manifest rules, execution halts.

Partial context is useful for diagnosis, but it must never silently become sufficient authority for code generation. Coding agents are notoriously compliant: if a tool provides three valid constraint files, the agent will cheerfully proceed without questioning whether a fourth was omitted. A strict routing gate stops this failure mode before code is written, ensuring that *“no additional memory was required”* is never confused with *“the system lacked the scope to know if additional memory was required.”*

---

## 6. Private Context Without Private Authority

Not all useful context belongs in Git. Individual developers have personal preferences—concise terminal outputs, local tool paths, or specific testing workflows—that should persist across sessions without polluting the shared repository. Conversely, keeping personal preferences completely untracked creates shadow policies that invisibly alter agent behavior across machines.

MemoryCustodian v0.11.0 addresses this with local overlays. Stored outside the repository and tied to a normalized project path, local memory personalizes the agent’s operating environment without entering version control. To ensure CI reproducibility, passing `--no-local` strips all private overlays, yielding an identical context pack across any environment.

Critically, privacy never grants authority. The precedence model is strictly asymmetric:

* **Shared project memory governs policy:** Shared constraints, architectural decisions, tombstones, and manifest routing rules always take absolute precedence.
* **Local overlays customize personal preferences:** A private setting can dictate tone (*"prefer concise explanations before code"*), but it can never override a shared project invariant (*"all migrations must remain deterministic"*).

Local overlays make tooling adaptable to individuals without allowing private configuration to quietly subvert team-level architectural guarantees.

---

## 7. What the System Does Not Claim

Adding diagnostics creates a temptation to overstate what the tooling understands. MemoryCustodian v0.11.0 is explicit about its boundaries:

* **No semantic contradiction guessing:** Two rules can logically conflict in prose without sharing a machine-detectable Subject ID or Facet collision. Protocol 0.7 catches exact structural collisions (such as duplicate ownership of `Scope + Subject + Facet`), but it does not claim to parse natural language nuance.
* **Skipped does not mean irrelevant:** A skipped disposition means only that declared routing inputs did not activate the module. It is a statement about manifest evaluation, not task semantics.
* **`COMPLETE` is not omniscience:** Completeness confirms that supplied inputs satisfied manifest rules. It does not promise that the resulting pack contains every piece of knowledge that could conceivably help.
* **Evidence is not a truth engine:** Evidence records answer *why an entry was admitted*, not *whether it is eternally factual*. It makes provenance auditable without pretending to be an infallible fact-checker.
* **No automatic tie-breaking:** When two active constraints structurally collide, the router does not use heuristics, timestamps, or file ordering to guess a winner. Under strict routing, it halts and demands human resolution.

These constraints are not limitations to obscure behind marketing claims. They define the trust boundary: deterministic tools enforce structure and flag ambiguity, language models reason over provided context, and human engineers make the authoritative trade-offs.

---

## 8. A Reproducible Routing Example

The NightNotes fixture used throughout the MemoryCustodian project provides a concrete example. NightNotes is intentionally incomplete: its current note store does not persist state across instances, and the implementation task is to add persistent session storage.

The repository already remembers several relevant facts:
* persistence should use human-readable local JSON
* routine operation must work without network access
* the implementation should use only the Python standard library
* existing note files should remain human-readable
* SQLite was rejected for the current session store

The task prompt does not need to repeat those decisions because a new coding-agent session can recover them from project memory. With v0.11.0, however, we can inspect the routing decision itself rather than merely asking what memory was loaded:

```bash
scripts/memory-custodian read \
  --project-root examples/nightnotes-video-demo \
  --task planning \
  --explain
```

![NightNotes read explain output in MemoryCustodian v0.11.0]({{ "/img/posts/2026-09-15-memory-custodian-explainable-routing/memorycustodian-nightnotes-read-explain.svg" | relative_url }})

*Figure 2. A clean-environment NightNotes `read --explain` excerpt in MemoryCustodian v0.11.0. Output ends before the rendered context contents.*

The important result is not just the four loaded files. The routing explanation details why each one appeared, whether anything configured was skipped or missing, whether the declared scope was sufficient, and whether complete entries were omitted by budget. Because the NightNotes fixture has no enabled optional rules, profiles, or areas, there is nothing optional to account for in this run—which is itself an inspectable fact.

Now consider implementation work in a larger project with path-routed areas. A more scoped call provides explicit routing inputs:

```bash
memory-custodian read \
  --task implementation \
  --path cli/memory_custodian/read.py \
  --explain \
  --strict-routing
```

Here, passing the target file path provides an explicit routing input rather than probabilistic evidence. The manifest determines which subsystem areas match that path pattern, the CLI evaluates the match, and the explanation reports the resulting dispositions. Under `--strict-routing`, the system verifies that all required scope is present before allowing code generation to start.

Because routing relies on declared inputs, file selection requires no speculative code scanning, embedding distance thresholds, or LLM guesses. Its value is operational clarity: any engineer or automated test can trace precisely why a rule was injected or omitted.

---

## From Memory Retrieval to Context Accountability

Most discussions of coding-agent memory focus exclusively on recall: Did the agent remember a prior decision? Did it avoid repeating a rejected design?

While recall matters, production workflows require precision and transparency. A dependable context system must answer what was omitted, whether inputs were sufficient to evaluate policy, whether entries were dropped due to token limits, and whether another developer would get the same result.

Protocol 0.7 addresses this by shifting focus from passive retrieval to **context accountability**:

* Deterministic routing from explicit task and scope inputs.
* Complete module dispositions with stable, machine-readable reason codes.
* Scope completeness diagnostics paired with strict execution gates.
* Private local overlays strictly subordinated to shared project constraints.
* Structural conflict detection across concurrent Git branches.

A dependable memory architecture must account for omissions just as rigorously as inclusions. It must distinguish missing scope from inactive modules, separate routing decisions from budget limits, refuse to conflate structural completeness with factual truth, and fail loudly when inputs are insufficient to proceed safely.

---

## Key Takeaways

* **Persistent memory and active context are separate problems:** Storing useful knowledge does not mean loading all of it into every task.
* **Deterministic routing depends on declared inputs:** Task and path scope determine context rather than hidden semantic guesses.
* **`COMPLETE` describes routing sufficiency:** It proves manifest rules were resolved, not that context is semantically omniscient or factually infallible.
* **Every module has an inspectable disposition:** Omissions are categorized into explicit policy skips, missing dependencies, or budget limits.
* **Strict routing prevents silent failures:** Unresolved scope halts code generation rather than allowing the agent to proceed on partial authority.
* **Local overlays never override shared policy:** Private preferences cannot supersede repository invariants or tombstones.

---

## Frequently Asked Questions

### Does deterministic routing mean semantic search is never useful?

No. Semantic search remains valuable for exploratory discovery across large, sprawling codebases where queries are fuzzy and boundaries are fluid. MemoryCustodian uses deterministic routing specifically for governed project context, where activation rules must be reproducible, auditable in Git, and testable in CI.

### What does `COMPLETE` actually mean?

`COMPLETE` indicates that the provided inputs were sufficient to evaluate all manifest rules for the requested task. It is a structural diagnostic, not a semantic guarantee—it does not claim that loaded memories are factually infallible or that no other useful code exists.

### What happens when routing is `INCOMPLETE`?

During exploratory inspection (`--explain`), the tool returns available baseline context along with diagnostics identifying unresolved paths or areas. Under `--strict-routing`, however, execution halts to prevent the agent from writing code with partial authority.

### Can local memory override repository memory?

No. Local overlays allow developers to configure personal preferences (such as terminal formatting or local tools), but they can never override shared constraints, architectural decisions, tombstones, or manifest routing rules.

---

## Continue the Series

* [Start with the series overview](/2026/07/01/memory-custodian/)
* [Read Part 2: Why Project Memory Should Be Plain Text and Repo-Native](/2026/07/20/memory-custodian-tech-design/)
* [Read Part 3: Designing Memory That Can Safely Forget](/2026/07/21/memory-custodian-safe/)
* [Read Part 4: What Should a Coding Agent Be Allowed to Remember?](/2026/08/26/memory-custodian-remember/)
* [View MemoryCustodian on GitHub](https://github.com/waittim/MemoryCustodian)
* [View MemoryCustodian v0.11.0](https://github.com/waittim/MemoryCustodian/tree/v0.11.0)
* [Read the v0.11.0 release notes](https://github.com/waittim/MemoryCustodian/blob/v0.11.0/RELEASE-NOTES.md)
