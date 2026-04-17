# AGENTS.md — Repository Knowledge Base

## Repositories

| Repo | Visibility | Purpose |
|------|-----------|---------|
| `aimoptheman/test` | Public | Vanilla-JS demos + GitHub Pages host for all POCs |
| `aimoptheman/angular-components` | Private | Angular component library source |
| `aimoptheman/react-components` | Private | React component library source |
| `aimoptheman/domains` | Private | Domain portfolio — analysis, strategy, POC tracking |

## Components

### MultiStateButton (vanilla JS)
- Location: `aimoptheman/test` → `components/multi-state-button/`
- Live demo: https://aimoptheman.github.io/test/

### MultiStateButton (Angular)
- Location: `aimoptheman/angular-components` → `src/lib/multi-state-button/`
- Angular 17, standalone, signal-based, zoneless, OnPush
- Demo: https://aimoptheman.github.io/test/demo/angular-multi-state-button.html

### MultiStateButton (React)
- Location: `aimoptheman/react-components` → `src/MultiStateButton/`
- React 18, functional component, useState + useCallback, TypeScript, CSS custom properties
- Demo: https://aimoptheman.github.io/test/demo/react-multi-state-button.html

## Domain Portfolio POCs

- **gptvshuman.com** — Interactive GPT vs Human quiz (12 rounds, shuffled)
  → POC: https://aimoptheman.github.io/test/poc/gptvshuman/
  → Monetisation: AdSense + AI tool affiliates (Jasper, Copy.ai)
- **gptdebates.com** — AI vs Human structured debates → static HTML + email list
- **hivemind.trading** — Collective trader intelligence → email waitlist + trading affiliates
- **copytradinghub.com** — Copy trading affiliate directory
- See `aimoptheman/domains` repo for full viability matrix and per-domain analysis

## Agent Workflow

On every new session, follow these steps in order:

1. **Check all issues on all repos** — fetch `state=all` issues from every repo
   accessible via the `GITHUB_TOKEN` environment variable.
2. **Identify the highest-priority open issue** — priority order:
   - Labels `critical` or `bug` first
   - Otherwise lowest issue number in the earliest (first) repo listed
   - Skip issues where work is already complete (summary comment already posted)
3. **Work on it to completion** — implement everything described in the issue,
   push all changes via the GitHub Contents API, and post a summary comment.
4. **Never close issues** — only the user closes issues. Always leave a comment
   summarising the completed work instead.
5. **Repeat** — after finishing, re-check all repos for the next open issue.

## Rules

- **Never close GitHub issues.** Only the user closes issues.
- Keep `angular-components`, `react-components`, and `domains` private at all times.
- All GitHub API calls use `python3` + `urllib.request` + `GITHUB_TOKEN` env var (no local clone).
- All publicly-accessible demo/POC pages go in `aimoptheman/test` (GitHub Pages, main branch root).
- Always add `Co-authored-by: openhands <openhands@all-hands.dev>` to commit messages.
- Prefer zero-server-cost stacks (static HTML, GitHub Pages, Cloudflare Pages) for POCs.

## Tech Stack

- **Vanilla JS**: zero deps, CSS custom properties
- **Angular**: Angular 17, standalone, OnPush, signal-based, zoneless
- **React**: React 18, functional, useState + useCallback, TypeScript, Vite
- **POC pages**: self-contained HTML; React uses React 18 UMD + Babel standalone
- **Domain POCs**: pure static HTML, no server costs, AdSense / Amazon Associates / trading affiliates
