# Changelog

All notable changes to the Board Voting App are documented here.

---

## [3.0.2] — 2026-04-25
### Changed
- **Colour theme updated** — new palette throughout both `index.html` and `vote.html`:
  - Primary `#6d776e` (sage green) replaces navy `#1a2744`
  - Background `#faf9f8` (warm off-white) replaces cream `#f8f5ef`
  - Accent `#ece7e4` (warm taupe) replaces gold `#b8942a`/`#d4aa3a`
  - All derived variables (tints, borders, tile hover states, election palette) updated to match
  - SVG icon strokes, print card styles, inline badge/alert colours, and `applyTheme()` fallbacks all updated

---

## [3.0.1] — 2026-04-25
### Removed
- **Congregational vote feature removed entirely** — the app now handles only board elections
  - Deleted `/api/voting-ballot` server endpoint
  - Removed all voting screens and JS functions (`renderVotingHub`, `renderVotingSetup`, `renderVotingControl`, `renderVotingDashboard`, paper ballot voting, etc.)
  - Removed `voting` state object, `votingPasswordHash`, `votingVoted` token field, and all related login routing from `index.html` and `vote.html`
  - Voter page (`vote.html`) simplified to three modes: `election`, `election-complete`, `idle`

---

## [3.0.0] — 2026-04-25
### Changed
- **Forked from Church Voting App and converted to generic Board Voting App**
  - All church-specific fields removed: elder/deacon distinction, congregation name, denomination
  - Single `election` object replaces the dual elder/deacon offices
  - `org` (Organisation Name) and `electionName` replace church-specific branding fields
  - Admin default password changed from `churchvoting` to `boardvoting`
  - App renamed throughout UI, server startup banner, and documentation

---

## [2.8.5] — 2026-04-21
### Changed
- **Split admin and election passwords** — App Settings is now protected by the **Admin Password** (default: `churchvoting`); Election Setup and Round Control are protected by a new **Election Password** (default: `election2024`). Both passwords are managed in App Settings → Access Passwords.
- Login prompts for Election Setup / Round Control now say "election password" instead of "admin password".
### Added
- **`electionPasswordHash`** state field — new password specifically for election access. On first run, initialised to the `election2024` default (or migrated from the previous admin password if it matched the old default).

---

## [2.8.4] — 2026-04-21
### Fixed
- **App Settings is now password-protected** — clicking "⚙ Settings" on the home screen now requires the admin password before the settings screen is shown, consistent with Election Setup and Round Control access control.

---

## [2.8.3] — 2026-04-21
### Fixed / Added
- **Voter page (vote.html) now applies App Settings theme** — primary colour, secondary colour, and heading font are read from state and applied via CSS custom properties on page load
- **Voter page header shows church logo** if one is uploaded in App Settings; falls back to the cross icon if none set
- **Voter page subtitle shows denomination** (e.g. "Free Reformed · 21 April 2026") when configured
- **Voter page heading font** uses `--heading-font` CSS var (Playfair Display / Tahoma / Arial) consistently across title, token input, and headings
- **Header text colour on voter page adapts** to primary colour luminance — dark primary gets dark text, light primary keeps white text in the card gradient

---

## [2.8.2] — 2026-04-21
### Fixed
- **Tile text contrast on light secondary colours** — tile accent (title) now uses the primary colour on light tiles instead of a darkened shade of the secondary, ensuring strong contrast; description text uses a properly dark opacity value
- **Back/home button contrast** — all nav-header back/home ghost buttons now use `--nav-back-color` and `--nav-back-border` CSS variables, computed from primary colour luminance (dark on light primary, muted light on dark primary)
- **Home screen subtitle and footer note** — `.landing-sub` and `.landing-note` now use `--primary-sub` and `--primary-note` CSS vars that flip between dark/light opacity based on primary colour brightness
- **Settings link** on home screen now adapts with `--nav-back-color`

---

## [2.8.1] — 2026-04-21
### Fixed
- **Tiles/nav cards now use the secondary theme colour** — `.home-tile` and `.nav-card` backgrounds are driven by `--tile-bg` (set to the secondary colour in App Settings) instead of the hardcoded navy-mid value.
- **Adaptive text colour on tiles** — tile text, accent and description colours are computed from the secondary colour luminance, so light secondary colours get dark text and dark secondary colours keep white text.
- **Primary colour text adaptation** — `--primary-text` is computed from the primary colour luminance; the home screen body text inherits it.

