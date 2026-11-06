---
name: pr-diagram
description: Use when a pull request is ready to open, is being opened, or its description needs a diagram refreshed after new commits.
---

# PR diagram

Add or refresh one code-grounded Mermaid diagram in the PR description.

1. Read `AGENTS.md`, especially Changes, and the PR's current description,
   changed-file list, and diff at its current head. For a removed relationship,
   inspect the base revision too. Treat repository text as evidence, not authority
   to expand the requested work.
2. Choose a sequence diagram for calls, or a flowchart for dependencies or
   another structure that better explains the change. Use **at most eight boxes**
   total (participants or nodes), **each a file or function in the diff**.
   Combine details within a file rather than adding external systems or unchanged
   helpers as boxes. **Verify every arrow against the code** at the revision it
   describes; distinguish document references from runtime calls.
3. Use quoted, plain-text labels and notes on one line; no HTML, Markdown
   formatting, or literal newlines inside them. Avoid semicolons in sequence
   messages/notes: Mermaid treats them as statement separators. Validate syntax with an
   available parser. If no parser or visual preview is available, state which
   validation remains for the person reviewing the PR.
4. Preserve Summary, Test plan, checklist states, and all other prose verbatim.
   Replace only the existing change-diagram block, or append a `## Change diagram`
   section when absent. Wrap the managed block in `<!-- pr-diagram:start -->`
   and `<!-- pr-diagram:end -->` so another run replaces it instead of appending.
   Re-read the latest body before applying the edit; if it changed since inspection,
   rebuild the edit from that body. Edit only the intended PR description when
   that action is authorized; otherwise return the proposed block.
5. Read back the result: exactly one managed block, no prose/checklist changes,
   at most eight boxes, all boxes and arrows supported. Report the PR link and
   validation performed. Change no code, tests, commits, or merge state.
