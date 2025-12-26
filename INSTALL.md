# Installation Guide

This guide will help you install all required dependencies for the FII Portfolio Manager.

## Quick Install (Automated)

Run the automated installation script:

```bash
./install-dependencies.sh
```

This script will install:
- ✅ Node.js 20.x (LTS)
- ✅ npm (package manager)
- ✅ Docker Engine
- ✅ Docker Compose

**Supported Operating Systems:**
- Ubuntu 20.04+ / Debian 11+
- Fedora 36+ / RHEL 8+ / CentOS 8+
- macOS (with Homebrew)

## What Gets Installed

### 1. Node.js and npm

**Version:** Node.js 20.x LTS
**Why needed:** Frontend development (React + Vite)

The script installs Node.js from the official NodeSource repository for the latest stable version.

### 2. Docker Engine

**Version:** Latest stable
**Why needed:** PostgreSQL and Redis containers (optional but recommended)

Docker provides an isolated environment for database services without affecting your system.

### 3. Docker Compose

**Version:** Latest stable (v2 plugin)
**Why needed:** Multi-container orchestration for PostgreSQL + Redis

Allows starting both database services with a single command.

## Manual Installation (Alternative)

If the automated script doesn't work or you prefer manual installation:

### Ubuntu/Debian

```bash
# Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Docker
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Fedora/RHEL

```bash
# Node.js and npm
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs

# Docker
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Node.js and npm
brew install node@20

# Docker Desktop (download and install manually)
# https://www.docker.com/products/docker-desktop
```

## Python Installation

Python is also required for the backend. Most Linux systems have Python pre-installed.

### Check Python Version

```bash
python3 --version  # Should be 3.11 or higher
```

### Install Python (if needed)

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-venv python3-pip
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip
```

**macOS:**
```bash
brew install python@3.11
```

## Verify Installation

After installation, verify everything is installed correctly:

```bash
# Node.js
node --version    # Should show v20.x.x
npm --version     # Should show 10.x.x

# Docker
docker --version  # Should show Docker version 24.x or higher
docker compose version  # Should show Docker Compose version v2.x

# Python
python3 --version # Should show Python 3.11.x or higher
```

## Post-Installation

### 1. Docker Group (Linux only)

If you just installed Docker, you need to activate the docker group:

```bash
# Option 1: Apply in current terminal
newgrp docker

# Option 2: Log out and log back in (system-wide)
```

Verify you can run Docker without sudo:
```bash
docker ps
```

### 2. Run Setup Wizard

After all dependencies are installed, run the setup wizard:

```bash
./setup-wizard.sh
```

This will:
- Check all prerequisites
- Let you choose database option (Docker, local PostgreSQL, or SQLite)
- Install project dependencies
- Create configuration files
- Run database migrations
- Provide next steps

## Troubleshooting

### Node.js Installation Failed

**Error:** `Unable to locate package nodejs`

**Solution:** Make sure you added the NodeSource repository:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get update
```

### Docker Permission Denied

**Error:** `permission denied while trying to connect to the Docker daemon socket`

**Solution:** Add user to docker group and re-login:
```bash
sudo usermod -aG docker $USER
newgrp docker
# Or log out and log back in
```

### Docker Service Not Running

**Error:** `Cannot connect to the Docker daemon`

**Solution:** Start Docker service:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### npm Command Not Found

**Error:** `npm: command not found` (but Node.js is installed)

**Solution:** npm is included with Node.js. Reinstall Node.js:
```bash
sudo apt-get install --reinstall nodejs
```

### Python Version Too Old

**Error:** `Python 3.7 is too old`

**Solution:** Install Python 3.11+:
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv

# Or use deadsnakes PPA for newer versions
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv
```

## Installation Flow

Here's the complete installation flow from scratch:

```bash
# 1. Clone the repository
git clone <repository-url>
cd fii

# 2. Install system dependencies
./install-dependencies.sh

# 3. Activate docker group (if needed)
newgrp docker

# 4. Run setup wizard
./setup-wizard.sh

# 5. Start the application
make start

# 6. Open browser
# http://localhost:5173
```

## Alternative: Without Docker

If you don't want to use Docker, you can install PostgreSQL locally:

See [SETUP_WITHOUT_DOCKER.md](SETUP_WITHOUT_DOCKER.md) for detailed instructions.

## Need Help?

- Check the [Quick Start Guide](QUICKSTART.md)
- Review [Setup Without Docker](SETUP_WITHOUT_DOCKER.md)
- See the [main README](README.md)
- Open an issue on GitHub

## System Requirements

### Minimum Requirements
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 10 GB free space
- **OS:** Ubuntu 20.04+, Debian 11+, Fedora 36+, macOS 12+

### Recommended Requirements
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Disk:** 20 GB free space (for Docker images and data)

## What's Next?

After installing dependencies:

1. ✅ Run setup wizard: `./setup-wizard.sh`
2. ✅ Create first user (wizard will guide you)
3. ✅ Start application: `make start`
4. ✅ Access frontend: http://localhost:5173
5. ✅ Login with your credentials

Happy coding! 🚀