---

## [2.8.0] — 2026-04-21
### Added
- **App Settings page** — new dedicated settings screen accessible via a subtle "⚙ Settings" link at the bottom of the home screen. Contains:
  - **Church Identity**: congregation name, denomination (Free Reformed / United Reformed), church logo upload, primary and secondary colour pickers, heading font selector (Playfair Display / Tahoma / Arial)
  - **Integration**: TinyURL API key (moved from Voter Tokens screen)
  - **Access Passwords**: all six app passwords consolidated in one place (App, Admin, Results, Congregational Voting, Paper Ballot, Voter Tokens)
- **Church logo support** — upload a logo image; it is stored in state and displayed on the home screen, replacing the cross icon
- **Custom colours** — primary and secondary hex colour pickers update the app's CSS variables (`--navy`, `--gold`) at runtime
- **Custom heading font** — font choice applies immediately via CSS custom property
- **Home screen branding** — congregation name and denomination are shown as a subtitle when configured
### Changed
- **Congregation name** moved from Election Setup → Details to App Settings (no duplication)
- **All passwords** moved from their respective screens to App Settings (removed from Election Setup → Settings tab and Voting Setup)
- **TinyURL API key** moved from Voter Tokens screen to App Settings; Voter Tokens now links to App Settings for the key
- Default password warnings updated to reference "App Settings" instead of "Election Setup → Settings"

---

## [2.7.2] — 2026-04-19
### Fixed
- **Voter page: "voting open" screen persists after congregational vote is closed** — the `voting-done`/`voting-already-voted` watchdog now transitions immediately to the thank-you (`voting-complete`) screen when the officer closes or completes the congregational vote, without waiting for a full reset.

---

## [2.7.1] — 2026-04-19
### Fixed
- **Voter page: "Voting Open" status persists after officer closes vote on voting-done screen** — the `voting-done`/`voting-already-voted` watchdog now also detects when `voting.complete` is set (transitioning to the complete screen) and when `votingOpen` changes (triggering a re-render so the status pill updates immediately).

---

## [2.7.0] — 2026-04-19
### Added
- **Election Setup → Settings: custom completion message** — officers can now enter a custom thank-you message that replaces the default "Thank you for participating…" heading on the voter completion screen. Leave blank to keep the default.
- **Election Setup → Settings: feedback survey link** — an optional URL can be configured; if provided, a "📋 Complete Feedback Survey" button is shown on the voter completion screen. The button is hidden when no URL is set.
### Fixed
- **Voter page: voting-ballot screen not reacting when officer closes congregational vote** — introduced a dedicated `ballotPoller` variable for the `voting-ballot` state, independent of the shared `waitingPoller`. Any residual `waitingPoller` from a prior state can no longer block ballot-close detection from starting.

---

## [2.6.11] — 2026-04-19
### Fixed
- **Voter page: voting-ballot screen not reacting when officer closes congregational vote** — the `voting-ballot` state now uses a dedicated `ballotPoller` variable (independent of the shared `waitingPoller`) to watch for voting close, question reset, or vote complete. Previously, any residual `waitingPoller` from an earlier state would block the ballot poller from starting, leaving the voter stuck on the ballot screen with "Voting Open" showing.

---

## [2.6.10] — 2026-04-19
### Fixed
- **Voter Tokens: "No active round" shown during congregational voting** — the stats and chip grid now show Voted/Not yet voted counts when the congregational vote is open, instead of the "No active round" placeholder. Token chips are highlighted as used when a voter has cast their congregational vote.
- **Voter page: token re-entry required after election completes and congregational vote opens** — when a voter was on the waiting screen (token already entered, waiting for voting to open) and the officer opened the congregational vote, the poller was falling through to the token entry screen. The poller now detects this case and carries the existing token straight to the voting ballot, matching the carry-forward behaviour from the election-complete screen.
- **Voter page: ballot screen not reacting when officer closes congregational vote** — when transitioning from `election-complete` to `voting-ballot`, the `waitingPoller` from the election-complete branch was not cleared, preventing the voting-ballot poller from starting. Closing the vote therefore never triggered a transition to the waiting screen.
- **Voter page: waiting screen shows "Voting Not Yet Open" after vote is closed** — `renderWaitingState()` now checks whether any votes or paper ballots have been cast; if so, it shows "Voting Round Closed" with appropriate subtext instead of "Voting Not Yet Open".
- **Voter Tokens: used token count not updating automatically** — added 3-second polling interval to the Voter Tokens screen so stats and chip grid refresh live while the screen is open.

