#!/usr/bin/env python3
"""
Board Voting App — HTTP server

Serves the static HTML files and provides API endpoints so all
devices share the same election state:

  GET  /api/state          — read current state (public)
  POST /api/state          — overwrite state (admin-authenticated)
  POST /api/ballot         — atomic ballot submission (token-authenticated)
  POST /api/voting-ballot  — atomic congregational vote submission

Local usage:
    python3 server.py          # port 8080
    python3 server.py 9000     # custom port

Cloud deployment (Render / Railway / Fly.io):
    Set the PORT and STATE_FILE environment variables in your hosting
    dashboard. The server reads PORT automatically; platforms inject it.

Security model for public hosting:
    /api/state POST requires the incoming JSON to contain the correct
    adminPasswordHash. If no state file exists yet (first run), the
    first write is accepted unconditionally.
"""

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ── Configuration (override via environment variables) ───────────────────────
PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 8080))

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
        print(f'{self.command} {self.path} → {args[1] if len(args) > 1 else "?"}')

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

        if path == '/api/state':
            with lock:
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r', encoding='utf-8') as f:
                        data = f.read().encode('utf-8')
                else:
                    data = b'{}'
            self._send(200, 'application/json; charset=utf-8', data)
            return

        if path == '/':
            path = '/index.html'
        local = os.path.normpath(os.path.join(SERVE_DIR, path.lstrip('/')))
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
                        pass

                os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
                with open(STATE_FILE, 'w', encoding='utf-8') as f:
                    f.write(body.decode('utf-8'))

            self._send(200, 'application/json; charset=utf-8', b'{"ok":true}')
            return

        # ── /api/voting-ballot — atomic congregational vote submission ────────
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

                token = next((t for t in state.get('tokens', [])
                              if t.get('code') == token_code), None)
                if not token:
                    return merr('Token not found')
                if token.get('votingVoted'):
                    return merr('Token already used for this vote')

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

        # ── /api/ballot — atomic board election ballot submission ─────────────
        if path == '/api/ballot':
            round_num  = payload.get('round')
            token_code = payload.get('tokenCode')
            selections = payload.get('selections', [])

            def err(msg):
                self._send(400, 'application/json; charset=utf-8',
                           json.dumps({'error': msg}).encode())

            with lock:
                if not os.path.exists(STATE_FILE):
                    return err('No election configured')
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                election = state.get('election', {})
                if not election.get('votingOpen'):
                    return err('Voting is closed')
                if election.get('currentRound') != round_num:
                    return err('Round has changed')

                # Validate token
                token = next((t for t in state.get('tokens', [])
                              if t.get('code') == token_code), None)
                if not token:
                    return err('Token not found')

                # usedRounds is now a flat list of round numbers
                used = token.setdefault('usedRounds', [])
                if round_num in used:
                    return err('Token already used this round')

                # Filter to valid candidates only
                valid_names = [c['name'] for c in election.get('candidates', [])]
                valid_sel   = [s for s in selections if s in valid_names]
                if not valid_sel:
                    return err('No valid candidates selected')

                # Record ballot atomically
                from datetime import datetime, timezone
                election.setdefault('ballots', []).append({
                    'token':     token_code,
                    'votes':     valid_sel,
                    'round':     round_num,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                for candidate in election.get('candidates', []):
                    if candidate['name'] in valid_sel:
                        candidate['votes'] = candidate.get('votes', 0) + 1
                used.append(round_num)

                state['election'] = election
                with open(STATE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(state, f)

            self._send(200, 'application/json; charset=utf-8', b'{"ok":true}')
            return

        # ── /api/tinyurl — proxy to TinyURL API (avoids browser CORS) ────────
        if path == '/api/tinyurl':
            import urllib.request, urllib.error

            action = payload.get('action', '')
            alias  = payload.get('alias', '').strip()

            if action == 'check':
                class _NoRedirect(urllib.request.HTTPRedirectHandler):
                    def redirect_request(self, *a, **kw):
                        return None

                opener = urllib.request.build_opener(_NoRedirect)
                try:
                    opener.open(f'https://tinyurl.com/{alias}', timeout=5)
                    available = False
                except urllib.error.HTTPError as e:
                    available = (e.code == 404)
                except Exception:
                    available = True

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
    state_dir = os.path.dirname(STATE_FILE)
    if state_dir:
        os.makedirs(state_dir, exist_ok=True)

    server = HTTPServer(('0.0.0.0', PORT), Handler)

    public_url = os.environ.get('RENDER_EXTERNAL_URL', '')

    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = '127.0.0.1'

    print('=' * 55)
    print('  Board Voting App Server')
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
