# Kent's VB — Virtual Browser

## Overview

A virtual browser web app that serves isolated private Chromium sessions per user via VNC/noVNC, with authentication, account management, device tracking, and admin features.

## Architecture

Single-file Python application (`startup`) — no frameworks, pure stdlib + Nix packages.

### Slot System (per-user isolation)
- **MAX_SLOTS = 20** concurrent browser sessions
- Each login allocates a slot with: Xvfb (display `:100+N`), fluxbox (window manager), x11vnc (port `5901+N`), Chromium (data dir `/tmp/chromium-data-N`), websockify (port `6001+N`)
- Logout/kick/idle timeout frees the slot
- WebSocket tunnel routes by auth token to the correct websockify port

### Key Files
- `startup` — entire application (server, HTML/JS frontend, session management)
- `acc` — `username=password` pairs (hot-reloaded each login, no restart needed)
- `AD Pass` — admin panel password (plain text, default: `admin123`)
- `devices.json` — device fingerprint tracking data

### Session Management
- Tokens stored in `localStorage` on client, in-memory `_sessions` dict on server
- Single-session-per-account: new login kicks old session
- Heartbeat every 25s (`/api/me`) detects kicks, also records activity for idle timeout
- **Idle timeout: 30 minutes** — inactive users are auto-freed

### Security
- Login rate limiting: 5 failed attempts = 30-second lockout per IP
- Single-session-per-account enforcement (new login kicks old)
- Admin panel behind separate password gate

### Performance Tuning (1 vCPU / 4 GiB RAM)
- MAX_SLOTS = 10 (realistic for 4GB RAM)
- x11vnc: threaded mode, xdamage, no xrecord/wireframe/xfixes, 3ms defer/wait
- Chromium: disk cache 64MB, renderer limit 3, V8 heap cap 256MB, GPU compositing off, smooth scrolling off, QUIC enabled, parallel downloads
- Display: 1024×640 @ 24-bit (35% less VNC data than 1280×720)
- WebSocket tunnel: 128KB buffer
- Static files: gzip compressed, 5-min cache
- No browser at boot — on-demand at login, ~3s server start
- Idle session timeout: 30 minutes auto-logout

### Admin Features
- Admin button visible only for username `Admin`
- Admin password gate → Device Tracker showing all user devices
- Active session management (kick users)

## Workflow
- `browser-startup` — runs `./startup`, serves on port 5000

## Dependencies (Nix)
- ungoogled-chromium, x11vnc, Xvfb, websockify, noVNC, fluxbox, Python 3.11