---

## [2.6.9] — 2026-04-19
### Fixed
- **Voter Tokens: used token count not updating automatically** — the tokens screen had no polling interval. A 3-second interval now refreshes the stats and token chip grid while the screen is active, keeping the Used/Available counts current as voters cast ballots.

---

## [2.6.8] — 2026-04-19
### Fixed
- **Paper Ballot Entry: congregational vote question shown before voting opened** — the unified paper ballot screen was displaying the voting section whenever a question was configured, regardless of whether voting was open. `hasVoting` now also requires `voting.votingOpen` to be true, so the section only appears once the officer opens the congregational vote.

---

## [2.6.7] — 2026-04-19
### Changed
- **Voter Tokens: TinyURL API key label updated** — label now reads "API Key (default provided - enter your own if required)" instead of referencing tinyurl.com/app/dev.

---

## [2.6.6] — 2026-04-19
### Changed
- **Voter Tokens: TinyURL Options panel moved above Custom URL field** — the alias and API key inputs now appear before the custom URL input rather than after it.
- **Voter Tokens: TinyURL auto-saves on create** — clicking "Create TinyURL" now immediately saves the generated URL as the custom URL; no separate "Save URL" click required. Status message updated to confirm the URL has been saved.

---

## [2.6.5] — 2026-04-19
### Changed
- **Voter Tokens: TinyURL API key pre-filled** — a default API key is now built into the app and used automatically. The key field pre-fills on load; users can enter and save their own key to override it.

---

## [2.6.4] — 2026-04-19
### Changed
- **Voter Tokens: TinyURL alias support added** — a new "TinyURL Options" panel in the Voting Page URL card adds an optional Custom Alias field (min 5 chars) and an API Key field (saved to `localStorage`, never stored in app state). Without an alias the button uses the free tinyurl.com legacy endpoint as before. With an alias, the request is proxied through `server.py` (`/api/tinyurl`) to avoid CORS: it first checks alias availability via a no-redirect HEAD probe of `https://tinyurl.com/{alias}` (taken if 301/302, available if 404), then creates via `POST https://api.tinyurl.com/create` with Bearer auth. Step-by-step status messages guide through the process. Free API key available at tinyurl.com/app/dev.

---

## [2.6.3] — 2026-04-19
### Changed
- **Voter Tokens: TinyURL reverted to simple free API** — removed the tinyurl.ee authenticated API, API key field, and custom alias input. The "Create TinyURL" button uses the free tinyurl.com API with no account or key required, generating a random short URL and pre-filling the custom URL field.

---

## [2.6.2] — 2026-04-19
### Changed
- **Voter Tokens: TinyURL integration upgraded** — switched from the unauthenticated tinyurl.com API to the tinyurl.ee authenticated API (Bearer token). The Voting Page URL card now includes a TinyURL Configuration panel with an API key field (saved to `localStorage`, never synced to the server) and an optional custom alias input. Before creating, the alias is checked for availability via `GET /api/url/{alias}`; if the alias is already taken, an error is shown immediately. Status messages guide through each step (blue = in progress, green = success, red = error). The API key pre-fills automatically on return visits.

---

## [2.6.1] — 2026-04-14
### Fixed
- **Voter page: congregational vote complete message** — the "voting complete" screen now reads "Thank you for your vote. The voting is now complete. The chairman will announce the results." using the same Playfair Display heading style as the election-complete screen.

---

