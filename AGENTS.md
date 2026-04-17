# AGENTS.md — Repository Knowledge Base

## Repository
- **GitHub**: `aimoptheman/test`
- **Purpose**: Vanilla-JS component library demo project

## Components
- **MultiStateButton** (`components/multi-state-button/`)
  - `MultiStateButton.js` — zero-dependency vanilla JS class
  - `MultiStateButton.css` — default styles with CSS custom properties
  - `README.md` — full API documentation

## GitHub Pages
- Root `index.html` serves as the live demo for MultiStateButton
- Pages source: `main` branch, root `/`
- Live URL: `https://aimoptheman.github.io/test/`

## Rules
- **Never close GitHub issues.** Only the user closes issues. When work on an issue
  is complete, leave a comment summarising what was done and say it is ready for review.
  Do NOT call the GitHub API to close (state: closed) any issue.

## Workflow
- All files are pushed directly via the GitHub Contents API (no local git clone)
- Use `python3` with `urllib.request` and the `GITHUB_TOKEN` env variable for all
  GitHub API calls
- After pushing changes, always post a comment on the relevant issue summarising
  what was done
