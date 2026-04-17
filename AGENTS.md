# AGENTS.md — Repository Knowledge Base

## Repositories

| Repo | Visibility | Purpose |
|------|-----------|---------|
| `aimoptheman/test` | Public | Vanilla-JS demos + GitHub Pages host for all POCs |
| `aimoptheman/angular-components` | Private | Angular component library source |
| `aimoptheman/react-components` | Private | React component library source |
| `aimoptheman/domains` | Private | Domain portfolio — central analysis and expiry tracking |
| `aimoptheman/customop` | Private | Agent operations tracker — deviations and blockers filed here |
| `aimoptheman/<domain-repo>` | Private | One repo per domain (see Domain Repos section below) |

## Domain Repos

Each domain has its own private repo named after the domain with dots replaced by hyphens.
e.g. `gptvshuman.com` → `aimoptheman/gptvshuman-com`

All 38 Keep/high-priority domain repos have been created with README analysis files.

Profitability-impossible domains (dissentar.com, dissentaur.com, employees.chat etc.)
are documented in `aimoptheman/domains` only — no individual repo.

## Components

### MultiStateButton (vanilla JS)
- Location: `aimoptheman/test` → `components/multi-state-button/`
- Live demo: https://aimoptheman.github.io/test/

### MultiStateButton (Angular)
- Location: `aimoptheman/angular-components` → `src/lib/multi-state-button/`
- Demo: https://aimoptheman.github.io/test/demo/angular-multi-state-button.html

### MultiStateButton (React)
- Location: `aimoptheman/react-components` → `src/MultiStateButton/`
- Demo: https://aimoptheman.github.io/test/demo/react-multi-state-button.html

## Domain POCs (on aimoptheman/test GitHub Pages)

| Domain | POC URL |
|--------|---------|
| gptvshuman.com | https://aimoptheman.github.io/test/poc/gptvshuman/ |
| youveneverbean.com | https://aimoptheman.github.io/test/poc/youveneverbean/ |
| hivemind.trading | https://aimoptheman.github.io/test/poc/hivemind-trading/ |

## Agent Workflow

On every new session, follow these steps in order:

1. **Check all issues on all repos** — fetch `state=all` issues from every repo via GITHUB_TOKEN.
2. **Identify the highest-priority open issue** — priority order:
   - Labels `critical` or `bug` first
   - Otherwise lowest issue number in the earliest (alphabetical) repo listed
   - Skip issues where work is already complete (summary comment posted)
3. **Work on it to completion** — push all changes via the GitHub Contents API, post a summary comment.
4. **Never close issues** — only the user closes issues. Post a comment summarising work done.
5. **File deviations in `customop`** — any time a task spec is not followed exactly, file an issue in `aimoptheman/customop` explaining the deviation. Do NOT silently scope-reduce.
6. **Repeat** — re-check all repos for the next open issue.

## Rules

- **Never close GitHub issues.** Only the user closes issues.
- **Always file deviations in `aimoptheman/customop`.** Silent scope reductions are not acceptable.
- Keep `angular-components`, `react-components`, `domains`, and all domain repos private.
- All public-facing POCs go in `aimoptheman/test` (GitHub Pages, main branch root).
- All GitHub API calls use `python3` + `urllib.request` + `GITHUB_TOKEN` (no local clone).
- Domain repos: named as `<domain-with-hyphens>` e.g. `gptvshuman-com`, `hivemind-trading`.
- Always add `Co-authored-by: openhands <openhands@all-hands.dev>` to commit messages.
- Prefer zero-server-cost stacks (static HTML, GitHub Pages, Cloudflare Pages).

## Tech Stack

- **Vanilla JS**: zero deps, CSS custom properties
- **Angular**: Angular 17, standalone, OnPush, signal-based, zoneless
- **React**: React 18, functional, useState + useCallback, TypeScript, Vite
- **POC pages**: self-contained HTML; React uses React 18 UMD + Babel standalone
- **Domain POCs**: pure static HTML, AdSense / Amazon Associates / trading affiliates
