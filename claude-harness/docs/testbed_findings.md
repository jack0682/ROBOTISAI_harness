# Testbed-driven harness findings

Gaps and confirmations found by running the harness on **real** projects, not by
review of reference repos (that is `ref_analysis.md`). Each finding is grounded
in concrete friction hit while doing a real task under the harness.

## Testbed 2 — frontier_robot (2026-06-12)

**Task.** Diagnose why a sensorless bilateral teleoperation feature failed: an
OMY follower runs current-as-force-proxy compliance (stays in *position* mode,
yields by moving the setpoint) while an OMY leader renders a P-P force-reflection
spring `τ_L = ramp·(α·kc·(q_F−q_L) − bc·q̇_L)`. Teleoperation alone works;
compliance + force-feedback **together** limit-cycle (documented in the code's
own `leader_feedback.yaml` 2026-06-12 REGRESSION note). **Constraint: nothing
builds or runs** — the repo only builds on an ORIN board in Docker; on the dev
MacBook there is no build, no run, no mock. Verification was read-only +
control-theory reasoning.

### Harness WINS (confirmed, keep)

- **W1 — the primary-source gate paid off immediately.** With execution
  impossible, the temptation is to trust a subagent's code map. The new
  `modes/verify.md` primary-source gate forced reading the actual crux files
  (`leader_feedback_controller.cpp:207`, `follower_admittance_controller.cpp:
  404–438`, both yaml regression notes) before any verdict. It changed nothing
  in the conclusion this time, but it is the correct discipline and was used.
- **W2 — `math_lock`'s observed-vs-latent / identifiability checklist
  generalized perfectly from pure math to a control system.** The root cause is
  exactly an identifiability failure: sensorless current = τ_gravity +
  τ_tracking + τ_friction + τ_external, and the controller subtracts only a
  *static* gravity baseline, so τ_ext is non-identifiable *during motion* —
  which is precisely when teleop is active. Item 7 of the `math_lock` checklist
  named the bug. Same lens that caught ONN's CSR tautology. This is the
  harness's killer app for the team's work (see F7).

### Harness GAPS (ranked by leverage)

