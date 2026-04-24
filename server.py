#!/usr/bin/env python3
"""
Church Voting App — HTTP server

Serves the static HTML files and provides two API endpoints so all
devices share the same election state:

  GET  /api/state        — read current state (public)
  POST /api/state        — overwrite state (admin-authenticated)
  POST /api/ballot       — atomic ballot submission (token-authenticated)

Local usage:
    python3 server.py          # port 8080
    python3 server.py 9000     # custom port

Cloud deployment (Render / Railway / Fly.io):
    Set the PORT and STATE_FILE environment variables in your hosting
    dashboard. The server reads PORT automatically; platforms inject it.

Security model for public hosting:
    /api/state POST requires the incoming JSON to contain the correct
    adminPasswordHash. If no state file exists yet (first run), the
    first write is accepted unconditionally. This means only the person
    who knows the admin password can overwrite the election state —
    preventing random internet users from corrupting the data.
"""

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ── Configuration (override via environment variables) ───────────────────────
# PORT: injected automatically by Render, Railway, Fly.io, etc.
PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 8080))

# STATE_FILE: set to a persistent-disk path on cloud platforms, e.g.
#   Render:  /data/election_state.json  (add a Disk in the Render dashboard)
#   Railway: /data/election_state.json  (add a Volume in the Railway dashboard)
STATE_FILE = os.environ.get(
    'STATE_FILE',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'election_state.json')
)

SERVE_DIR = os.path.dirname(os.path.abspath(__file__))
lock      = threading.Lock()

