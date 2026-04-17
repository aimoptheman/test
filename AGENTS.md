# AGENTS.md — Repository Knowledge Base

## Repositories

| Repo | Visibility | Purpose |
|------|-----------|---------|
| `aimoptheman/test` | Public | Vanilla-JS component demos + GitHub Pages |
| `aimoptheman/angular-components` | Private | Angular component library source |

## Components

### MultiStateButton (vanilla JS)
- Location: `aimoptheman/test` → `components/multi-state-button/`
- Files: `MultiStateButton.js`, `MultiStateButton.css`, `README.md`
- Live demo: https://aimoptheman.github.io/test/

### MultiStateButton (Angular)
- Location: `aimoptheman/angular-components` → `src/lib/multi-state-button/`
- Angular 17, standalone component, signal-based, zoneless
- Demo: https://aimoptheman.github.io/test/demo/angular-multi-state-button.html

## Agent Workflow

On every new session, follow these steps in order:

1. **Check all issues on all repos** — fetch `state=all` issues from every repo
   accessible via the `GITHUB_TOKEN` environment variable.
2. **Identify the highest-priority open issue** — priority order:
   - Labels `critical` or `bug` first
   - Otherwise lowest issue number in the earliest (first) repo listed
3. **Work on it to completion** — implement everything described in the issue,
   push all changes via the GitHub Contents API, and post a summary comment on
   the issue when done.
4. **Never close issues** — only the user closes issues. Always leave a comment
   summarising the completed work instead.
5. **Repeat** — after finishing, re-check all repos for the next open issue.

## Rules

- **Never close GitHub issues.** Only the user closes issues. Post a comment
  summarising what was done; do NOT set `state: closed` via the API.
- Keep `aimoptheman/angular-components` private at all times.
- All GitHub API calls use `python3` + `urllib.request` + `GITHUB_TOKEN` env var
  (no local git clone needed).
- Demo pages that must be publicly accessible go in `aimoptheman/test`
  (GitHub Pages enabled, main branch root `/`).
- Always add `Co-authored-by: openhands <openhands@all-hands.dev>` to commit messages.

## Tech Stack

- **Vanilla JS component**: zero dependencies, CSS custom properties
- **Angular component**: Angular 17, standalone, `ChangeDetectionStrategy.OnPush`,
  signal-based reactive state, zoneless (`provideExperimentalZonelessChangeDetection`)
- **Demo pages**: self-contained HTML on GitHub Pages; Angular demo uses Angular 17
  via esm.sh importmaps (no build step required for the demo)
