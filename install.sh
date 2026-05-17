#!/bin/bash
# xfmix quick setup - installs Pure Data and configures systemd

echo "╔════════════════════════════════════════════╗"
echo "║  xfmix Setup                               ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "This script needs your password to install system packages."
echo "It will install: Pure Data, puredata-extra"
echo ""

# Run the full setup
exec bash "$(dirname "$0")/setup-xfmix.sh"
