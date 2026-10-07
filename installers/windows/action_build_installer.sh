#!/usr/bin/env bash
# Builds the Windows installer with Inno Setup.
# Usage: bash installers/windows/action_build_installer.sh <version-tag>
set -euo pipefail

# Work from installers/windows so relative paths in installer.iss resolve
cd "$(dirname "${BASH_SOURCE[0]}")"

VERSION="${1#v}"
REVERSE_DOMAIN="com.glowingpixel.navigator"

DIST_STAGING="pkg_staging"
DIST_BASE="$DIST_STAGING/$REVERSE_DOMAIN"
DIST_LIB="$DIST_BASE/lib"
DIST_PKG="dist"

PACKAGE_BASENAME="mediapool_navigator_v${VERSION}_windows"   # Inno appends .exe

rm -rf "$DIST_STAGING" "$DIST_PKG"
mkdir -p "$DIST_PKG" "$DIST_LIB"

echo "Staging python package to $DIST_STAGING"
python -m pip install ../../ --target "$DIST_LIB"
# Same layout as the macOS installer: script at staging root, lib in the domain folder
cp "../../workflow_integration/Media Pool Navigator.py" "$DIST_STAGING/"

# Find iscc (preinstalled on GitHub's windows runners, but not always on PATH)
if command -v iscc >/dev/null 2>&1; then
	ISCC="iscc"
elif [ -x "/c/Program Files (x86)/Inno Setup 6/ISCC.exe" ]; then
	ISCC="/c/Program Files (x86)/Inno Setup 6/ISCC.exe"
else
	echo "iscc not found, installing Inno Setup"
	choco install innosetup -y --no-progress
	ISCC="/c/Program Files (x86)/Inno Setup 6/ISCC.exe"
fi

DIST_PKG_ABS="$(cygpath -m "$(pwd)/$DIST_PKG")"

echo "Building installer"
# MSYS2_ARG_CONV_EXCL stops Git Bash from mangling the /D /O /F switches
MSYS2_ARG_CONV_EXCL="*" "$ISCC" \
	"/DMyAppVersion=$VERSION" \
	"/O$DIST_PKG_ABS" \
	"/F$PACKAGE_BASENAME" \
	installer.iss

DIST_PKG_FULL="$DIST_PKG_ABS/$PACKAGE_BASENAME.exe"
[ -f "$DIST_PKG_FULL" ] || { echo "Installer not found at $DIST_PKG_FULL" >&2; exit 1; }

echo "Done! Written to $DIST_PKG_FULL"
echo "PKG_PATH=$DIST_PKG_FULL" >> "$GITHUB_ENV"