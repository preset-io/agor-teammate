# Skill: Amazon-Style Correction of Errors (COE) Authoring

**When to use:** Write, rewrite, migrate, or grade any production-incident postmortem. This is the canonical standard. Pair it with [[postmortem-from-p0-p1]] when evidence must first be reconstructed from incident and release channels.

**Role and objective:** Soraya acts as an SRE/postmortem investigator. Produce blameless Amazon-style Correction of Errors (COE) documents that explain exactly what happened; the technical failure mechanism; the engineering and organisational escape mechanisms; why safeguards did not prevent, contain, detect, diagnose, or accelerate recovery; and which concrete changes materially reduce recurrence or related failures. The objective is systemic improvement, never attribution of blame.

## Non-negotiable rules

### One incident per document

Every production incident has its own COE. Never combine incidents merely because they occurred on the same day, affected the same release/subsystem, generated related pages, or share a defect. Incident identity follows the distinct production event and customer/system impact, not root-cause uniqueness.

If a source document contains multiple incidents, split it. Cross-reference related COEs and repeat shared context where useful. Preserve every substantive source fact somewhere in the resulting documents. A single fix may legitimately appear in multiple COEs.

### Preserve historical evidence

When rewriting or migrating an existing postmortem:

- Never silently discard evidence or overwrite investigation history.
- Preserve timestamps, corrections, retractions, uncertainty, links, metrics, logs, PRs, tickets, people involved, mitigation attempts, unsuccessful actions, and discarded hypotheses.
- Never promote an old hypothesis to fact or leave a superseded hypothesis as the current cause.
- Preserve the distinction between **quiet**, **mitigated**, **recovered**, and **fixed**.
- Retain superseded conclusions under **Investigation History / Retracted Hypotheses**, including the hypothesis, original supporting evidence, actions it prompted, disproving evidence, correction time if known, and investigation cost/lesson when meaningful.
- Before publication, perform a preservation audit. Every substantive source fact must be (A) retained, (B) moved to a related incident's COE during a split, or (C) explicitly classified as duplicate/non-substantive formatting.

### Evidence and confidence discipline

Separate evidence from interpretation. Support important claims with logs, traces, metrics, source, commits/PRs, deployments, Sentry, Datadog, Shortcut, Slack, release metadata, or reproducible tests. Use **CONFIRMED**, **STRONGLY SUPPORTED**, **PLAUSIBLE**, **UNCONFIRMED**, and **DISPROVEN** where useful. A symptom-compatible hypothesis is not automatically a cause. Disproven hypotheses remain operational knowledge.

Capture expiring evidence in the COE: paste query windows and values, representative searchable log lines, and stable screenshots/artifacts. Keep live links as labelled pointers.

## Incident rating

Assign both live priority (**P0–P4**) and retrospective **Impact × Severity**. They are independent. Rate peak observed impact, not average or worst imaginable impact; round up when uncertain and explain. Preserve previous ratings if later corrected.

| Impact | Breadth |
|---|---|
| **A — Global** | Most/all workspaces, regions, or shared control plane |
| **B — Segment** | Region, cluster, customer tier, or large cohort |
| **C — Localized** | A few workspaces/single customer, or one non-critical feature broadly |
| **D — Isolated/Internal** | One workspace, internal tooling, staging/pre-prod |

| Severity | Depth |
|---|---|
| **1 — Critical** | Complete outage, data loss/corruption, or confirmed security/privacy breach; no workaround |
| **2 — Major** | Core workflow unusable; no acceptable workaround |
| **3 — Moderate** | Degraded/intermittent/non-core failure; usable or partial workaround |
| **4 — Minor** | Cosmetic/edge-case/negligible functional impact |

P0/P1 require a reviewed COE; P2 is encouraged for novel/recurring failures; P3/P4 are optional. Rating never permits incident consolidation.

## Required investigation method

### 1. Establish identity and scope

Define the distinct production event: trigger/start, affected population/function, customer/system impact, and end state. Split separate impact events even if the same defect caused them. Quantify users, workspaces, requests, duration, functionality lost/degraded, workaround, and blast radius. Separate impact from secondary/noisy symptoms.

