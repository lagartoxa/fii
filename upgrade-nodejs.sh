#!/bin/bash

# Upgrade Node.js to version 20.x (required for Vite/Frontend)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Node.js Upgrade Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check current Node.js version
if command -v node &> /dev/null; then
    CURRENT_VERSION=$(node --version)
    echo -e "${YELLOW}Current Node.js version: $CURRENT_VERSION${NC}"
else
    echo -e "${YELLOW}Node.js is not installed${NC}"
    CURRENT_VERSION="none"
fi

echo ""
echo -e "${YELLOW}This script will upgrade Node.js to version 20.x (LTS)${NC}"
echo -e "${YELLOW}Vite (frontend build tool) requires Node.js 18.0.0 or higher${NC}"
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Upgrade cancelled."
    exit 0
fi

echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}Cannot detect OS${NC}"
    exit 1
fi

case $OS in
    ubuntu|debian)
        echo -e "${BLUE}Upgrading Node.js on Ubuntu/Debian...${NC}"

        # Remove old Node.js
        if [ "$CURRENT_VERSION" != "none" ]; then
            echo -e "${YELLOW}Removing old Node.js version...${NC}"
            sudo apt-get remove -y nodejs npm 2>/dev/null || true
            sudo apt-get autoremove -y 2>/dev/null || true
        fi

        # Remove old NodeSource repository if exists
        sudo rm -f /etc/apt/sources.list.d/nodesource.list 2>/dev/null || true

        # Add NodeSource repository for Node.js 20.x
        echo -e "${YELLOW}Adding NodeSource repository...${NC}"
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

        # Install Node.js
        echo -e "${YELLOW}Installing Node.js 20.x...${NC}"
        sudo apt-get install -y nodejs

        echo -e "${GREEN}✓ Node.js upgraded successfully!${NC}"
        ;;

    fedora|rhel|centos)
        echo -e "${BLUE}Upgrading Node.js on Fedora/RHEL...${NC}"

        # Remove old Node.js
        if [ "$CURRENT_VERSION" != "none" ]; then
            echo -e "${YELLOW}Removing old Node.js version...${NC}"
            sudo dnf remove -y nodejs npm 2>/dev/null || true
        fi

        # Remove old NodeSource repository if exists
        sudo rm -f /etc/yum.repos.d/nodesource-*.repo 2>/dev/null || true

        # Add NodeSource repository for Node.js 20.x
        echo -e "${YELLOW}Adding NodeSource repository...${NC}"
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -

        # Install Node.js
        echo -e "${YELLOW}Installing Node.js 20.x...${NC}"
        sudo dnf install -y nodejs

        echo -e "${GREEN}✓ Node.js upgraded successfully!${NC}"
        ;;

    darwin)
        echo -e "${BLUE}Upgrading Node.js on macOS...${NC}"

        if command -v brew &> /dev/null; then
            # Uninstall old version
            if [ "$CURRENT_VERSION" != "none" ]; then
                echo -e "${YELLOW}Removing old Node.js version...${NC}"
                brew uninstall node 2>/dev/null || true
            fi

            # Install Node.js 20
            echo -e "${YELLOW}Installing Node.js 20.x...${NC}"
            brew install node@20
            brew link --force node@20

            echo -e "${GREEN}✓ Node.js upgraded successfully!${NC}"
        else
            echo -e "${RED}Homebrew is not installed${NC}"
            echo "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
        ;;

    *)
        echo -e "${RED}Unsupported OS: $OS${NC}"
        echo "Please upgrade Node.js manually to version 20.x"
        echo "Download from: https://nodejs.org/"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verify installation
if command -v node &> /dev/null; then
    NEW_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)

    echo -e "${GREEN}✓ Node.js: $NEW_VERSION${NC}"
    echo -e "${GREEN}✓ npm: $NPM_VERSION${NC}"

    # Check if version is 18 or higher
    MAJOR_VERSION=$(echo $NEW_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$MAJOR_VERSION" -ge 18 ]; then
        echo ""
        echo -e "${GREEN}✓ Node.js version is compatible with Vite!${NC}"
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo "1. Reinstall frontend dependencies:"
        echo "   ${BLUE}cd frontend${NC}"
        echo "   ${BLUE}rm -rf node_modules package-lock.json${NC}"
        echo "   ${BLUE}npm install${NC}"
        echo "   ${BLUE}cd ..${NC}"
        echo ""
        echo "2. Start the application:"
        echo "   ${BLUE}make start${NC}"
        echo ""
    else
        echo ""
        echo -e "${RED}✗ Node.js version is still too old (need 18+)${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Node.js installation failed${NC}"
    exit 1
fi
