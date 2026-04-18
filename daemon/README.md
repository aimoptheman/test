# OpenHands Workflow Daemon

Polls GitHub every 60 seconds.  When any issue is opened or updated it fires
`run workflow` against your local OpenHands instance.  No external endpoint,
no GitHub webhook, no cloud runner needed.

## Setup

```bash
cd daemon/
cp .env.example .env
# Edit .env — set GITHUB_TOKEN (your existing PAT is fine)
python3 watcher.py
```

## Run as a background service

### macOS (launchd)

```bash
# 1. Edit com.aimoptheman.ohd.plist — update the two paths
# 2. Copy to LaunchAgents
cp com.aimoptheman.ohd.plist ~/Library/LaunchAgents/
# 3. Load it (starts now and on every login)
launchctl load ~/Library/LaunchAgents/com.aimoptheman.ohd.plist
# Logs: tail -f /tmp/ohd.log
```

### Linux (systemd user service)

```bash
# 1. Edit ohd.service — update ExecStart and WorkingDirectory paths
# 2. Install
mkdir -p ~/.config/systemd/user/
cp ohd.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now ohd
# Logs: journalctl --user -u ohd -f
```

## Configuration (via .env)

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | — | GitHub PAT (required) |
| `GITHUB_USER` | `aimoptheman` | User/org whose repos to watch |
| `OPENHANDS_URL` | `http://localhost:3000` | Local OpenHands URL |
| `POLL_INTERVAL` | `60` | Seconds between GitHub polls |
| `COOLDOWN` | `300` | Min seconds between OpenHands triggers |

## How it works

1. On first run: snapshots all open issues — **no trigger fired**
2. Every `POLL_INTERVAL` seconds: re-fetches all open issues
3. If any issue is new, updated, or closed: logs it and fires `run workflow`
4. OpenHands picks up from AGENTS.md: scans all repos, finds highest-priority
   open issue, works it, posts a summary comment
5. Cooldown prevents re-triggering while the previous run is still in progress
