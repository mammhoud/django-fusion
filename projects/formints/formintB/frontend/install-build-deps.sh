#!/bin/bash

set -e

echo "🚀 Installing Build Dependencies for POS"
echo "=================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Update package list
echo -e "${YELLOW}📦 Updating package list...${NC}"
sudo apt update

# Base build tools and Tauri dependencies
echo -e "${YELLOW}📦 Installing base build tools and Tauri dependencies...${NC}"
sudo apt install -y \
  curl \
  wget \
  file \
  build-essential \
  libssl-dev \
  pkg-config \
  libgtk-3-dev \
  libwebkit2gtk-4.1-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  patchelf \
  libsoup-3.0-dev \
  libjavascriptcoregtk-4.1-dev

# Cross-compilation tools for Windows
echo -e "${YELLOW}📦 Installing MinGW for Windows cross-compilation...${NC}"
sudo apt install -y \
  mingw-w64 \
  gcc-mingw-w64 \
  g++-mingw-w64 \
  clang-17

# Cross-compilation tools for ARM
echo -e "${YELLOW}📦 Installing ARM cross-compilation tools...${NC}"
sudo apt install -y \
  gcc-aarch64-linux-gnu \
  g++-aarch64-linux-gnu \
  gcc-arm-linux-gnueabihf \
  g++-arm-linux-gnueabihf \
  crossbuild-essential-arm64 \
  crossbuild-essential-armhf

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
else
    echo -e "${GREEN}✅ Node.js already installed: $(node --version)${NC}"
fi

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}📦 Installing pnpm...${NC}"
    npm install -g pnpm
else
    echo -e "${GREEN}✅ pnpm already installed: $(pnpm --version)${NC}"
fi

# Check if Rust is installed
if ! command -v rustc &> /dev/null; then
    echo -e "${YELLOW}🦀 Installing Rust...${NC}"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo -e "${GREEN}✅ Rust already installed: $(rustc --version)${NC}"
fi

# Ensure cargo is in PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Add Rust compilation targets
echo -e "${YELLOW}🎯 Adding Rust compilation targets...${NC}"
rustup target add \
  x86_64-unknown-linux-gnu \
  aarch64-unknown-linux-gnu \
  armv7-unknown-linux-gnueabihf \
  x86_64-pc-windows-gnu \
  aarch64-linux-android \
  armv7-linux-androideabi \
  i686-linux-android \
  x86_64-linux-android

echo ""
echo -e "${GREEN}✅ All dependencies installed successfully!${NC}"
echo ""
echo "📋 Installed components:"
echo "   - Node.js: $(node --version)"
echo "   - pnpm: $(pnpm --version)"
echo "   - Rust: $(rustc --version)"
echo "   - MinGW: $(x86_64-w64-mingw32-gcc --version | head -n1)"
echo "   - ARM64 GCC: $(aarch64-linux-gnu-gcc --version | head -n1)"
echo "   - ARMv7 GCC: $(arm-linux-gnueabihf-gcc --version | head -n1)"
echo ""
echo "🎯 Installed Rust targets:"
rustup target list --installed
echo ""
echo "📱 Optional: To build for Android, install Android Studio:"
echo "   https://developer.android.com/studio"
echo ""
echo "🍎 Optional: To build for macOS/iOS, you need macOS with Xcode"
echo ""
echo -e "${GREEN}🎉 Ready to build! Run:${NC}"
echo "   cd $(pwd)"
echo "   pnpm install"
echo "   pnpm build:desktop"
echo ""

