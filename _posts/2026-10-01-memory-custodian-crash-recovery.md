---
layout: post
title: "A Memory System Should Survive an Interrupted Write"
subtitle: "Transactional crash recovery, conditional rollback, and staged migration in MemoryCustodian v0.12.0"
date: 2026-10-01
updated: 2026-10-01
author: Zekun Wang
description: "Why multi-file agent-memory mutations require repo-external transaction journaling, conditional rollback, audit blockers, and staged protocol migration."
image: /img/headers/post-bg-unix-linux.jpg
series: MemoryCustodian Design Series
series_nav_title: Crash Recovery
series_order: 6
header-img: img/headers/post-bg-unix-linux.jpg
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

## Multi-File Mutations Require Transactional Durability

When a coding agent changes persistent project memory, the operation often spans several files. A governance update may rewrite structured entries, update Subject or reconciliation state, change manifest metadata, and touch a bound local overlay. If the process exits halfway through, each file that was already replaced may still be perfectly valid on its own while the project as a whole is left between two intended states.

[MemoryCustodian](https://github.com/waittim/MemoryCustodian) has used atomic file replacement for managed writes since earlier releases: write the new contents separately, flush them, and replace the destination atomically. That protects readers from truncated files, but the guarantee stops at the file boundary. If an operation needs to change A, B, C, and D, a crash after B still leaves a mixture of old and new state.

Protocol 0.8, introduced in MemoryCustodian v0.12.0, adds a transaction layer for this failure mode. Multi-file mutations are journaled in private repo-external state, interrupted transactions can be inspected and explicitly completed or rolled back, and recovery refuses to overwrite files that have changed outside the transaction. The filesystem remains the source of truth; the journal records enough information to recover MemoryCustodian's own interrupted writes without reconstructing intent from timestamps, diffs, or prose.

*For developers building durable transaction, recovery, and migration engines for coding agents. Implementation details in this article reflect MemoryCustodian v0.12.0 and Protocol 0.8.*

---

## 1. Atomic Files Do Not Make an Atomic Operation

Suppose one mutation needs to update four pieces of state:

```text
1. Rewrite a managed entry
2. Update related structural state
3. Rewrite another managed entry
4. Commit updated protocol authority
```

Atomic replacement guarantees that step 1 does not leave half a Markdown file behind. It says nothing about whether steps 2 through 4 happen. A process that dies after step 2 can therefore leave two valid new files next to two valid old ones. The failure is not a corrupted byte stream; the collection simply no longer represents either the pre-mutation state or the intended post-mutation state.

Earlier MemoryCustodian releases already had mutation plans and atomic target replacement. Protocol 0.8 adds an operation-level record around those writes. Any mutation that can change more than one managed target is executed through the shared transaction engine, including initialization and repair, enable/link, add and promotion, compaction, forget and purge, Subject and reconciliation governance, staged migration, schema conversion, and local reset.

![Transaction lifecycle and recovery in Protocol 0.8]({{ "/img/posts/2026-10-01-memory-custodian-crash-recovery/transaction-lifecycle-and-recovery.svg" | relative_url }})

*Figure 1. Protocol 0.8 records multi-file mutations in private repo-external state. Interrupted transactions can be completed or rolled back only while the recorded recovery conditions still hold.*

A transaction moves through `planned`, `prepared`, and `committing` on the normal path to `committed`. An interruption can leave it in `failed`, after which recovery records whether the transaction will be completed or rolled back before changing another target. A journal that has not reached a safe terminal state remains visible to transaction audit and blocks new mutations.

---

## 2. The Journal Records State, Not Meaning

Recovery does not try to infer what a previous command probably intended from Git diffs, modification times, or nearby prose. Protocol 0.8 persists the operation before protected outputs are prepared, then records enough information to recognize both sides of each target transition.

The journal uses transaction schema 1. At a high level, it records an opaque transaction ID, the command and Plan ID, the current phase, the project binding, target metadata, base and output digests, target existence, file modes where applicable, and locators for protected backup or prepared artifacts.

Transaction IDs are opaque 32-character hexadecimal values. Target IDs are mechanical identifiers rather than semantic names. Journal metadata is not allowed to contain user topics, removed entry bodies, secret previews, or reversible encodings of them. If rollback requires the original bytes, those bytes are stored as separate protected recovery artifacts rather than embedded in the journal metadata.

The journal lives under MemoryCustodian's repo-external private state root rather than under `docs/memory/`. On POSIX systems, private-state directories are maintained with mode `0700` and private regular files with mode `0600`. Normal context loading does not treat this state as project memory.

With the journal available, recovery can compare each target with two recorded states: its base and its prepared output. There is no need to decide which version of a decision looks newer or which text seems more plausible. If the current filesystem still matches the transaction's recorded conditions, the operation can proceed toward a known terminal state; if not, automated recovery stops.

---

## 3. Conditional Rollback Prevents Recovery from Deleting New Work

Rollback becomes dangerous when the repository changes after the original process stops.

Assume a transaction replaces file A and then crashes before replacing file B. A developer notices the problem and edits A manually. If recovery later restores A from its saved pre-state simply because the original operation never committed, the rollback destroys work that happened after the failure.

Protocol 0.8 checks the current target against the transaction record before either completing or rolling back:

| Current target | Matches base | Matches prepared output | Recovery |
|---|---:|---:|---|
| Untouched | Yes | No | Completion may proceed |
| Already updated | No | Yes | Completion or rollback may proceed |
| Externally modified | No | No | Stop with a blocker |

Content digests are only part of the check. Recovery also validates target existence, expected mode semantics where supported, safe path resolution, symlink state, and the integrity of protected transaction artifacts. A missing target that was expected to exist, an unexpected digest, or a symlink substituted for a regular file is enough to stop automatic recovery.

Once recovery chooses a direction, that choice is durable. A committed journal can only finish completion and cleanup; a rolled-back journal can only finish rollback cleanup. Retrying recovery cannot silently switch from one outcome to the other.

This is more conservative than restoring a backup directory wholesale. MemoryCustodian rewrites only state that can still be tied to the interrupted transaction. Anything that has drifted outside that model is left for manual review.

---

## 4. Recovery Data Stays Out of Agent Context

The separation between transaction state and managed memory becomes especially important for destructive operations.

A hard forget or purge may remove information from active memory while recovery still temporarily needs the pre-operation bytes in case the mutation must be rolled back. Storing those bytes inside the repository, exposing them through `audit --format json`, or allowing normal routing to discover them would create another persistence path for content the operation was trying to remove.

Protocol 0.8 keeps protected rollback bytes outside the reader and public-output surfaces. Transaction metadata contains only the identifiers, locators, modes, and digests needed to reason about the mutation; protected artifacts containing pre-state bytes remain private recovery material. After completion or rollback reaches a verified terminal state, the transaction engine removes those artifacts.

Cleanup is checked rather than treated as a blind recursive delete. Before removing protected state, a committed transaction verifies that committed targets still match their recorded outputs, while a rolled-back transaction verifies that restored targets still match their bases. Local-reset recovery also tracks directory identity and refuses to remove directories that have gained unexpected children.

The same limits apply to erasure more generally. MemoryCustodian can control what remains available through its managed memory surfaces, but it does not rewrite Git history or revoke clones, forks, backups, caches, or exports. Protocol 0.8 exposes those limits through the same versioned `ErasureScope` used by forget and recovery operations. A bounded `no-reachable-copy-detected` history result describes the inspected repository state; it is not evidence that no other copy exists.

---

## 5. Transaction State Is Part of Audit

Private recovery state would be difficult to operate safely if it were invisible to normal inspection, so v0.12.0 includes transaction health in the audit model.

`memory-custodian audit --transactions` inspects transaction state and reports unfinished, malformed, unsupported, orphaned, symlinked, or otherwise unsafe journals. These conditions are emitted as `BLOCKER` findings rather than warnings.

| Code | Meaning |
|---|---|
| `MC-TRANSACTION-001` | Unfinished transaction or pending terminal cleanup |
| `MC-TRANSACTION-002` | Malformed or unsupported transaction journal |
| `MC-TRANSACTION-003` | Orphan transaction state |
| `MC-TRANSACTION-004` | Unsafe or symlinked transaction state |

A blocker produces overall status `FAIL` and exit class `blocker`. Recovery uses the opaque transaction ID reported by audit:

```bash
memory-custodian recover --transaction-id <OPAQUE_ID>
memory-custodian recover --transaction-id <OPAQUE_ID> --complete
memory-custodian recover --transaction-id <OPAQUE_ID> --rollback
```

The public machine interface is separate from the private journal. Commands using `--format json` return output schema 1, with stable top-level fields for the command result and structured findings. An unfinished transaction can appear in a result shaped like this:

```json
{
  "output_schema_version": 1,
  "command": "audit",
  "protocol_version": "0.8",
  "status": "FAIL",
  "exit_class": "blocker",
  "data": {
    "audit_schema_version": 1,
    "rendered_text": "..."
  },
  "findings": [
    {
      "code": "MC-TRANSACTION-001",
      "severity": "BLOCKER",
      "path": "private/transactions",
      "entry_id": null,
      "message": "Unfinished transaction requires recovery.",
      "remediation": "Run `memory-custodian recover`.",
      "details": {
        "transaction_id": "<OPAQUE_ID>",
        "transaction_state": "unfinished"
      }
    }
  ],
  "disclaimers": []
}
```

Execution plans, recovery journals, and public results serve different purposes. Plans may contain protected information needed to rebuild a mutation, journals retain the state needed for crash recovery, and the public result model remains sanitized and stable for scripts and agent adapters. Keeping those representations separate prevents private recovery details from becoming part of the external API.

---

## 6. Migration Uses the Same Recovery Model

Protocol migration is one of the clearest cases where a single implicit rewrite is insufficient. Moving a project from Protocol 0.5, 0.6, or 0.7 to Protocol 0.8 can require schema conversion across managed entries, validation of Subject and Facet ownership, local-overlay migration, and finally a change to the protocol metadata that controls how future reads interpret those files.

v0.12.0 splits that process into three separately confirmed stages.

![Staged migration to Protocol 0.8]({{ "/img/posts/2026-10-01-memory-custodian-crash-recovery/staged-migration-protocol-0-8.svg" | relative_url }})

*Figure 2. Migration keeps source capture, semantic canonicalization, and the final protocol authority change as separate confirmed stages. Bound local overlays participate in the same schema transition.*

`prepare` captures the source protocol and entry schema, project binding, normalized root, source digests, and bound local-overlay state in protected repo-external migration state. Shared protocol metadata remains unchanged, so preparing a migration does not cause existing readers to interpret the project under the target schema.

`canonicalize` is repeatable and preview-first. It can convert mechanically unambiguous legacy units, but semantic fields still require explicit input where the old representation does not contain enough information. The migrator does not synthesize Evidence, infer Subject equivalence from prose, guess Facets, or manufacture reconciliation records. Ambiguous units remain unchanged and continue to block finalization.

`finalize` rebuilds and validates the migration against the current source files. It requires canonical active entries, valid Subject and Facet relationships, and the absence of audit errors, blockers, or unresolved canonicalization work. The target Entry schema 3 representation, any bound local-overlay rewrites, and the protocol update are then applied through one transaction. The `protocol_version: 0.8` and `entry_schema_version: 3` authority in `manifest.md` is committed last.

Committing the authority metadata last avoids a particularly bad migration failure mode: a repository claiming Protocol 0.8 while some of its entries are still encoded according to an older schema. If finalization is interrupted, the same transaction audit and recovery machinery handles the resulting state instead of asking the next run to infer how far the migration progressed.

---

## 7. One CLI Contract Across Agent Adapters

Codex, Claude Code, Gemini, and the generic adapter all sit above the same CLI contract in v0.12.0. Their integration files differ, but manifest-first routing, explicit task and scope inputs, conflict gates, recovery behavior, JSON output, and erasure language are defined below the adapter layer.

When an agent runtime such as Claude Code, Codex, or Gemini is interrupted mid-turn—whether through token cutoffs, network timeouts, or process cancellation—the adapter does not need to synthesize custom recovery heuristics. Because transaction logging and audit blockers live below the adapter layer, any subsequent invocation under any agent runtime immediately encounters the same deterministic blocker finding (`MC-TRANSACTION-001`). The engine fails closed, ensuring that no agent continues mutating project memory on top of a half-applied transaction.

The repository includes offline fixtures that run the same canonical commands under each adapter label and compare expected fields and payload stability. These checks are useful for detecting adapter drift, but they are not equivalent to launching four external agent runtimes and benchmarking their behavior end to end. v0.12.0 records a separate current-protocol Codex startup smoke rather than treating the static contract fixture as live-agent evidence.

Keeping that boundary explicit has become increasingly useful as MemoryCustodian grows. The shared CLI contract is deterministic and testable in CI; behavior above that contract remains a separate runtime question.

---

## 8. Scope of the Transaction Model

Protocol 0.8 does not provide general database ACID semantics. MemoryCustodian cannot prevent an unrelated editor, Git command, or foreign process from modifying files while an interrupted transaction exists, nor does it attempt semantic merge resolution when that happens.

Its recovery guarantee is narrower: MemoryCustodian records its own multi-file transition, recognizes whether targets still match the recorded base or prepared state, and refuses to overwrite anything that has drifted outside those states.

That changes the failure mode substantially. Before Protocol 0.8, an interrupted multi-file operation could leave the next process with a set of individually valid files and no durable record of how they got there. In v0.12.0, the unfinished operation remains identifiable, auditable, and recoverable as long as the filesystem still satisfies the recorded recovery conditions.

Persistent agent memory makes interrupted writes more consequential because their results survive the agent session that produced them. The recovery layer in Protocol 0.8 is built around that constraint: after a mutation stops halfway through, the next run can determine what MemoryCustodian was doing without reconstructing intent, and recovery does not erase newer work merely to make the old transaction disappear.

---

## Key Takeaways

* **Atomic files do not make an atomic operation:** Safely replacing individual files still leaves multi-file agent mutations vulnerable to partial completion.
* **Match state, do not infer intent:** Recovery compares recorded content digests and target existence instead of guessing developer intent from diffs, prose, or commit history.
* **Conditional rollback protects external work:** Automatic recovery halts with a blocker if any target has drifted outside the transaction’s recorded base or prepared states.
* **Recovery state stays out of prompt context:** Transaction journals and pre-state recovery artifacts reside in repo-external private storage (`0700`/`0600`), preventing them from leaking into agent prompts.
* **Staged migration prevents schema split-brain:** Migration isolates source capture, semantic canonicalization, and atomic finalization, committing protocol authority in `manifest.md` strictly last.
* **Audit-first blockers:** Unfinished transactions produce `BLOCKER` audit findings and `status: FAIL`, preventing new mutations until explicitly resolved.

---

## Frequently Asked Questions

### Why not store the transaction journal inside `docs/memory/` or Git?

If transaction journals were stored inside the repository, unfinished recovery state or sensitive pre-state bytes could be inadvertently ingested into agent prompt context or committed into Git history. Keeping journals in repo-external private state (`0700` directories, `0600` files) isolates operational recovery from project memory.

### What happens if a developer edits a file while an interrupted transaction is pending?

Recovery performs conditional checks before touching disk. If a target file matches neither the transaction's recorded base state nor its prepared output state, automated recovery refuses to proceed. It reports an audit blocker (`MC-TRANSACTION-001`) and leaves the conflict for human review, ensuring recovery never overwrites external work.

### Does Protocol 0.8 provide full ACID database transactions?

No. Protocol 0.8 does not provide cross-process locking or general database ACID semantics. It guarantees that MemoryCustodian's own multi-file mutations are journaled, auditable, and recoverable between known states, refusing to overwrite external drift.

### Why does migration commit protocol authority in `manifest.md` as the very last step?

Committing authority last prevents readers from evaluating partially migrated entries against a newer schema. If finalization fails midway through, the project is still recognized under its source protocol, allowing transaction recovery to resolve the interruption safely.

---

## Continue the Series

* [Start with the series overview](/2026/07/01/memory-custodian/)
* [Read Part 2: Why Project Memory Should Be Plain Text and Repo-Native](/2026/07/20/memory-custodian-tech-design/)
* [Read Part 3: Designing Memory That Can Safely Forget](/2026/07/21/memory-custodian-safe/)
* [Read Part 4: What Should a Coding Agent Be Allowed to Remember?](/2026/08/26/memory-custodian-remember/)
* [Read Part 5: A Memory System Should Explain What It Did Not Load](/2026/09/15/memory-custodian-explainable-routing/)
* [View MemoryCustodian on GitHub](https://github.com/waittim/MemoryCustodian)
* [View MemoryCustodian v0.12.0](https://github.com/waittim/MemoryCustodian/tree/v0.12.0)
* [Read the v0.12.0 release notes](https://github.com/waittim/MemoryCustodian/blob/v0.12.0/RELEASE-NOTES.md)