## [2.6.0] — 2026-04-14
### Fixed
- **Voter page: congregational voting ballot not reacting to close/reset** — voters on the voting ballot screen now automatically transition to the "Voting Round Closed" waiting screen when the officer closes voting, and return to the idle/token screen when the vote is reset. Previously the `voting-ballot` state had no poller, so voters were stuck.
- **Voter page: voting-done / already-voted not reacting to vote reset** — after submitting a congregational vote, voters now return to the idle screen automatically if the officer resets the vote (question cleared).
### Changed
- **Voting Control: consolidated control bar** — Open Voting, Close Voting, and Mark Complete are now in a single control bar, mirroring the Round Control layout. "Reset & New Vote" appears in the control bar when the vote is complete.
- **Voting Control: targeted auto-refresh** — the 3-second interval now updates only the stats and results rows (not the full screen), matching the Round Control approach and eliminating unnecessary re-renders.
- **Voting Dashboard: mirrored Election Dashboard layout** — the dashboard now uses the same card/header/body structure, status section with status pills, info strip (Expected Voters + Absentee Votes), and result row style as the Election Dashboard.

---

## [2.5.0] — 2026-04-14
### Added
- **Landing page password protection** — the admin hub now requires an access password (`votevote2024` by default) on first load each session. A warning banner is shown until the default is changed. "Change App Password" added to Election Setup → Settings.
- **Absentee checkbox on congregational vote paper ballot** — paper ballot entries for the congregational vote can now be marked as absentee; shown in the ballot log with a count summary.
### Fixed
- **Dashboard auto-refresh** — both Election Dashboard and Voting Dashboard (and Voting Control) were creating an exponential number of timers on each render, causing freezes. Fixed with polling guard flags so only one interval runs per screen at a time.
- **Congregational vote expected total** — absentee count is now added to the expected voters denominator in Voting Control and Voting Dashboard statistics, matching the majority threshold calculation.
- **Round Control "End Round" confirmation** — clicking End Round now shows a confirmation dialog with the ballot count before proceeding to the transition screen.
- **Voting Control formatting** — changed to use the same `rc-header`/`rc-body` CSS structure as Round Control, giving a consistent look and feel. Header subtitle now shows church name and context.
- **Voter: show voted answer** — after submitting a congregational vote, the "Vote Recorded" screen now shows the question and the answer the voter selected.

---

## [2.4.1] — 2026-04-13
### Fixed
- Voter page: after the office bearer election completes and the congregational vote opens, the voter no longer has to re-enter their token — the token entered for the election is carried forward automatically
- Voting Control and Voting Dashboard: answer rows now show a green "✓ Majority" badge when the vote count meets or exceeds the configured majority threshold; the progress bar turns green and the threshold is noted below the bar

---

## [2.4.0] — 2026-04-13
### Added
- **Paper Ballot Entry is now password-protected** (default: `paperentry2024`) — the home screen tile now prompts for the paper ballot password before opening the entry station
- **Change Paper Ballot Password** option added to both Election Setup → Settings tab and Voting Setup screen
- **Absentee Voters** field added to Voting Setup — enter the number of absentee votes to include in the majority calculation
- **Majority Threshold** configuration added to Voting Setup — three options: 50%+1 (simple majority), 75% of eligible voters, or a custom percentage. The computed required vote count is shown as a stat in Voting Control and Voting Dashboard

---

## [2.3.0] — 2026-04-13
### Added
- **Paper Ballot Entry** tile added to the home screen — a unified volunteer station that auto-detects whether an office bearer election or a congregational vote is active and shows the appropriate entry form. No password required.
### Changed
- Paper Ballot Entry removed from the Office Bearer Election hub and the Congregational Vote hub — now accessed exclusively from the home screen
- `screen-voting-paper` removed; its content merged into the unified `screen-paper-ballot` screen
- Extracted `updatePBLog()` helper; introduced `renderUnifiedPaperBallot()`, `unifiedPBKey()`, and `startUnifiedPaperBallotPoller()` to coordinate both ballot types

---

## [2.2.2] — 2026-04-13
### Changed
- Voter page: after the office bearer election completes, the thank-you screen now automatically transitions to the congregational vote flow (token entry or waiting screen) when a congregational vote is configured — no manual refresh needed. The election-complete screen polls every 3 s; entering the voting flow resets the token entry so voters authenticate fresh for the vote.