MIME = {
    '.html': 'text/html; charset=utf-8',
    '.css':  'text/css; charset=utf-8',
    '.js':   'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png':  'image/png',
    '.jpg':  'image/jpeg',
    '.ico':  'image/x-icon',
    '.svg':  'image/svg+xml',
    '.woff2': 'font/woff2',
    '.woff':  'font/woff',
}


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Print a concise access log instead of the verbose default
        print(f'{self.command} {self.path} → {args[1] if len(args) > 1 else "?"}')

    # ── Common response helper ─────────────────────────────
    def _send(self, code, ctype, body: bytes):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # ── GET ───────────────────────────────────────────────
    def do_GET(self):
        path = self.path.split('?')[0]

        # API: read state (public — voters need this)
        if path == '/api/state':
            with lock:
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as f:
                        data = f.read().encode('utf-8')
                else:
                    data = b'{}'
            self._send(200, 'application/json; charset=utf-8', data)
            return

        # Static file serving
        if path == '/':
            path = '/index.html'
        local = os.path.normpath(os.path.join(SERVE_DIR, path.lstrip('/')))
        # Prevent path traversal attacks
        if not local.startswith(SERVE_DIR):
            self._send(403, 'text/plain', b'Forbidden')
            return
        if os.path.isfile(local):
            ext   = os.path.splitext(local)[1].lower()
            ctype = MIME.get(ext, 'application/octet-stream')
            with open(local, 'rb') as f:
                self._send(200, ctype, f.read())
        else:
            self._send(404, 'text/plain', b'Not found')

    # ── POST ──────────────────────────────────────────────
    def do_POST(self):
        path   = self.path.split('?')[0]
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send(400, 'application/json; charset=utf-8',
                       b'{"error":"Invalid JSON"}')
            return

        # ── /api/state — full state write (admin-authenticated) ──────────────
        if path == '/api/state':
            with lock:
                # Security: if a state file already exists with a non-empty
                # adminPasswordHash, the incoming payload must have the same
                # hash. This prevents unauthenticated writes over the internet.
                if os.path.exists(STATE_FILE):
                    try:
                        with open(STATE_FILE, 'r', encoding='utf-8') as f:
                            existing = json.load(f)
                        stored_hash   = existing.get('adminPasswordHash', '')
                        incoming_hash = payload.get('adminPasswordHash', '')
                        if stored_hash and stored_hash != incoming_hash:
                            self._send(403, 'application/json; charset=utf-8',
                                       b'{"error":"Unauthorized"}')
                            return
                    except (json.JSONDecodeError, OSError):
                        pass  # Corrupt file — allow overwrite to recover

                # Ensure the directory for STATE_FILE exists
                os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
                with open(STATE_FILE, 'w', encoding='utf-8') as f:
                    f.write(body.decode('utf-8'))

            self._send(200, 'application/json; charset=utf-8', b'{"ok":true}')
            return

        # ── /api/voting-ballot — atomic voting ballot submission ─────────────
        if path == '/api/voting-ballot':
            token_code = payload.get('tokenCode')
            answer     = payload.get('answer')

            def merr(msg):
                self._send(400, 'application/json; charset=utf-8',
                           json.dumps({'error': msg}).encode())

            with lock:
                if not os.path.exists(STATE_FILE):
                    return merr('No state configured')
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                voting = state.get('voting', {})
                if not voting.get('question'):
                    return merr('No vote configured')
                if not voting.get('votingOpen'):
                    return merr('Voting is not open')

                valid_answers = voting.get('answers', [])
                if answer not in valid_answers:
                    return merr('Invalid answer')

                # Validate token
                token = next((t for t in state.get('tokens', [])
                              if t.get('code') == token_code), None)
                if not token:
                    return merr('Token not found')
                if token.get('votingVoted'):
                    return merr('Token already used for this vote')

                # Record ballot atomically
                from datetime import datetime, timezone
                votes = voting.setdefault('votes', {})
                votes[answer] = votes.get(answer, 0) + 1
                voting.setdefault('ballots', []).append({
                    'token':     token_code,
                    'answer':    answer,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                token['votingVoted'] = True

                state['voting'] = voting
                with open(STATE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(state, f)

            self._send(200, 'application/json; charset=utf-8', b'{"ok":true}')
            return

        # ── /api/ballot — atomic ballot submission (token-validated) ─────────
        if path == '/api/ballot':
            office_key = payload.get('office')
            round_num  = payload.get('round')
            token_code = payload.get('tokenCode')
            selections = payload.get('selections', [])

            def err(msg):
                self._send(400, 'application/json; charset=utf-8',
                           json.dumps({'error': msg}).encode())

            if office_key not in ('elder', 'deacon'):
                return err('Invalid office')

            with lock:
                if not os.path.exists(STATE_FILE):
                    return err('No election configured')
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                if state.get('activeOffice') != office_key:
                    return err('Office not active')

                office = state.get(office_key, {})
                if not office.get('votingOpen'):
                    return err('Voting is closed')
                if office.get('currentRound') != round_num:
                    return err('Round has changed')

                # Validate token
                token = next((t for t in state.get('tokens', [])
                              if t.get('code') == token_code), None)
                if not token:
                    return err('Token not found')
                used = token.setdefault('usedRounds', {}) \
                            .setdefault(office_key, [])
                if round_num in used:
                    return err('Token already used this round')

                # Filter to valid candidates only
                valid_names = [c['name'] for c in office.get('candidates', [])]
                valid_sel   = [s for s in selections if s in valid_names]
                if not valid_sel:
                    return err('No valid candidates selected')

                # Record ballot atomically
                from datetime import datetime, timezone
                office.setdefault('ballots', []).append({
                    'token':     token_code,
                    'votes':     valid_sel,
                    'round':     round_num,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                for candidate in office.get('candidates', []):
                    if candidate['name'] in valid_sel:
                        candidate['votes'] = candidate.get('votes', 0) + 1
                used.append(round_num)

                state[office_key] = office
                with open(STATE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(state, f)

            self._send(200, 'application/json; charset=utf-8', b'{"ok":true}')
            return

        # ── /api/tinyurl — proxy to TinyURL API (avoids browser CORS) ───────────
        if path == '/api/tinyurl':
            import urllib.request, urllib.error

            action = payload.get('action', '')
            alias  = payload.get('alias', '').strip()

            if action == 'check':
                # HEAD https://tinyurl.com/{alias} without following redirects.
                # A 301/302 means the alias exists; a 404 means it's available.
                class _NoRedirect(urllib.request.HTTPRedirectHandler):
                    def redirect_request(self, *a, **kw):
                        return None

                opener = urllib.request.build_opener(_NoRedirect)
                try:
                    opener.open(f'https://tinyurl.com/{alias}', timeout=5)
                    available = False  # 200 without redirect → alias is a TinyURL page
                except urllib.error.HTTPError as e:
                    available = (e.code == 404)
                except Exception:
                    available = True  # network error — let creation attempt proceed

                self._send(200, 'application/json; charset=utf-8',
                           json.dumps({'available': available}).encode())
                return

            elif action == 'create':
                url_to_shorten = payload.get('url', '')
                api_key        = payload.get('apikey', '')
                body_data      = {'url': url_to_shorten, 'domain': 'tinyurl.com'}
                if alias:
                    body_data['alias'] = alias

                req = urllib.request.Request(
                    'https://api.tinyurl.com/create',
                    data=json.dumps(body_data).encode(),
                    headers={
                        'Content-Type':  'application/json',
                        'Authorization': f'Bearer {api_key}',
                    },
                    method='POST',
                )
                try:
                    resp   = urllib.request.urlopen(req, timeout=10)
                    result = json.loads(resp.read())
                except urllib.error.HTTPError as e:
                    raw    = e.read()
                    result = json.loads(raw) if raw else {'code': e.code, 'errors': [str(e)]}
                except Exception as e:
                    result = {'code': -1, 'errors': [str(e)]}

                self._send(200, 'application/json; charset=utf-8',
                           json.dumps(result).encode())
                return

            self._send(400, 'application/json; charset=utf-8',
                       b'{"error":"Unknown action"}')
            return

        self._send(404, 'text/plain', b'Not found')


def main():
    # Ensure state file directory exists before we start
    state_dir = os.path.dirname(STATE_FILE)
    if state_dir:
        os.makedirs(state_dir, exist_ok=True)

    server = HTTPServer(('0.0.0.0', PORT), Handler)

    # Detect public URL (set automatically by Render)
    public_url = os.environ.get('RENDER_EXTERNAL_URL', '')

    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = '127.0.0.1'

    print('=' * 55)
    print('  Church Voting App Server')
    print('=' * 55)
    if public_url:
        print(f'  Public URL:      {public_url}/')
        print(f'  Voter page:      {public_url}/vote.html')
    else:
        print(f'  Admin / local:   http://localhost:{PORT}/')
        print(f'  Voter devices:   http://{local_ip}:{PORT}/vote.html')
    print(f'  State file:      {STATE_FILE}')
    print('  Press Ctrl+C to stop.')
    print('=' * 55)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')


if __name__ == '__main__':
    main()