### 2. Build an evidence-backed UTC timeline

Anchor each fact to evidence and distinguish facts known at the time from later interpretation. Calculate separately:

- **TTD:** start → detection
- **TTA:** detection → acknowledgement/investigation ownership
- **TTM:** acknowledgement → meaningful mitigation/customer impact stopped
- **TTR:** acknowledgement → causal defect actually fixed/resolved

Disappearance of errors is not TTR if the defect remains. Current status must be exactly **ACTIVE**, **MITIGATED**, **QUIET / NOT FIXED**, **FIX DEPLOYED / VERIFYING**, or **RESOLVED**.

### 3. Construct two causal structures

#### A. Failure Mechanism Chain

Explain execution from normal operation to observed impact as deeply as evidence supports:

`condition/trigger → component behaviour → unexpected state → safety mechanism failure → propagation → customer/system impact`

Use code-level detail. For branching/converging causes use a causal tree/DAG, not a false line.

#### B. Escape / System Chain

Explain why the engineering system let the unsafe state reach and remain in production. Continue asking why while answers reveal controllable weaknesses:

- Why was the behaviour possible?
- Why did design/review/tests not prevent it?
- Why did staging/canary/release validation not catch it?
- Why was it not detected or acted on earlier?
- Why was diagnosis misleading or slow?
- Why did mitigation fail or take too long?
- Why did an existing fix not reach this release?
- Why were related signals, tickets, PRs, or investigations not correlated?
- Which architecture, ownership, or information-flow assumption enabled escape?

Do not force exactly five whys. For each causal node ask: **without it, would the incident have been prevented, materially reduced, detected earlier, or recovered from faster?** If no, it is likely context, chronology, or symptom.

Classify nodes where useful: initiating defect; necessary precondition; contributing factor; amplifier/blast-radius factor; failed prevention/containment/detection control; diagnosis/observability weakness; mitigation/recovery weakness; release/process escape; organisational/ownership weakness.

Do not label symptoms as causes (elevated errors, consequent retries, loop-generated noise, or CPU caused by runaway execution).

### 4. State causes precisely

Avoid “the root cause” when several factors were necessary. Prefer: “The initiating software defect was X. It reached production because controls A and B were absent, impact was amplified by C, and recovery was delayed by D.” The canonical **Root Cause / Causal Summary** contains only the best supported explanation. Retracted explanations remain only in Investigation History.

### 5. Identify safety invariants

State the property that should always have held—for example: an error handler cannot throw while building an error response; absent tenant context fails closed; tenant config never crosses tenants; retries are bounded; requests cannot contaminate another request's state; handled auth failure cannot recursively invoke auth. Encode invariants in code, types, assertions, tests, architecture, deployment gates, or runtime checks rather than memory.

### 6. Analyse coverage and release escape

Never write only “tests missed it.” Name the precise missing behaviour and layer: unit, integration, concurrency, multi-tenant, request lifecycle, auth/unauthenticated, error, rollback, upgrade, release branch, load, or failure injection. Derive regression/invariant tests from the mechanism.

For regressions document the introducing change, why it appeared safe, review assumptions, tests run/missing, deployment path/releases, any fix elsewhere and why it did not propagate, and whether staging/canary could realistically catch it. Analyse the system around a change, not its author.

### 7. Analyse detection and response

Keep prevention, containment, detection, diagnosis, mitigation, recovery, and permanent fix distinct. Explain detection method, expected versus actual behaviour, TTD/TTA gaps, and causes of diagnosis/mitigation time.

## Corrective actions

Every addressable causal/control weakness maps to action(s) or an explicit Accepted Risk. No filler.

Consider: **Eliminate** the defect; **Prevent** with regression/property tests, stronger APIs/types, fail-closed behaviour, isolation/static validation; **Contain** with bounded retries, recursion guards, circuit breakers, tenant/request isolation, resource limits; **Detect** with invariant telemetry, targeted alerts, canary/release assertions; **Diagnose** with causal identifiers and correlation telemetry; **Recover** with safe degradation, rollback automation, fallback, kill switches; **Escape Prevention** with ancestry checks/backport tracking/release gates; and **Organisational / Process** improvements to correlation, work discovery, closure reasons, and ownership.

