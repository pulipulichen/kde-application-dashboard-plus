#!/usr/bin/env bash
set -euo pipefail
# Build prerequisites for Kubuntu 24.04 / Plasma 5.27. No desktop restart.
command -v apt-get >/dev/null || { echo 'Use Kubuntu 24.04, or install the README dependencies manually.' >&2; exit 1; }
sudo apt-get update
sudo apt-get install --no-install-recommends build-essential cmake qtbase5-dev qtdeclarative5-dev libkf5windowsystem-dev gettext python3 kpackagetool5 qml-module-qtquick-controls2
