#!/usr/bin/env python3
"""
GitHub -> OpenHands Workflow Daemon

Polls GitHub for issue activity across all repos owned by GITHUB_USER.
When a new or updated issue is detected it fires a "run workflow" conversation
against the local OpenHands server.  No external endpoint needed.

Configure via environment variables or a .env file in the same directory:

  GITHUB_TOKEN      GitHub PAT with issues:read scope        (required)
  GITHUB_USER       GitHub username / org to watch           (default: aimoptheman)
  OPENHANDS_URL     Local OpenHands base URL                 (default: http://localhost:3000)
  POLL_INTERVAL     Seconds between GitHub polls             (default: 60)
  COOLDOWN          Min seconds between OpenHands triggers   (default: 300)
  STATE_FILE        Path for persisted issue state           (default: .daemon_state.json)

Usage:
  python watcher.py
  POLL_INTERVAL=30 python watcher.py
"""

import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


# ── Config ─────────────────────────────────────────────────────────────────────

def _env(key: str, default: str = '') -> str:
    # check a sibling .env file first, then os.environ
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            if k.strip() == key:
                return v.strip().strip('"').strip("'")
    return os.environ.get(key, default)


GITHUB_TOKEN  = _env('GITHUB_TOKEN')
GITHUB_USER   = _env('GITHUB_USER', 'aimoptheman')
OPENHANDS_URL = _env('OPENHANDS_URL', 'http://localhost:3000')
POLL_INTERVAL = int(_env('POLL_INTERVAL', '60'))
COOLDOWN      = int(_env('COOLDOWN', '300'))
STATE_FILE    = Path(_env('STATE_FILE', str(Path(__file__).parent / '.daemon_state.json')))
TASK_MSG      = 'run workflow'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
)
log = logging.getLogger('ohd')


# ── GitHub helpers ─────────────────────────────────────────────────────────────

def _gh(path: str) -> list | dict:
    req = urllib.request.Request(
        f'https://api.github.com{path}',
        headers={
            'Authorization': f'Bearer {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'openhands-daemon/1.0',
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def fetch_open_issues() -> dict[str, str]:
    """Return {repo#number: updated_at} for all open non-PR issues."""
    result: dict[str, str] = {}
    page = 1
    while True:
        repos = _gh(f'/users/{GITHUB_USER}/repos?per_page=100&page={page}&type=owner')
        if not repos:
            break
        for repo in repos:
            rname = repo['full_name']
            try:
                issues = _gh(f'/repos/{rname}/issues?state=open&per_page=100')
                for issue in issues:
                    if 'pull_request' in issue:
                        continue
                    result[f"{rname}#{issue['number']}"] = issue['updated_at']
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    log.warning(f'Issues fetch failed for {rname}: HTTP {e.code}')
            except Exception as e:
                log.warning(f'Issues fetch failed for {rname}: {e}')
        if len(repos) < 100:
            break
        page += 1
    return result


# ── State ──────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {'issues': {}, 'last_trigger': 0.0}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── OpenHands trigger ──────────────────────────────────────────────────────────

def trigger_openhands(reason: str, state: dict) -> bool:
    since = time.time() - state.get('last_trigger', 0.0)
    if since < COOLDOWN:
        remaining = int(COOLDOWN - since)
        log.info(f'Cooldown: {remaining}s left — skipping trigger ({reason})')
        return False

    log.info(f'Triggering OpenHands — {reason}')
    body = json.dumps({'initial_user_msg': TASK_MSG}).encode()
    req = urllib.request.Request(
        f'{OPENHANDS_URL}/api/conversations',
        data=body,
        method='POST',
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            resp = json.load(r)
            cid = resp.get('conversation_id', '(no id)')
            log.info(f'Conversation started: {cid}')
            state['last_trigger'] = time.time()
            return True
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()[:300]
        log.error(f'OpenHands returned HTTP {e.code}: {body_text}')
    except Exception as e:
        log.error(f'Could not reach OpenHands at {OPENHANDS_URL}: {e}')
        log.error('  Is OpenHands running?  Check OPENHANDS_URL in .env')
    return False


# ── Diff helper ────────────────────────────────────────────────────────────────

def diff(current: dict[str, str], previous: dict[str, str]) -> list[str]:
    changes = []
    for key, ts in current.items():
        if key not in previous:
            changes.append(f'NEW {key}')
        elif ts != previous[key]:
            changes.append(f'UPDATED {key}')
    for key in previous:
        if key not in current:
            changes.append(f'CLOSED {key}')
    return changes


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not GITHUB_TOKEN:
        log.error('GITHUB_TOKEN is not set. Add it to daemon/.env or export it.')
        sys.exit(1)

    log.info('OpenHands workflow daemon starting')
    log.info(f'  GitHub user : {GITHUB_USER}')
    log.info(f'  OpenHands   : {OPENHANDS_URL}')
    log.info(f'  Poll every  : {POLL_INTERVAL}s')
    log.info(f'  Cooldown    : {COOLDOWN}s between triggers')
    log.info(f'  State file  : {STATE_FILE}')

    state = load_state()
    first_run = not state['issues']

    while True:
        try:
            current = fetch_open_issues()

            if first_run:
                log.info(f'First run — seeding {len(current)} issue(s), no trigger fired')
                state['issues'] = current
                save_state(state)
                first_run = False
            else:
                changes = diff(current, state['issues'])
                if changes:
                    for c in changes:
                        log.info(f'  {c}')
                    trigger_openhands('; '.join(changes), state)
                    state['issues'] = current
                    save_state(state)
                else:
                    log.debug(f'Polled {len(current)} issue(s) — no changes')

        except Exception as e:
            log.error(f'Poll error: {e}')

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
