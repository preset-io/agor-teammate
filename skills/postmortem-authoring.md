# Skill: Postmortem Authoring (Impact × Severity)

**When to use:** You need to write (or grade) a postmortem for a production incident. This is the canonical "how to structure, rate, and publish the doc" skill. It defines Preset's **Impact × Severity** rating (e.g. a `B3` incident) and a copy-paste template. Pair it with [[postmortem-from-p0-p1]] when the raw story has to be reconstructed from `#p0-p1-comms` / `#releases-preset-cloud` first — that skill *gathers* the facts, this one *rates and writes them up*.

**Principle: blameless.** Postmortems fix systems, not people. Name roles/systems, never blame an individual. Assume everyone acted reasonably with the information they had. (Google SRE.)

---

## The Rating: Impact × Severity → a two-letter/number code

> **Canonical standard:** [Postmortem Rubric: Impact × Severity](https://agor.sandbox.preset.zone/ui/kb/incidents/standards/impact-severity-rubric.md) (`agor://kb/incidents/standards/impact-severity-rubric.md`). The tables below mirror it — if they ever diverge, the KB doc wins; update it there and re-sync here.

Every incident gets **one Impact letter (A–D)** and **one Severity number (1–4)**, combined into a single code like `B3`. The two axes are deliberately independent:

- **Impact = blast radius.** *Who and how many* are affected (breadth).
- **Severity = depth of harm.** *How badly* they're affected, for those in the blast radius (depth).

This is why one number isn't enough. "A single enterprise customer lost all their data" (`D1`) and "every workspace has a slightly-misaligned button" (`A4`) are wildly different incidents that a single SEV scale would smear together. Keeping breadth and depth on separate axes captures both.

### Why this shape (prior art)

- **[MIL-STD-882E](https://reliabilityanalytics.com/reliability_engineering_library/MIL-STD-882E_Department_of_Defense_Standard_Practice_System_Safety_11_May_2012/MIL-STD-882E_Department_of_Defense_Standard_Practice_System_Safety_11_May_2012_pp_18.pdf)** — the DoD system-safety standard — rates hazards on exactly this shape: a **numeric Severity** (1 Catastrophic, 2 Critical, 3 Marginal, 4 Negligible) crossed with a **letter axis**, combined into a single "Risk Assessment Code" like `1A`. We borrow the code shape and the Severity number semantics directly.
- **[Google SRE](https://sre.google/workbook/postmortem-culture/):** "severity is an attribute of the incident; priority is a decision made by the responder." Our Severity number is that attribute; the combined code drives the priority (below).
- **[PagerDuty / Atlassian SEV1–SEV5](https://www.xurrent.com/blog/incident-severity-levels):** the conventional single-axis scale. Our Severity number maps 1:1 to SEV1–SEV4 depth; our Impact letter is the axis those scales leave implicit.

### Impact — blast radius (A–D)

| Impact | Blast radius (Preset terms) | Rough scope |
|--------|------------------------------|-------------|
| **A — Global** | All / most workspaces across regions, or a shared control-plane outage (auth, manager, gateway) affecting the whole fleet. Public/press-worthy, fleet-wide SLA exposure. | Whole customer base |
| **B — Segment** | A full region/cluster, or a large customer tier/cohort of workspaces. Bounded, but many customers. | A region / a tier |
| **C — Localized** | A handful of workspaces or a single customer, **or** one non-critical feature across many workspaces. | Few customers / one feature |
| **D — Isolated / Internal** | A single workspace, internal tooling, or staging/pre-prod. No material external customer impact. | One tenant / internal only |

### Severity — depth of harm (1–4)

| Severity | Depth of harm | Workaround |
|----------|---------------|------------|
| **1 — Critical** | Complete loss of service, data loss/corruption, or a confirmed **security/privacy breach**. | None |
| **2 — Major** | A core workflow (log in, load a dashboard, run a query) is broken or effectively unusable. | None acceptable |
| **3 — Moderate** | Degraded but usable — slow, intermittent, elevated errors, or a non-core feature down. Most requests still succeed. | Exists / partial |
| **4 — Minor** | Cosmetic or edge-case. Negligible functional impact. | Trivial / N/A |

> Rate on **peak observed impact**, not the average and not the worst *imaginable* case. If it worsened over time, rate the worst point actually reached and note the escalation in the timeline.

### Combined matrix → priority & response

The code maps to a priority tier (the `P0/P1` language already used in `#p0-p1-comms`), which drives paging, comms cadence, and whether a full postmortem is required.

| Impact ↓ / Severity → | **1 Critical** | **2 Major** | **3 Moderate** | **4 Minor** |
|---|---|---|---|---|
| **A Global**   | **P0** | **P0** | **P1** | **P2** |
| **B Segment**  | **P0** | **P1** | **P2** | **P3** |
| **C Localized**| **P1** | **P2** | **P3** | **P3** |
| **D Isolated** | **P2** | **P3** | **P3** | **P4** |

| Priority | Response | Postmortem |
|----------|----------|------------|
| **P0** | All-hands, page immediately, public status page + exec notify, comms on a fixed cadence. | **Required**, reviewed |
| **P1** | Page on-call, stakeholder notify, status page if customer-visible. | **Required** |
| **P2** | Business-hours urgent, internal notify. | Optional (encouraged if novel/recurring) |
| **P3** | Normal queue. | Optional |
| **P4** | Tracked as a bug. | Not needed |

**Worked example — a `B3`:** a whole region's workspaces (`B` — Segment) saw elevated errors / slow chart loads but stayed usable with most requests succeeding (`3` — Moderate) → **P2**. Notable and postmortem-worthy, but not a fleet-wide fire. This is the level the user flagged as the reference case.

Put the code **in the title and the TL;DR** (`Postmortem: <slug> — B3 (P2)`) so it's greppable and sortable later.

---

## Steps

### 1. Rate it first

Assign Impact + Severity before writing prose — it sets the priority, the required rigor, and the audience. If you're between two ratings, **round up** and say why in one line. Re-rate at the end if the investigation changed your understanding of blast radius (and note the change).

### 2. Reconstruct the timeline (UTC, anchored to evidence)

A table, every row anchored to something **verifiable** — a commit SHA, a Slack `ts`, a Datadog event timestamp, a deploy/rollback event — never vague relative time. See [[postmortem-from-p0-p1]] for pulling these from Slack + release channels. Capture the canonical incident metrics from the timeline:

| Metric | Meaning |
|--------|---------|
| **TTD** — time to detect | incident start → first alert/human notice |
| **TTA** — time to acknowledge | detect → someone owns it |
| **TTM** — time to mitigate | ack → customer impact stopped (rollback/flag/scale) |
| **TTR** — time to resolve | ack → root cause actually fixed |

A large **TTD** is itself a finding — it means detection is the gap (see step 5), regardless of how fast the fix was.

### 3. Capture the logs and metrics *into the doc* — don't just link

**Datadog (and most dashboard) links expire.** Treat every external link as a pointer that will rot. The doc must stand alone years later. So:

- **Pull the raw numbers via the API and paste them as markdown tables / code blocks** — this is the source of truth, it never expires, and it's diff-able. Use the [[datadog]] skill (`/api/v2/logs/events/search` for samples, `/api/v2/logs/analytics/aggregate` for exact counts grouped by `cluster_name`/`environment`). Include the **exact query string and time window** next to the numbers so anyone can re-run it.
- **Screenshot anything that only lives in a graph** (a spike shape, a flame graph, a trace waterfall) and embed the image — *and still paste the underlying peak/count as text beneath it*, so the fact survives even if the image is later lost.
- Paste representative log lines (timestamp + status + message + a stack frame) in a code block, not a screenshot of a log line — text is searchable and copyable.
- Keep the live Datadog URL too, but label it *"(link expires — data captured below)"* so no future reader trusts it as the record.

Attaching images to the published doc: upload the screenshot as an Agor Knowledge attachment / board artifact (or drop it under `incidents/assets/<slug>/`) and reference it with a stable relative/`agor://` path — never a Datadog CDN URL, which expires with the link.

### 4. Root cause — the mechanism, confirmed

State the **confirmed mechanism**, not the symptom. Distinguish the **trigger** (what set it off now — a deploy, a traffic spike, a config change) from the **root cause** (the latent condition that made the trigger harmful). Confirm via source diff / logs, not changelog text alone — see [[postmortem-from-p0-p1]] steps 3–4 for the verify-at-the-tag technique and checking for prior recurrences.

Then go past the first "why." A short **5-whys** or a **contributing-factors** list ("why did it happen / why wasn't it caught / why did it take so long to mitigate") almost always beats a single root cause — most incidents are a chain, not a point. If something is genuinely unknown from outside the org, **say so and name who should chase it** — don't launder speculation as fact.

### 5. Remediation — what we did, and the detection gap

- **Mitigation** (stopped the bleeding): rollback, feature flag, scale-up, failover — with the timestamp it took effect and how you confirmed impact stopped (the *last* occurrence in Datadog after the fix — verify before claiming "resolved").
- **Fix** (removed the root cause): the PR/commit, whether it's merged and deployed everywhere.
- **Detection gap:** should a monitor have caught this, and why didn't it? "No monitor exists" vs. "a monitor exists but didn't fire" (threshold too high for a low-traffic-but-100%-failing tenant, ratio metric whose denominator collapsed, wrong layer) are different findings with different fixes. Remember monitors are **IaC/Terraform + PR only**, never console clicks ([[project_iac_only_no_manual_infra_changes]]).

### 6. Next steps — action items that reduce recurrence or blast radius

An **action-item table**, each row with an **owner, a due date, a tracking link (Shortcut story), and a class**:

- **Prevent** — stop the root cause recurring (the highest-leverage row is usually here — often a *process* gap like the release pipeline, not another monitor).
- **Detect** — catch it faster next time (closes the TTD gap from step 2).
- **Mitigate** — make it less bad / faster to stop when it does recur.

Pick **1–3 that matter**, file them as real Shortcut stories, and link them. An action item with no owner or ticket is a wish, not a plan. Prefer one durable fix over ten vague "improve X" bullets.

### 7. Publish

Publish to Agor Knowledge under the `incidents` namespace (same convention as [[postmortem-from-p0-p1]]):

```
agor_kb_put({
  namespace: "incidents",
  path: "YYYY-MM-DD-<slug>.md",
  kind: "decision",
  visibility: "public",
  status: "published",
  editPolicy: "public",
  content: "<full markdown>"
})
```

Then report back in the incident channel: lead with the **code + one-line root cause + peak impact numbers + doc URL**. Don't paste the whole timeline into chat — that's the doc's job. Link any related prior incident doc via `agor://kb/document/<id>` if this is a recurrence.

---

## Postmortem Template (copy-paste)

````markdown
# Postmortem: <short title> — <CODE> (<Pn>)

**Status:** Draft | In review | Published
**Impact × Severity:** <e.g. B3 — Segment × Moderate → P2>
**Author:** <name>   **Date:** <YYYY-MM-DD>   **Reviewers:** <names>
**Related:** <agor://kb/document/... for any prior/recurring incident>

> Blameless: this document examines systems and decisions, not individuals.

## TL;DR
- What broke, for whom, how bad (5–8 bullets — the 30-second read).
- Rating: **<CODE>** (<Impact> × <Severity>) → **<Pn>**.
- Root cause in one sentence. Mitigation in one sentence.

## Impact
- **Rating:** <CODE> — <Impact letter rationale> × <Severity number rationale>.
- **Blast radius:** <regions/clusters/workspaces/customers affected>.
- **Numbers (captured, not linked — Datadog links expire):**
  | Metric | Value | Query / window |
  |--------|-------|----------------|
  | Failed requests | | `<dd query>` / `<from>–<to>` |
  | Peak error rate | | |
  | Customers affected | | |
  | Revenue / SLA at risk | | |
- **Detection:** how we found out (monitor / customer / manual) and when.

## Timeline (UTC)
| Time (UTC) | Event | Evidence |
|------------|-------|----------|
| | Incident begins | <commit/deploy> |
| | Detected | <alert/Slack ts> |
| | Acknowledged | |
| | Mitigated | <rollback/flag> |
| | Resolved | <last DD occurrence> |

**TTD:** __  **TTA:** __  **TTM:** __  **TTR:** __

## Logs & Evidence
<!-- Paste raw log lines in code blocks; embed screenshots AND the numbers beneath them.
     Every image via a stable path, never a Datadog CDN URL. -->
```
[timestamp] [status] message ... stack frame
```
![error spike](incidents/assets/<slug>/error-spike.png)
_Peak: <N> errors/min at <time> in <cluster>. (Datadog link expires — captured above.)_

## Root Cause
- **Trigger:** <what set it off now>.
- **Root cause:** <latent condition, confirmed via source diff / logs>.
- **Contributing factors / 5 whys:**
  1. Why did it happen? …
  2. Why wasn't it caught? …
  3. Why did mitigation take as long as it did? …
- **Open questions:** <unknowns + who should chase them>.

## Remediation
- **Mitigation:** <action, timestamp, how impact-stop was confirmed>.
- **Fix:** <PR/commit, merged? deployed everywhere?>.
- **Detection gap:** <no monitor / monitor didn't fire — and why>.

## What went well / poorly / where we got lucky
- **Well:** …
- **Poorly:** …
- **Lucky:** <things that could have been much worse>.

## Next Steps (action items)
| Action | Class (Prevent/Detect/Mitigate) | Owner | Due | Ticket |
|--------|--------------------------------|-------|-----|--------|
| | | | | <Shortcut story> |

## Related incidents
- <links to prior/similar postmortems>
````

---

## Notes

- **Rate on peak observed impact**, round up when between tiers, and re-rate at the end if the facts changed (note the change).
- **Every external dashboard link is assumed to expire** — the numbers and screenshots must live inside the doc. A postmortem whose evidence is a dead Datadog link is worthless in six months.
- A big **TTD** is a finding, not a footnote — it means detection, not the fix, is where the leverage is.
- Highest-leverage action item in a recurrence is almost always the **process/prevent** row (e.g. a release-pipeline gap), not another layer of monitoring — say so explicitly rather than burying it in an equal-weighted list ([[postmortem-from-p0-p1]] step 7).
- Action items are only real once they're **Shortcut stories with owners** — file them, link them, don't leave wishes.

**Related skills:** [[postmortem-from-p0-p1]] (reconstruct the story from Slack + release channels — the input to this skill), [[datadog]] (pull the log/metric evidence), [[report-execution-investigation]] (execution-id tracing), [[release-health-check]] (release-tag vs. Datadog correlation)

**Sources:** [MIL-STD-882E](https://reliabilityanalytics.com/reliability_engineering_library/MIL-STD-882E_Department_of_Defense_Standard_Practice_System_Safety_11_May_2012/MIL-STD-882E_Department_of_Defense_Standard_Practice_System_Safety_11_May_2012_pp_18.pdf) · [Google SRE postmortem culture](https://sre.google/workbook/postmortem-culture/) · [SEV1–SEV5 explained (Xurrent)](https://www.xurrent.com/blog/incident-severity-levels) · [Incident severity & blast radius (Uptime Labs)](https://www.uptimelabs.io/learn/incident-severity-levels)
```
