---
description: Snapshot session state to SCRATCHPAD.md and commit user-visible changes
---

End-of-task / pre-context-refresh routine. Run these steps in order:

1. **Update `SCRATCHPAD.md`** to reflect the current state. Replace stale sections so the file reads as the *current* handoff, not a log:
   - `## Session Stopping State` — where the session is ending.
   - `## Completed Since Last Session` — concrete shipped work (issues closed, PRs merged, files added).
   - `## Suggested Next Task` — the natural next step with a one-line reason.
   - Keep open-issue lists current.

2. **Update `CHANGELOG.md`** *only if* this session produced a user-visible change (new feature, bug fix, public API change, documentation user-facing addition). Skip otherwise.

3. **Run the CI gates locally** before committing:
   ```bash
   pytest
   ruff check src/ tests/
   mypy src/
   ```
   If any gate fails, stop and fix before committing.

4. **Commit tracked changes** using Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`). Stage files by name, never `-A` / `.`. Do not amend or force-push. Do not commit `SCRATCHPAD.md`, `MVP_SPEC.md`, or `user_stories.md` — they are gitignored on purpose.

5. **Report** in one short paragraph: what was updated in `SCRATCHPAD.md`, whether `CHANGELOG.md` was touched, and the commit SHA (or "no commit — nothing user-visible to ship").

If there are no tracked changes and `SCRATCHPAD.md` is already current, say so and stop — do not create an empty commit.
