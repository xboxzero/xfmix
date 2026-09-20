#!/bin/bash
# xfmix setup script - Run this to install xfmix system-wide

set -e

XFMIX_HOME="/home/xero/xfmix"
XFMIX_BIN="/usr/local/bin/xfmix"
SERVICE_FILE="$HOME/.config/systemd/user/xfmix.service"

echo "╔════════════════════════════════════════════╗"
echo "║  xfmix Setup & Installation                ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
python3 --version
echo ""

# Install system packages (requires sudo)
echo "📦 Installing system dependencies..."
echo "   (This will prompt for your password)"
echo ""
sudo apt-get update -qq
sudo apt-get install -y puredata puredata-extra pipewire-jack pipewire-alsa ffmpeg
echo "✓ Pure Data, pipewire-jack, pipewire-alsa, ffmpeg installed"
echo ""

# Create systemd user directory
mkdir -p "$HOME/.config/systemd/user"

# Install systemd service
echo "⚙️  Installing systemd service..."
cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=xfmix - Computer Music History Synthesizer
Documentation=https://github.com/xboxzero/xfmix
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=%h/xfmix
ExecStart=/usr/bin/python3 %h/xfmix/server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
StandardInput=null

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
echo "✓ Systemd service installed"
echo ""

# Install terminal shortcut
echo "🔗 Installing terminal shortcut..."
sudo install -m 755 /tmp/xfmix-shortcut.sh /usr/local/bin/xfmix
echo "✓ Terminal shortcut installed"
echo ""

# Make server executable
chmod +x "$XFMIX_HOME/server.py"

echo "╔════════════════════════════════════════════╗"
echo "║  Setup Complete! 🎉                        ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📍 To start xfmix:"
echo "   $ xfmix"
echo ""
echo "   Then open http://<pi-ip>:8866 in Safari"
echo ""
echo "📖 Available commands:"
echo "   xfmix             - Start xfmix (or check status)"
echo "   xfmix stop        - Stop the service"
echo "   xfmix status      - Check service status"
echo "   xfmix log         - View live logs (Ctrl+C to exit)"
echo "   xfmix restart     - Restart the service"
echo ""
echo "📚 Documentation: https://github.com/xboxzero/xfmix"
echo ""
