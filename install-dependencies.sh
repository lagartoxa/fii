#!/bin/bash

# FII Portfolio Manager - Dependency Installation Script
# Installs Docker, Docker Compose, Node.js, and npm

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}FII Portfolio Manager - Dependency Installer${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_VERSION=$VERSION_ID
else
    echo -e "${RED}Cannot detect OS. This script supports Ubuntu/Debian, Fedora/RHEL, and macOS.${NC}"
    exit 1
fi

echo -e "${YELLOW}Detected OS: $OS $OS_VERSION${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if running as root (for apt/dnf commands)
if [ "$EUID" -eq 0 ] && [ "$OS" != "darwin" ]; then
    echo -e "${RED}Please do not run this script as root (without sudo)${NC}"
    echo "Run it as a regular user. The script will ask for sudo when needed."
    exit 1
fi

echo -e "${YELLOW}This script will install:${NC}"
echo "  - Node.js 20.x (LTS)"
echo "  - npm (comes with Node.js)"
echo "  - Docker Engine"
echo "  - Docker Compose"
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""

# ============================================
# Install Node.js and npm
# ============================================

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Installing Node.js and npm${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

if command_exists node && command_exists npm; then
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION is already installed${NC}"
    echo -e "${GREEN}✓ npm $NPM_VERSION is already installed${NC}"
else
    case $OS in
        ubuntu|debian)
            echo -e "${YELLOW}Installing Node.js 20.x on Ubuntu/Debian...${NC}"

            # Add NodeSource repository
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

            # Install Node.js and npm
            sudo apt-get install -y nodejs

            echo -e "${GREEN}✓ Node.js and npm installed${NC}"
            ;;

        fedora|rhel|centos)
            echo -e "${YELLOW}Installing Node.js 20.x on Fedora/RHEL...${NC}"

            # Add NodeSource repository
            curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -

            # Install Node.js and npm
            sudo dnf install -y nodejs

            echo -e "${GREEN}✓ Node.js and npm installed${NC}"
            ;;

        darwin)
            echo -e "${YELLOW}Installing Node.js on macOS...${NC}"

            if command_exists brew; then
                brew install node@20
                echo -e "${GREEN}✓ Node.js and npm installed${NC}"
            else
                echo -e "${RED}Homebrew is not installed.${NC}"
                echo "Please install Homebrew first: https://brew.sh/"
                exit 1
            fi
            ;;

        *)
            echo -e "${RED}Unsupported OS: $OS${NC}"
            echo "Please install Node.js manually from: https://nodejs.org/"
            exit 1
            ;;
    esac
fi

# Verify Node.js installation
if command_exists node && command_exists npm; then
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ Verified: Node.js $NODE_VERSION${NC}"
    echo -e "${GREEN}✓ Verified: npm $NPM_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js installation failed${NC}"
    exit 1
fi

echo ""

# ============================================
# Install Docker
# ============================================

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Installing Docker${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ Docker is already installed: $DOCKER_VERSION${NC}"
else
    case $OS in
        ubuntu|debian)
            echo -e "${YELLOW}Installing Docker on Ubuntu/Debian...${NC}"

            # Update package index
            sudo apt-get update

            # Install prerequisites
            sudo apt-get install -y \
                ca-certificates \
                curl \
                gnupg \
                lsb-release

            # Add Docker's official GPG key
            sudo install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            sudo chmod a+r /etc/apt/keyrings/docker.gpg

            # Set up the repository
            echo \
              "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
              $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

            # Install Docker Engine
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

            echo -e "${GREEN}✓ Docker installed${NC}"
            ;;

        fedora|rhel|centos)
            echo -e "${YELLOW}Installing Docker on Fedora/RHEL...${NC}"

            # Remove old versions
            sudo dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine 2>/dev/null || true

            # Install prerequisites
            sudo dnf install -y dnf-plugins-core

            # Add Docker repository
            sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

            # Install Docker Engine
            sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

            echo -e "${GREEN}✓ Docker installed${NC}"
            ;;

        darwin)
            echo -e "${YELLOW}Installing Docker on macOS...${NC}"
            echo ""
            echo -e "${YELLOW}For macOS, please download and install Docker Desktop manually:${NC}"
            echo "  https://www.docker.com/products/docker-desktop"
            echo ""
            echo "After installing Docker Desktop:"
            echo "  1. Open Docker Desktop"
            echo "  2. Wait for it to start"
            echo "  3. Run this script again to verify installation"
            exit 0
            ;;

        *)
            echo -e "${RED}Unsupported OS: $OS${NC}"
            echo "Please install Docker manually from: https://docs.docker.com/get-docker/"
            exit 1
            ;;
    esac