> **Status as of 2026-09-20** — all eight closed, verified against `main` rather
> than remembered. The ranking in *Net* below called F1 and F2+F3
> highest-leverage and those landed first; the rest followed in one pass.
>
> | | Finding | Status | Where it lives now |
> |---|---|---|---|
> | **F1** | environment-capability | **shipped** | `project.config.yaml` `environment:` block; `stop_gate.py` `analysis_only` branch demanding a verification ceiling; `modes/verify.md` |
> | **F2** | control scope | **shipped** | `scopes/control/AGENTS.md`, `registry/scopes.yaml`, wired into `route_hint.py` and `.claude/rules/scope-control.md` |
> | **F3** | math_lock dynamics axis | **shipped** | `modes/math_lock.md` items 10–12 — closed-loop stability, energy/passivity, delay/sampling/bandwidth |
> | **F4** | harvest the code's self-documentation | **shipped** | `protocols/debugging.md` step 3 and a `scopes/coding/` local invariant: a developer's documented failure is primary evidence, not background |
> | **F5** | reconcile the description against the artifact | **shipped** | `modes/verify.md` operation 8 (the primary-source gate applied to the user's own account) + `ROUTING.md` Step 0 |
> | **F6** | `/harness-analyze` | **shipped** | `commands/harness-analyze.md` + `scripts/new_analysis.py` — a work graph and claims scoped to an external repo, registered `status: analysis` so it cannot disarm the real project's gates |
> | **F7** | identifiability as a cross-scope lens | **shipped** | cited from `scopes/control/` and now `scopes/experiments/` as a local invariant, pointing back at `modes/math_lock.md` item 7 |
> | **F8** | sampled-data / delay | **shipped** | absorbed into F3 item 12 and `scopes/control/`, which is what F8 itself asked for |
>
> **One placement deviates from the prescription, deliberately.** F4 said "a step
> in `scopes/coding` + `modes/audit`". `modes/audit.md` takes *the original
> request and the produced work* as input — it audits your own output, not
> someone else's system. Harvesting a codebase's self-documentation is
> brownfield *diagnosis*, so the step went to `protocols/debugging.md`, which is
> the procedure that actually runs it, with the invariant in `scopes/coding/` as
> written.

- **F1 — no environment-capability awareness; verification machinery assumes you
  can execute.** `stop_gate` demands `validation.commands` (pytest/colcon)
  evidence, and the whole verify discipline implicitly assumes run/test is
  possible. Here it is *physically impossible*. The harness has no notion of an
  **analysis-only environment**, so it can neither (a) recognize that
  execution-verification is unavailable, (b) substitute the right standard
  (primary-source read + theory + cross-check against the code's own
  self-documentation), nor (c) avoid the false binary of "no test evidence →
  block forever" vs "silently treat unverified as fine". *Fix:* a
  `project.config.yaml` `environment:` block (`can_build / can_run /
  can_run_hardware / verification_mode: execution|analysis_only`); when
  `analysis_only`, `stop_gate` stops demanding `validation.commands` and instead
  demands an analytic-verification artifact, and `verify` marks every claim with
  its **verification ceiling** (here: "static + theory; not hardware-validated").
- **F2 — no control / dynamics scope.** Scopes are math/research/writing/coding/
  experiments/prompts. A bilateral-teleoperation stability bug is part coding
  (ROS2 C++), part math (passivity/stability), part experiments (the failed
  run) — spanned ad hoc across three. the team's domains include robotics/control
  + ROS2; there is no scope owning loop stability, passivity/energy, causality,
  real-time bandwidth, or sensor/actuator model fidelity. *Fix:* add
  `scopes/control/AGENTS.md` (or `dynamics`) with those invariants.
- **F3 — `math_lock` has no closed-loop / feedback-stability axis.** Its
  checklist verifies a *static* formalism; both real testbeds were *dynamic
  systems*. Nothing in it prompts "check the closed-loop poles / passivity /
  gain-phase margin / sampling + delay / limit cycles." The frontier failure is
  literally a limit cycle from coupled stiffness/damping at a 200 Hz loop with
  EMA + transport lag. *Fix:* a dynamics sub-checklist in `math_lock` (or the
  control scope): stability, passivity/energy, delay/sampling, actuator–sensor
  bandwidth — sitting next to the existing identifiability item.
- **F4 — no "harvest the code's own self-documentation first" reflex for
  brownfield work.** The single most valuable artifact was the dev's own
  REGRESSION comment that named the failure. ONN had the same (FINAL_/COMPLETION
  docs, EVIDENCE_FIRST_VERDICT). The harness's audit/coding modes never say:
  before diagnosing an existing system, harvest its TODO/FIXME/regression notes/
  commit messages/known-issue files as *primary* evidence. *Fix:* a step in
  `scopes/coding` + `modes/audit` — "read what the code says about itself first;
  a dev's documented failure is primary evidence, not background."
- **F5 — reconcile the user's described architecture against the code.** The
  user described follower compliance as "sensorless **torque/current**"; the code
  reality is *position-mode* admittance using current only as a *proxy*, yielding
  via the setpoint — not torque-mode control. A real, decision-relevant gap
  between mental model and artifact. `ROUTING.md` Step 0 ("read the request
  twice") parses the request but never reconciles it with the artifact. *Fix:*
  make this the primary-source gate applied to the *user's own claims* — when the
  user describes a system, check the description against the code and surface the
  divergence before reasoning on the description.
- **F6 — no lightweight "attach to an external repo for analysis" mode.** For
  testbed 1 (ONN) a full harness copy + bridge + hook install was deployed; for
  this one that is disproportionate for a read-only diagnosis. There is nothing
  between "no harness" and "full project registration + bridge + hooks". *Fix:* a
  `/harness-analyze <path>` that sets up just the work-graph + claims scoped to
  an external repo, no bridge/hook deployment.
- **F7 — elevate identifiability/observability from a buried checklist item to a
  first-class cross-scope lens.** In *both* testbeds the decisive contribution was
  "can the quantity of interest actually be recovered from what's observed?" —
  ONN: CSR measures what it enforces (not independent); frontier: τ_ext not
  separable from τ_tracking sensorlessly during motion. It applies to
  experiments and control, not only proofs, yet it lives as item 7 in one mode.
  *Fix:* promote it (a prominent kernel lens or a small dedicated mode) and
  reference it from experiments + the new control scope.
- **F8 — no sampled-data / delay / latency reasoning anywhere.** The failure is
  inseparable from discrete time: 200 Hz loop, EMA τ=0.05 s (~10-cycle lag),
  5-cycle debounce, 2 s ramp, topics across two controller managers. The harness
  has no vocabulary for sampling/delay/latency. *Fix:* fold into F2/F3 (control
  scope + dynamics checklist).

### Net

The harness's *epistemic core* (primary-source, identifiability, claim
discipline) transferred cleanly and did real work (W1, W2). Its *coverage* is
research-OS-shaped and missed a whole domain it claims (control/robotics, F2/F3/
F8) and a whole *mode of work* (brownfield diagnosis under non-executable
conditions, F1/F4/F5/F6). Highest leverage: **F1** (environment-capability) and
**F2+F3** (control scope + dynamics/stability axis), because they convert the
harness from "research-paper rigor" to "rigor for a system you can read but not
run" — which is most of real engineering.
