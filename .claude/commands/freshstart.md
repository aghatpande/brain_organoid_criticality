---
description: Load core project context at the start of a session
---

Read the following files in order to understand the current project state, then summarize what you find:

1. `CLAUDE.md` — project conventions and the **Ground rules** block (non-negotiable).
2. `PRD.md` — full requirements; focus on §2 (scope), §3 (functional reqs), §5 (architecture), §9 (phased roadmap).
3. `MVP_SPEC.md` — Phase 1 detail spec with pinned function signatures and default thresholds. *(gitignored local planning doc)*
4. `SCRATCHPAD.md` — handoff notes from the previous session: stopping point, what's in flight, suggested next task. *(gitignored)*

Then list open issues:

```bash
gh issue list --repo aghatpande/brain_organoid_criticality --state open
```

Report back in under 200 words:

- The stopping point from the last session (per `SCRATCHPAD.md`).
- The current phase (per `PRD.md` §9) and what's actively in flight.
- The 1–2 open issues that look like the natural next step, with a one-line reason for each.

Do **not** start coding. This command is read-only orientation.
