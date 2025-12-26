#!/bin/bash
#
# Test Environment Setup Script
# This script sets up the virtual environment and installs test dependencies
#

set -e  # Exit on error

echo "=========================================="
echo "FII Portfolio Test Environment Setup"
echo "=========================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "app/main.py" ]; then
    echo "Error: This script must be run from the backend directory"
    echo "Usage: cd /home/parallels/projects/fii/backend && bash setup_tests.sh"
    exit 1
fi

# Step 1: Check for python3-venv
echo "Step 1: Checking for python3-venv..."
if ! dpkg -l | grep -q python3.10-venv; then
    echo "❌ python3-venv is not installed"
    echo ""
    echo "Please install it with:"
    echo "  sudo apt update"
    echo "  sudo apt install python3.10-venv"
    echo ""
    exit 1
else
    echo "✅ python3-venv is installed"
fi

# Step 2: Remove old venv if it exists
if [ -d "venv" ]; then
    echo ""
    echo "Step 2: Removing old virtual environment..."
    rm -rf venv
    echo "✅ Old venv removed"
fi

# Step 3: Create new virtual environment
echo ""
echo "Step 3: Creating new virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Step 4: Activate and upgrade pip
echo ""
echo "Step 4: Upgrading pip..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"

# Step 5: Install production dependencies
echo ""
echo "Step 5: Installing production dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ Production dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping"
fi

# Step 6: Install test dependencies
echo ""
echo "Step 6: Installing test dependencies..."
pip install pytest==8.3.4 \
            pytest-asyncio==0.24.0 \
            pytest-cov==6.0.0 \
            httpx==0.28.1 \
            faker==33.1.0 \
            > /dev/null 2>&1
echo "✅ Test dependencies installed"

# Step 7: Verify installation
echo ""
echo "Step 7: Verifying installation..."
python -c "import pytest; import httpx; import faker; print('✅ All test packages imported successfully')"

# Step 8: Run a quick test
echo ""
echo "Step 8: Running syntax check on test files..."
python -m py_compile tests/conftest.py
python -m py_compile tests/utils/test_helpers.py
python -m py_compile tests/api/test_auth.py
python -m py_compile tests/api/test_fiis.py
python -m py_compile tests/api/test_transactions.py
python -m py_compile tests/api/test_dividends.py
echo "✅ All test files compile successfully"

# Done
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest -v"
echo ""
echo "To run tests with coverage:"
echo "  pytest --cov=app --cov-report=html"
echo ""
echo "For more information, see TESTING.md"
echo ""