---

## [2.2.1] — 2026-04-13
### Changed
- Voting Page URL setting (custom URL override + QR code) moved from Election Setup → Settings tab into the Voter Tokens screen — it lives alongside token generation and token cards since they all share the same voter URL

---

## [2.2.0] — 2026-04-13
### Changed
- `vote.html` and `motion-vote.html` merged into a single voter page (`vote.html`) — the page auto-detects whether an office bearer election or congregational vote is currently active and presents the appropriate ballot. Voters use one URL for all voting types.
- `motion-vote.html` deleted; `votingVoteUrl()` removed from `index.html` — both the election voter URL and the voting voter URL now point to `vote.html`
### Fixed
- Congregational vote submission was calling `/api/motion-ballot` (which does not exist); corrected to `/api/voting-ballot`

---

## [2.1.2] — 2026-04-13
### Added
- Voter Tokens is now its own password-protected section (accessed via a third home tile using the tokens password), with token generation, stats, token chip grid, Print Token Cards, and a Change Tokens Password form
### Changed
- Purple accent colour removed from all Congregational Vote screens and replaced with navy (`#1a2744` / `#243460`) — affects Voting Control stat numbers, result bars, Voting Dashboard vote counts and bars, ballot card office label, and paper ballot answer selection highlight
- Print Token Cards button (previously its own password prompt) is now simply inside the Voter Tokens screen, which is already behind the tokens password — no double-authentication needed

---

## [2.1.1] — 2026-04-13
### Added
- Print Token Cards button is now password-protected (default: `tokens2024`) — clicking it opens the standard login screen with a new tokens password. A fourth independent password level has been added alongside admin, voting, and results.
### Fixed
- Elder Election and Deacon Election tabs in Election Setup were blank due to a `ReferenceError`: `names` (undefined) was used in the ballot-printing template string instead of `(o.nominees || []).length`. Corrected to use the nominees array from state.

---

## [2.1.0] — 2026-04-13
### Added
- Voter Tokens section moved to main home screen — accessible before choosing a section, with token generation, stats, chip display, and Print Token Cards button
- Tokens are now explicitly shared across both Office Bearer Election and Congregational Vote (description updated on home screen)
- Separate voting password (default: `voting2024`) for Voting Setup and Voting Control, independent of the admin password and the results password
- "Change Voting Password" card added to Voting Setup screen
- Print paper ballots for Elder and Deacon elections moved from the Tokens tab into each office's setup tab (available in both the pre-round setup state and the in-progress state)
- "Print Voting Ballots" button added to Voting Setup screen
- `showHome()` navigation helper that refreshes the token display when returning to the home screen
### Changed
- Default congregational vote answer options changed from "In Favour / Against / Abstain" to **"In favour" / "Not in favour"**
- Voting question placeholder updated to generic wording ("Do you agree with the proposed resolution?")
- Tokens tab removed from Election Setup entirely (moved to home screen)
- Voting Setup and Voting Control now require the voting password instead of the admin password
### Fixed
- `migrateState()` condition was always false (`parsed.voting && !parsed.voting`) — corrected to `parsed.motion && !parsed.voting`
- `updateVPBLog()` referenced an undefined variable `voting` (leftover from the motion→voting rename); corrected to `const voting = state.voting`

---

## [2.0.0] — 2026-04-13
### Added
- Home landing screen with two tiles: **Office Bearer Election** and **Congregational Vote** — replaces the old single-section landing page
- Full **Congregational Vote** feature:
  - Voting Hub with status overview card and navigation to all voting screens
  - Voting Setup — configure question text, answer options (add/remove), and expected voters
  - Voting Control — open/close voting, live vote counts with bar chart, mark complete, reset
  - Voting Dashboard (results-password protected) — chairman read-only results view, auto-refreshes every 3 s
  - Voting Paper Ballot Entry — volunteer station for members who cannot use the digital system; 4 s auto-refresh log
  - Voter page (`motion-vote.html`) — token entry, answer selection, done/waiting/already-voted/complete states with 3 s polling
  - Server endpoint `/api/voting-ballot` — atomic, token-authenticated vote submission under thread lock
