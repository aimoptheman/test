#!/usr/bin/env python3
"""
GitHub -> OpenHands Workflow Daemon

Polls GitHub for issue activity across all repos owned by GITHUB_USER.
When a new or updated issue is detected, triggers a local OpenHands run.

Two trigger modes — set one in .env:

  TRIGGER_CMD   Shell command to run (for CLI / Docker mode)
                e.g.  docker run --rm -e LLM_API_KEY=... openhands/openhands:latest \\
                        python -m openhands.core.main -t "run workflow"

  OPENHANDS_URL HTTP API base URL (for server / GUI mode)
                e.g.  http://localhost:3000

If both are set, TRIGGER_CMD takes priority.

Other env vars (via .env or environment):

  GITHUB_TOKEN      GitHub PAT with repo scope    (required)
  GITHUB_USER       GitHub username / org          (default: aimoptheman)
  POLL_INTERVAL     Seconds between polls          (default: 60)
  COOLDOWN          Min seconds between triggers   (default: 300)
  STATE_FILE        Path for persisted state       (default: .daemon_state.json)
"""

import json
import logging
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


# ── Config ─────────────────────────────────────────────────────────────────────

def _env(key: str, default: str = '') -> str:
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
OPENHANDS_URL = _env('OPENHANDS_URL', '')
TRIGGER_CMD   = _env('TRIGGER_CMD', '')
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
        repos = _gh(f'/user/repos?per_page=100&page={page}&type=owner')
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


# ── Trigger ────────────────────────────────────────────────────────────────────

def trigger(reason: str, state: dict) -> bool:
    since = time.time() - state.get('last_trigger', 0.0)
    if since < COOLDOWN:
        log.info(f'Cooldown: {int(COOLDOWN - since)}s left — skipping ({reason})')
        return False

    if TRIGGER_CMD:
        return _trigger_cmd(reason, state)
    elif OPENHANDS_URL:
        return _trigger_http(reason, state)
    else:
        log.error('Neither TRIGGER_CMD nor OPENHANDS_URL is set in .env')
        return False


def _trigger_cmd(reason: str, state: dict) -> bool:
    log.info(f'Running trigger command — {reason}')
    log.info(f'  $ {TRIGGER_CMD}')
    try:
        # Run detached so the daemon keeps polling while OpenHands works
        subprocess.Popen(
            TRIGGER_CMD,
            shell=True,
            stdout=open(Path(__file__).parent / 'openhands.log', 'a'),
            stderr=subprocess.STDOUT,
        )
        log.info('Process launched (output -> daemon/openhands.log)')
        state['last_trigger'] = time.time()
        return True
    except Exception as e:
        log.error(f'Failed to launch trigger command: {e}')
        return False


def _trigger_http(reason: str, state: dict) -> bool:
    log.info(f'Triggering OpenHands via HTTP — {reason}')
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
            log.info(f'Conversation started: {resp.get("conversation_id", resp)}')
            state['last_trigger'] = time.time()
            return True
    except urllib.error.HTTPError as e:
        log.error(f'OpenHands HTTP {e.code}: {e.read().decode()[:300]}')
    except Exception as e:
        log.error(f'Could not reach OpenHands at {OPENHANDS_URL}: {e}')
    return False


# ── Diff ───────────────────────────────────────────────────────────────────────

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
        log.error('GITHUB_TOKEN is not set.')
        sys.exit(1)
    if not TRIGGER_CMD and not OPENHANDS_URL:
        log.error('Set either TRIGGER_CMD or OPENHANDS_URL in daemon/.env')
        log.error('  CLI/Docker mode  ->  TRIGGER_CMD=docker run ...')
        log.error('  Server/GUI mode  ->  OPENHANDS_URL=http://localhost:3000')
        sys.exit(1)

    mode = f'CMD: {TRIGGER_CMD[:60]}' if TRIGGER_CMD else f'HTTP: {OPENHANDS_URL}'
    log.info('OpenHands workflow daemon starting')
    log.info(f'  GitHub user : {GITHUB_USER}')
    log.info(f'  Trigger     : {mode}')
    log.info(f'  Poll every  : {POLL_INTERVAL}s')
    log.info(f'  Cooldown    : {COOLDOWN}s between triggers')

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
                    trigger('; '.join(changes), state)
                    state['issues'] = current
                    save_state(state)
                else:
                    log.info(f'Polled {len(current)} issue(s) — no changes')
        except Exception as e:
            log.error(f'Poll error: {e}')

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
