# Church Voting App

A browser-based voting application for Reformed church congregational meetings. Supports both **office bearer elections** (Elder and Deacon) and **congregational motion votes** (custom questions with custom answers). Runs on a local Python server with no internet connection required — all data is stored on the meeting laptop and shared in real time across all devices on the local Wi-Fi network.

---

## Features

### Office Bearer Elections
- Multi-round elections with automatic majority detection
- Separate, independent elections for Elder and Deacon offices
- Either or both offices can be configured — unconfigured offices are skipped automatically
- Digital voting via members' phones/tablets using unique 4-digit token codes
- Paper ballot entry station for members who prefer to vote on paper
- Printable token cards with QR codes
- Printable paper ballots

### Congregational Motion Voting
- Custom question with fully customisable answer options (e.g. In Favour / Against / Abstain)
- Chairman controls when voting opens and closes
- Live vote count dashboard for the chairman
- Same token system as the election — no separate cards required
- Single vote per member per motion

### General
- Two separate password-protected areas: admin (setup & control) and results (chairman only)
- Real-time updates on all control and dashboard screens
- Voter pages auto-update when rounds open, close, or state changes
- No internet required — runs entirely on a local network

---

## Files

| File | Purpose |
|---|---|
| `server.py` | Local Python HTTP server — serves the app and stores all shared state |
| `index.html` | Admin hub — Home, Election Setup, Round Control, Paper Ballot Entry, Election Dashboard, Motion Setup, Motion Control, Motion Dashboard |
| `vote.html` | Voter page — auto-detects whether an office bearer election or congregational vote is active and presents the appropriate ballot |
| `election_state.json` | Shared state file, created automatically on first save |
| `render.yaml` | One-click deployment config for Render.com |
| `requirements.txt` | No external dependencies (Python stdlib only) |
| `build_manual.py` | Generates `manual.docx` (requires `python-docx`) |
| `manual.docx` | Complete Word document user manual |

---

## Quick Start

**Requirements:** Python 3.8 or later. No packages to install.

```bash
# 1. Start the server
python3 server.py

# 2. Open the admin hub in a browser on the laptop
#    http://localhost:8080/

# 3. Share the voter URL with members (covers both elections and motion votes):
#    http://<your-laptop-ip>:8080/vote.html
```

The server prints the local IP address on startup. Voter URLs are also displayed on the relevant hub screens inside the app.

---

## How It Works

### Admin Hub (`index.html`)

The app opens on a home screen with two sections:

#### Office Bearer Election

| Screen | Access | Purpose |
|---|---|---|
| Election Hub | Open | Navigation to all election screens |
| Election Setup | Admin password | Configure nominees, tokens, passwords, voter URL |
| Round Control | Admin password | Open/close voting, monitor ballots, end rounds |
| Paper Ballot Entry | Open | Volunteer enters paper votes in real time |
| Election Dashboard | Results password | Chairman views live status and confidential results |

#### Congregational Motion

| Screen | Access | Purpose |
|---|---|---|
| Motion Hub | Open | Overview of current motion, navigation, voter URL |
| Motion Setup | Admin password | Enter question, add/remove answer options, set expected voters |
| Motion Control | Admin password | Open/close voting, live vote counts, mark complete |
| Motion Dashboard | Results password | Chairman read-only results view, auto-refreshes every 3s |

### Voter Pages

**`vote.html`** — Unified voter page. Automatically detects whether an office bearer election or congregational vote is currently active and presents the appropriate ballot. Members enter their token once; the page routes them to the correct flow and updates automatically as the meeting progresses.

### Passwords

| Password | Protects | Default |
|---|---|---|
| Admin password | Election Setup, Round Control, Motion Setup, Motion Control | `election2024` |
| Results password | Election Dashboard, Motion Dashboard | `results2024` |

> **Change both passwords before the meeting** in Election Setup → Settings tab.

---

## Election Flow

```
Election Setup → configure nominees, tokens, passwords
    ↓
Generate & Print Token Cards
    ↓
Round Control → Start Round 1
    ↓
Voting Open → members vote on phones or paper
    ↓
Close Voting → End Round
    ↓
Round Transition: confirm elected, select who advances
    ↓
Launch Next Round  ─── or ───  Complete This Office
    ↓                                   ↓
(repeat)                        Next office (if configured)
                                        ↓
                               Election Complete screen
                                        ↓
                          Chairman views Election Dashboard
```

## Motion Vote Flow

```
Motion Setup → enter question and answer options
    ↓
Motion Control → Open Voting
    ↓
Members open vote.html, enter token, select answer
    ↓
Motion Control → Close Voting
    ↓
Mark Motion Complete
    ↓
Chairman views Motion Dashboard
```

---

## Token System

- Each eligible voter receives one token card before the meeting
- Token cards include: congregation name, 4-digit code, QR code, and voter URL
- One token covers both the Elder and Deacon elections (all rounds) and any congregational motion votes
- Each token can only be used once per round per office, and once per motion
- Saving a new motion setup resets all token motion-vote records for a fresh vote

---

## API Endpoints

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/state` | GET | None | Read full shared state |
| `/api/state` | POST | `adminPasswordHash` in payload | Full state overwrite (admin) |
| `/api/ballot` | POST | Valid token + office + round | Submit election ballot (atomic) |
| `/api/motion-ballot` | POST | Valid token + answer | Submit motion vote (atomic) |

---

## Cloud Deployment (Render.com)

The app can be hosted publicly so voters access it over the internet instead of a local network.

1. Push this repository to GitHub
2. Go to [render.com](https://render.com) → **New → Blueprint**
3. Connect the repository — Render reads `render.yaml` automatically
4. Click **Apply** (takes ~2 minutes)
5. Your URL appears in the Render dashboard (e.g. `https://church-voting.onrender.com`)
6. In Election Setup → Settings, set the voter URL to `https://church-voting.onrender.com/vote.html`

**Note:** A persistent disk (Render Starter plan, ~$7/month) is recommended to ensure `election_state.json` survives restarts. The free plan is acceptable for a single meeting day as long as the service is not redeployed mid-session.

---

## Security

- Passwords are stored as SHA-256 hashes — never as plain text
- `POST /api/state` requires the correct `adminPasswordHash` in the payload — unauthenticated writes are rejected
- `POST /api/ballot` and `POST /api/motion-ballot` validate the token and state before writing — votes are applied atomically under a thread lock, preventing race conditions
- `election_state.json` is excluded from version control via `.gitignore`

---

## License

Private — for internal church use only.