- Token system extended: each token now covers both election rounds and congregational votes via a `votingVoted` flag; saving a new vote setup resets all `votingVoted` flags for a fresh vote
### Changed
- App renamed from **Church Office Bearer Election** to **Church Voting App**
- All internal code identifiers renamed from `motion`/`Motion` to `voting`/`Voting` across `index.html`, `motion-vote.html`, and `server.py`
- `migrateState()` added in `load()` for backward compatibility with existing `election_state.json` files that still use the old `motion` key or `motionVoted` token flag
### Infrastructure
- `README.md` fully rewritten for "Church Voting App" covering both feature sets, the motion vote flow diagram, and all four API endpoints

---

## [1.2.5] — 2026-04-08
### Changed
- Election Dashboard: replaced the small "Delete All Election Data" ghost button with a full Danger Zone section (matching the one in Election Setup → Settings tab) — includes a red heading, explanatory text, and a prominent red "Reset All Election Data" button. Only shown after the election is complete.

---

## [1.2.4] — 2026-04-07
### Fixed
- Voter page: when a new round opened, authenticated voters (token already entered) were sent straight to the ballot without any confirmation prompt. The waiting screen now shows the same "Vote Now" notification button used on the done screen — the voter must tap it to proceed to the ballot. `determineView()` reverted to always returning `'token'` when voting is open; the `waitingPoller` intercepts the case where `enteredToken` is set and calls `checkForNextBallot()` to inject the prompt instead.

---

## [1.2.3] — 2026-04-07
### Fixed
- Voter page: when a new round opened after the voter had already authenticated, they were shown the token entry screen instead of the ballot. `determineView()` always returned `'token'` when voting was open, ignoring that `enteredToken` was already set. It now returns `'ballot'` directly when the voter's token is known and they haven't yet voted in the current round. `selectedCandidates` is also cleared when the `waitingPoller` transitions to ballot, preventing stale selections carrying over.

---

## [1.2.2] — 2026-04-07
### Fixed
- Voter page: after submitting a vote, closing the round left the voter stuck on the "Vote Submitted" confirmation screen instead of switching to "Voting Round Closed". `checkForNextBallot()` was returning early when `!office.votingOpen`, doing nothing. It now transitions to the `waiting` state when voting closes (so the voter sees the round-closed screen) and to the `complete` state when the election finishes entirely.

---

## [1.2.1] — 2026-04-07
### Fixed
- Voter page: ballot screen still switched back to token entry because the `waitingPoller` started during the token state was never stopped before `view = 'ballot'` was set. The `if (!waitingPoller)` guard in the ballot branch then prevented the ballot-specific poller from starting, so the old token-state poller fired, called `determineView()`, got `'token'`, and switched the view back. Fixed by explicitly clearing `waitingPoller` before setting `view = 'ballot'` in both `handleTokenSubmit()` and `goToNextBallot()`.

---

## [1.2.0] — 2026-04-07
### Fixed
- Voter page: after entering a token the ballot screen was immediately replaced by the token entry screen. The v1.1.9 fix added 'ballot' to the general waitingPoller which calls `determineView()` — that function correctly returns 'token' (voting open, not yet done), causing the switch back. Fixed by giving the ballot state its own dedicated poller that only watches for `votingOpen` going false, never calling `determineView()`.

---

## [1.1.9] — 2026-04-07
### Fixed
- Voter page: voters on the ballot screen (after entering their token, while selecting candidates) were not automatically redirected to the "Voting Round Closed" screen when the officer closed voting. The `ballot` state is now included in the `waitingPoller` so all active screens update within 3 seconds when voting status changes.

---

## [1.1.8] — 2026-04-07
### Fixed
- Election Setup: "▶ Round Control" button was not appearing after saving an office setup because `saveOfficeSetup()` only called `renderOfficeSetup()`, not the full `renderSetup()` which contains the button visibility logic. Button now shown immediately on save.

---

## [1.1.7] — 2026-04-07
### Added
- Election Setup header: "▶ Round Control" shortcut button appears as soon as at least one office is configured, allowing the officer to switch directly to Round Control without going back to the landing page.
### Fixed
- Voter page: voters who had already submitted a ballot were being shown the "Voting Round Closed" waiting screen when the round closed. The `done` state check in `determineView()` now runs before the `votingOpen` check, so voted voters stay on the confirmation screen regardless of round status.

