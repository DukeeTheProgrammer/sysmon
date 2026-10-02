#!/bin/bash

################################################################################
# Install System Tools for Remote Screen Control
#
# This script installs xdotool and imagemagick required for:
# - Mouse movement and clicking
# - Screen capture fallback
# - Keyboard input
################################################################################

echo "================================================================"
echo "       Installing Remote Screen Control Tools"
echo "================================================================"
echo ""

# Check if sudo works without password
if sudo -n true 2>/dev/null; then
    SUDO_CMD="sudo"
else
    SUDO_CMD="sudo"
    echo "Note: You may need to enter your sudo password"
    echo ""
fi

# Detect package manager
if command -v apt-get &> /dev/null; then
    echo "Detected: Debian/Ubuntu/Debian-based system"
    echo "Installing with apt-get..."
    $SUDO_CMD apt-get update -qq
    $SUDO_CMD apt-get install -y xdotool imagemagick
elif command -v dnf &> /dev/null; then
    echo "Detected: RHEL/Fedora/CentOS system"
    echo "Installing with dnf..."
    $SUDO_CMD dnf install -y xdotool ImageMagick
elif command -v pacman &> /dev/null; then
    echo "Detected: Arch Linux"
    echo "Installing with pacman..."
    $SUDO_CMD pacman -S --noconfirm xdotool imagemagick
elif command -v zypper &> /dev/null; then
    echo "Detected: openSUSE"
    echo "Installing with zypper..."
    $SUDO_CMD zypper install -y xdotool ImageMagick
else
    echo "Unknown package manager. Please install manually:"
    echo "  Debian/Ubuntu: sudo apt-get install xdotool imagemagick"
    echo "  RHEL/Fedora:   sudo dnf install xdotool ImageMagick"
    echo "  Arch:          sudo pacman -S xdotool imagemagick"
    exit 1
fi

echo ""
echo "================================================================"
echo "                    Installation Complete"
echo "================================================================"
echo ""

# Verify installation
echo "Verifying installation..."

if command -v xdotool &> /dev/null; then
    echo "✓ xdotool installed: $(which xdotool)"
else
    echo "✗ xdotool not found"
fi

if command -v import &> /dev/null; then
    echo "✓ ImageMagick installed: $(which import)"
else
    echo "✗ ImageMagick not found"
fi

echo ""
echo "Test xdotool:"
xdotool --version 2>/dev/null || echo "xdotool test failed"

echo ""
echo "Remote screen control is now ready!"
echo "Restart the dashboard to apply changes:"
echo "  cd /home/dukeetheprogrammer/rat && ./install.sh"
echo ""
