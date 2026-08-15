#!/usr/bin/env bash
# ============================================================================
# dev-desktop-daemon.sh — run `make dev-desktop` as a persistent launchd agent
# ============================================================================
# Keeps the formintA Tauri desktop dev app (Astro on :1420 + Rust backend)
# alive across terminal / Freebuff restarts. launchd owns the process, so it is
# NOT a child of the launching shell; `KeepAlive` restarts it whenever it is
# killed or crashes (but not on a clean quit).
#
# Usage:
#   scripts/dev/dev-desktop-daemon.sh             # install (or update) + start
#   scripts/dev/dev-desktop-daemon.sh stop        # stop + unload
#   scripts/dev/dev-desktop-daemon.sh status      # show launchd agent state
#   scripts/dev/dev-desktop-daemon.sh plist       # print the generated plist path
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)" # formintA/
LABEL="com.forminta.pos-dev-desktop"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST="$LAUNCH_AGENTS_DIR/$LABEL.plist"
LOG="/tmp/formintA-dev-desktop-daemon.log"

# Resolve the node bin dir (nvm puts node + pnpm there). Prefer PATH, else the
# newest nvm version. The plist bakes in this absolute PATH so launchd does not
# need a login shell / profile.
NODE_BIN="$(dirname "$(command -v node 2>/dev/null || true)")"
if [ -z "$NODE_BIN" ] || [ "$NODE_BIN" = "." ]; then
  NODE_BIN="$(ls -d "$HOME"/.nvm/versions/node/v*/bin 2>/dev/null | sort -V | tail -1 || true)"
fi
if [ -z "$NODE_BIN" ]; then
  echo "❌ node not found — install Node or export its bin dir on PATH." >&2
  exit 1
fi
# Tauri's CLI shells out to `cargo metadata`, so rustup's bin dir is required too.
CARGO_BIN="$(dirname "$(command -v cargo 2>/dev/null || true)")"
if [ -z "$CARGO_BIN" ] || [ "$CARGO_BIN" = "." ]; then
  CARGO_BIN="$HOME/.cargo/bin"
fi
PATH_VAL="$NODE_BIN:$CARGO_BIN:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

generate_plist() {
  mkdir -p "$LAUNCH_AGENTS_DIR"
  cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/make</string>
        <string>dev-desktop</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$PATH_VAL</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>StandardOutPath</key>
    <string>$LOG</string>
    <key>StandardErrorPath</key>
    <string>$LOG</string>
    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>
PLIST_EOF
}

case "${1:-start}" in
  start)
    generate_plist
    # Always reload from the freshly generated plist (idempotent).
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    if launchctl bootstrap "gui/$(id -u)" "$PLIST" 2>/dev/null; then
      echo "✅ launchd agent '$LABEL' bootstrapped — dev-desktop starting (log: $LOG)"
    else
      echo "⚠️  bootstrap failed — check: launchctl print gui/$(id -u)/$LABEL" >&2
      exit 1
    fi
    ;;
  stop)
    if launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null; then
      echo "🛑 agent '$LABEL' stopped and unloaded"
    else
      echo "ℹ️  agent '$LABEL' was not running"
    fi
    ;;
  status)
    launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | head -25 || echo "❌ agent '$LABEL' not loaded"
    ;;
  plist)
    echo "$PLIST"
    ;;
  *)
    echo "Usage: $0 [start|stop|status|plist]" >&2
    exit 1
    ;;
esac