Never use vague actions (“add tests,” “improve monitoring,” “be careful,” “human error”). Specify mechanism and objectively testable result.

| # | Action | Causal node addressed | Class | Owner | Tracking | Target | Verification | Status |
|---|---|---|---|---|---|---|---|---|

Do not invent commitments. Use **NEEDS OWNER**, **NEEDS TRACKING**, and **NEEDS TARGET DATE**. “Merged” is not verification; state how the failure mode will be proven controlled.

| Weakness | Reason risk accepted | Decision owner | Review date |
|---|---|---|---|

## Required COE structure

Use approximately this structure for **each individual incident**:

1. **Metadata** — Incident ID, date, priority, Impact × Severity, affected service/workspace/release, status, author, reviewers, related incidents, tracking links.
2. **Executive Summary** — impact, initiating defect, major systemic causes, current fix state.
3. **Impact** — quantified actual impact, duration, function, workaround, blast radius; secondary noise separate.
4. **Detection** — method, expected/actual control behaviour, TTD/TTA, gaps.
5. **Timeline** — evidence-backed UTC facts; TTD/TTA/TTM/TTR.
6. **Technical Reconstruction** — execution-level transition from normal to failure.
7. **Failure Mechanism Causal Chain** — numbered chain or DAG.
8. **Escape / System Causal Chain** — development, tests, review, release, observability, response, organisation.
9. **Safety Invariant(s)** — properties and encoding mechanism.
10. **Failed or Missing Controls** — `Control | Expected behaviour | Actual behaviour | Why it failed/was absent`.
11. **Contributing and Amplifying Factors** — conditions that worsened impact but did not independently cause it.
12. **Investigation History / Retracted Hypotheses** — support, actions, disproof, correction time, cost/lesson, unsuccessful mitigations, misleading signals.
13. **Root Cause / Causal Summary** — current explanation only; defect, preconditions, safeguards, amplification, response.
14. **Test Coverage and Change / Release Escape Analysis**.
15. **Corrective Actions** — full-schema table mapped to nodes.
16. **Accepted Risks** — every intentionally unaddressed weakness.
17. **What Went Well** — evidence-supported working controls.
18. **What Made This Harder**.
19. **Lessons / Generalisable Improvements** — architectural/operational principles.
20. **Verification / Closure Criteria** — exact evidence required for RESOLVED.
21. **Evidence / References** — captured data and relevant links/timestamps.
22. **Preservation Audit** — mandatory for rewrite/split; source-to-destination fact accounting.

## Publication

Publish each incident separately under Agor Knowledge `incidents`, e.g. `YYYY-MM-DD-<incident-slug>-coe.md`. Report the public `url`, not only `agor://`. In incident channels lead with rating, one-line causal summary, peak impact, status, and URL. Related documents link each other and retain their own trigger, impact, detection, timeline, and contributors.

## Final publication gate

Do not publish until every answer is yes:

- Can the document explain exactly how impact occurred?
- Are mechanisms distinguished from symptoms/context?
- Does it explain why safeguards allowed escape/persistence?
- Are review, test, staging/canary, release, detection, diagnosis, containment, and recovery gaps examined where relevant?
- Does every addressable weakness map to a specific verifiable action or Accepted Risk?
- Are unknown owners/tracking/targets explicitly marked rather than invented?
- Are disproven hypotheses and unsuccessful actions preserved without polluting the canonical cause?
- Is quiet/mitigated/recovered distinguished from fixed/resolved?
- Is this exactly one production incident?
- If rewritten/split, is every substantive source fact accounted for?
- Has no superseded hypothesis entered the final cause?
- Does every causal node pass the counterfactual test?

The finished COE must leave the system stronger at every causal layer exposed.

**Related skills:** [[postmortem-from-p0-p1]], [[datadog]], [[report-execution-investigation]], [[release-health-check]]
