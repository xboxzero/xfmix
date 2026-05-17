#!/bin/bash
# xfmix click-launcher: start the server if not already running, then open
# the UI in a browser. Safe to double-click repeatedly.

set -u
XFMIX_DIR="$(cd "$(dirname "$0")" && pwd)"
URL="http://localhost:8866"
LOGFILE="${TMPDIR:-/tmp}/xfmix.log"

is_up() {
    # Pure-bash TCP probe so we don't depend on netcat/curl flavors.
    (exec 3<>/dev/tcp/127.0.0.1/8866) 2>/dev/null && { exec 3<&-; exec 3>&-; return 0; } || return 1
}

if ! is_up; then
    cd "$XFMIX_DIR"
    nohup python3 server.py > "$LOGFILE" 2>&1 &
    disown
    # Wait up to ~8s for the HTTP port to come up.
    for _ in $(seq 1 40); do
        sleep 0.2
        if is_up; then break; fi
    done
fi

# Pick a browser; prefer Chromium kiosk-style, fall back to xdg-open.
if command -v chromium >/dev/null 2>&1; then
    exec chromium --new-window "$URL" >/dev/null 2>&1
elif command -v chromium-browser >/dev/null 2>&1; then
    exec chromium-browser --new-window "$URL" >/dev/null 2>&1
elif command -v xdg-open >/dev/null 2>&1; then
    exec xdg-open "$URL" >/dev/null 2>&1
else
    echo "No browser found. Open $URL manually."
fi
