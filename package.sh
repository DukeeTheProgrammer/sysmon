#!/bin/bash

################################################################################
# Package System Monitor for distribution
# Creates agent.tar.gz for Linux/macOS and agent_windows.zip for Windows
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================"
echo "              System Monitor - Package Builder"
echo "================================================================"
echo ""

# Create build directory
BUILD_DIR="$SCRIPT_DIR/build"
mkdir -p "$BUILD_DIR"

# Files to include
INCLUDE_FILES=(
    "rat_agent"
    "dashboard"
    "requirements.txt"
    "config.py"
)

echo "[INFO] Creating Linux/macOS package..."

# Create tarball for Linux/macOS
tar -czf "$BUILD_DIR/agent.tar.gz" \
    rat_agent/ \
    dashboard/ \
    requirements.txt \
    install \
    start.sh \
    README.md \
    2>/dev/null || true

echo "[OK] Created: $BUILD_DIR/agent.tar.gz ($(du -h "$BUILD_DIR/agent.tar.gz" | cut -f1))"

echo "[INFO] Creating Windows package..."

# Create zip for Windows (using zip if available)
if command -v zip &> /dev/null; then
    cd "$BUILD_DIR"
    rm -f agent_windows.zip
    cd "$SCRIPT_DIR"
    
    zip -r "$BUILD_DIR/agent_windows.zip" \
        rat_agent/ \
        dashboard/ \
        requirements.txt \
        install_windows.bat \
        start_windows.bat \
        README_WINDOWS.md \
        2>/dev/null || true
    
    echo "[OK] Created: $BUILD_DIR/agent_windows.zip ($(du -h "$BUILD_DIR/agent_windows.zip" | cut -f1))"
else
    echo "[WARN] zip not found, skipping Windows package"
    echo "[INFO] Install zip: sudo apt install zip"
fi

echo ""
echo "================================================================"
echo "                    Packaging Complete"
echo "================================================================"
echo ""
echo "Packages created in: $BUILD_DIR"
echo ""
echo "Next steps:"
echo "  1. Upload to GitHub:"
echo "     git add build/ && git commit -m 'Build packages' && git push"
echo ""
echo "  2. Or host on your server:"
echo "     cp build/* /var/www/html/"
echo ""
echo "  3. Update URLs in install scripts:"
echo "     GITHUB_USER=your_username"
echo "     GITHUB_REPO=your_repo"
echo ""
echo "================================================================"