fi

echo ""

# ============================================
# Configure Docker
# ============================================

if [ "$OS" != "darwin" ]; then
    echo -e "${YELLOW}Configuring Docker...${NC}"

    # Start Docker service
    sudo systemctl start docker
    sudo systemctl enable docker

    # Add current user to docker group
    if ! groups $USER | grep -q docker; then
        echo -e "${YELLOW}Adding user to docker group...${NC}"
        sudo usermod -aG docker $USER
        echo -e "${YELLOW}Note: You need to log out and log back in for group changes to take effect${NC}"
        echo -e "${YELLOW}Or run: newgrp docker${NC}"
    fi

    echo -e "${GREEN}✓ Docker configured${NC}"
fi

echo ""

# ============================================
# Verify Docker Compose
# ============================================

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Verifying Docker Compose${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

if command_exists docker; then
    # Check for docker compose (new syntax)
    if docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version --short)
        echo -e "${GREEN}✓ Docker Compose (plugin) is available: v$COMPOSE_VERSION${NC}"
    # Check for docker-compose (old syntax)
    elif command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        echo -e "${GREEN}✓ Docker Compose (standalone) is available: v$COMPOSE_VERSION${NC}"
    else
        echo -e "${YELLOW}Installing Docker Compose...${NC}"

        case $OS in
            ubuntu|debian|fedora|rhel|centos)
                # Install Docker Compose plugin (should have been installed with Docker)
                sudo apt-get install -y docker-compose-plugin 2>/dev/null || \
                sudo dnf install -y docker-compose-plugin 2>/dev/null || {
                    # Fallback to standalone installation
                    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
                    sudo curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    sudo chmod +x /usr/local/bin/docker-compose
                }
                echo -e "${GREEN}✓ Docker Compose installed${NC}"
                ;;
        esac
    fi
fi

echo ""

# ============================================
# Final Verification
# ============================================

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Installation Summary${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

ERRORS=0

# Check Node.js
if command_exists node; then
    echo -e "${GREEN}✓ Node.js: $(node --version)${NC}"
else
    echo -e "${RED}✗ Node.js: Not installed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check npm
if command_exists npm; then
    echo -e "${GREEN}✓ npm: $(npm --version)${NC}"
else
    echo -e "${RED}✗ npm: Not installed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker
if command_exists docker; then
    echo -e "${GREEN}✓ Docker: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)${NC}"
else
    echo -e "${RED}✗ Docker: Not installed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker Compose
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose: v$(docker compose version --short)${NC}"
elif command_exists docker-compose; then
    echo -e "${GREEN}✓ Docker Compose: $(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)${NC}"
else
    echo -e "${RED}✗ Docker Compose: Not installed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Python
if command_exists python3; then
    echo -e "${GREEN}✓ Python: $(python3 --version | cut -d' ' -f2)${NC}"
else
    echo -e "${YELLOW}⚠ Python: Not installed (required for backend)${NC}"
    echo "  Install with: sudo apt install python3 python3-venv python3-pip"
fi

echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}✓ All dependencies installed successfully!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo ""

    if ! groups $USER | grep -q docker; then
        echo -e "${YELLOW}1. Activate docker group (choose one):${NC}"
        echo "   ${BLUE}newgrp docker${NC}  # Apply in current terminal"
        echo "   ${BLUE}# OR log out and log back in${NC}  # Apply system-wide"
        echo ""
        echo -e "${YELLOW}2. Run the setup wizard:${NC}"
    else
        echo -e "${YELLOW}1. Run the setup wizard:${NC}"
    fi

    echo "   ${BLUE}./setup-wizard.sh${NC}"
    echo ""
    echo -e "${YELLOW}Or follow the quick start guide:${NC}"
    echo "   ${BLUE}cat QUICKSTART.md${NC}"
    echo ""
else
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}Installation completed with errors${NC}"
    echo -e "${RED}============================================${NC}"
    echo ""
    echo "Please review the errors above and install missing dependencies manually."
    exit 1
fi