---

## [1.1.6] — 2026-04-06
### Changed
- Election Dashboard info strip: removed "Total Eligible" pill; updated "Absentee Votes" label to include "(Round 1 only)"
### Added
- Election Dashboard: current round card (active + awaiting transition) now shows ballot counters — Ballots In, Paper, Absentee (Round 1 only), Expected, and Turnout %
- Election Dashboard: each committed round in Round History now shows full counters — total ballots, paper, absentee, turnout %, majority required, and all candidate vote counts

---

## [1.1.5] — 2026-04-06
### Added
- Election Dashboard: new election information strip showing Expected Voters (attending), Absentee Votes, and Total Eligible — displayed between the status section and the results.

---

## [1.1.4] — 2026-04-06
### Added
- Election Dashboard now shows Round 1 pre-round information when the election is configured but voting has not yet started: nominee list, positions to fill, votes per voter, and majority required. Previously showed "No results yet."

---

## [1.1.3] — 2026-04-06
### Changed
- Next round now starts with voting **closed** when the officer clicks "Launch Next Round". The officer must explicitly click Open Voting in Round Control, giving time to announce the new round before votes can be submitted.

---

## [1.1.2] — 2026-04-06
### Fixed
- Election Dashboard was not showing live round results while voting was open. The `isActiveRound` condition was missing — only the post-round "awaiting transition" state was handled. Dashboard now shows the current round results card in all three states: voting open (green tag), voting closed awaiting transition (amber tag), and after transition (committed history).

---

## [1.1.1] — 2026-04-06
### Added
- Election Dashboard status header now shows "Majority required: N" pill next to the round and voting status, using the correct round-aware threshold
- Election Dashboard shows full round results (vote counts, bars, majority badges) immediately when a round is ended, before the election officer processes the transition — labelled "Round N Results — Awaiting transition"

---

## [1.1.0] — 2026-04-06
### Added
- Absentee vote support: enter number of absentee votes in Election Setup → Details tab
- Absentee checkbox on Paper Ballot Entry screen (Round 1 only)
- "Absentee" badge on each absentee ballot in the paper ballot log, with count summary
- Absentee stat box on Round Control screen (Round 1 only)
- Majority threshold is now round-aware: Round 1 uses expected attending voters + absentee count; Round 2 and later use attending voters only
- Details tab majority display shows both thresholds when absentees are configured

---

## [1.0.2] — 2026-04-06
### Fixed
- Token card QR code was blank on the first print attempt; `QRCode.js` renders asynchronously via an internal `setTimeout`, so reading the canvas immediately after construction returned an empty element. `getQrDataUrl()` now returns a Promise with a short delay and `printTokenCards()` is async.

---

## [1.0.1] — 2026-04-06
### Added
- Version number displayed in the footer of the admin hub (`index.html`)

---

## [1.0.0] — 2026-04-06
### Initial release
- Multi-round elections for Elder and Deacon offices with automatic majority detection
- Digital voting via unique 4-digit token codes on members' phones/tablets
- Paper ballot entry station with ballot log, edit, and delete last entry
- Absentee-aware majority calculation (added in v1.1.0; baseline majority used expected voters)
- Round Control with real-time vote count updates (3-second poll)
- Round Transition: auto-suggest elected candidates based on majority, configurable advancing candidates
- Skip unconfigured offices automatically in the election flow
- Election Complete screen showing elected names by office (no vote counts)
- Election Dashboard (results password protected) with delete option after election is complete
- Voter page with full state machine: token → ballot → done/waiting → complete
- Paper Ballot Entry with 4-second auto-refresh and structural change detection
- Two password-protected areas: admin and results (SHA-256 hashed, WebCrypto with pure-JS fallback)
- Token cards with QR codes, printable paper ballots
- Local Python server (`server.py`) with `/api/state` and `/api/ballot` endpoints
- Atomic ballot submission under thread lock — supports concurrent voters
- Cloud deployment support via Render.com (`render.yaml`)
- No internet required for local use; no external dependencies beyond Google Fonts and QRCode.js CDN
