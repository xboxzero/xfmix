#!/bin/bash
set -e

XFMIX_HOME="$HOME/xfmix"
XFMIX_BIN="/usr/local/bin/xfmix"
SERVICE_FILE="$HOME/.config/systemd/user/xfmix.service"

echo "╔════════════════════════════════════════════╗"
echo "║  xfmix Installation                        ║"
echo "╚════════════════════════════════════════════╝"

# Check Python version
echo "✓ Checking Python..."
python3 --version

# Install system dependencies
echo "✓ Installing system dependencies..."
sudo -n apt-get update -qq 2>/dev/null || echo "⚠ apt update skipped"
sudo -n apt-get install -y -qq puredata puredata-extra python3-aiohttp python3-websockets 2>/dev/null || {
    echo "⚠ Some packages failed to install (may already be installed)"
    echo "  Try: sudo apt install puredata puredata-extra python3-aiohttp python3-websockets"
}

# Create service directory
mkdir -p "$HOME/.config/systemd/user"

# Install systemd service
echo "✓ Installing systemd service..."
cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=xfmix - Computer Music Synthesizer

[Service]
WorkingDirectory=%h/xfmix
ExecStart=/usr/bin/python3 %h/xfmix/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload

# Create terminal shortcut
echo "✓ Creating terminal shortcut..."
sudo tee "$XFMIX_BIN" > /dev/null << 'EOF'
#!/bin/bash
# xfmix - Computer music synthesizer starter

case "$1" in
  stop)
    systemctl --user stop xfmix
    echo "xfmix stopped"
    ;;
  status)
    systemctl --user status xfmix
    ;;
  log)
    journalctl --user -fu xfmix
    ;;
  start)
    systemctl --user start xfmix
    IP=$(hostname -I | awk '{print $1}')
    sleep 1
    echo "✓ xfmix started at http://$IP:8866"
    ;;
  *)
    systemctl --user start xfmix
    sleep 1
    IP=$(hostname -I | awk '{print $1}')
    echo "✓ xfmix started at http://$IP:8866"
    echo "  Run 'xfmix log' to see output"
    echo "  Run 'xfmix stop' to stop"
    ;;
esac
EOF
sudo chmod +x "$XFMIX_BIN"

# Make server executable
chmod +x "$XFMIX_HOME/server.py"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  Installation Complete!                    ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "To start xfmix:"
echo "  $ xfmix"
echo ""
echo "To view logs:"
echo "  $ xfmix log"
echo ""
echo "To stop:"
echo "  $ xfmix stop"
echo ""
echo "To check status:"
echo "  $ xfmix status"
echo ""
