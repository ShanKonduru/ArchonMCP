#!/bin/bash
# ArchonMCP - Build and Deploy Script for Unix/Linux/macOS
# Supports both CLI and MCP Server modes
#
# After deployment, use:
#   archon-mcp init            - Initialize governance (CLI mode)
#   archon-mcp detect          - Detect tech stack (CLI mode)
#   archon-mcp server          - Run as MCP server (IDE integration)
#   archon-mcp --help          - Show all available commands

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}"
echo "========================================"
echo "ArchonMCP Build and Deploy Tool"
echo "========================================"
echo -e "${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check for required tools
if ! python3 -m pip show build &> /dev/null; then
    echo -e "${YELLOW}Installing build tools...${NC}"
    python3 -m pip install --upgrade build twine
else
    echo -e "${GREEN}Build tools already installed${NC}"
fi

# Menu
echo ""
echo "Select an action:"
echo "1. Build only"
echo "2. Test locally with pip"
echo "3. Upload to TestPyPI"
echo "4. Upload to PyPI (production)"
echo "5. Full cycle (build + TestPyPI + PyPI)"
echo "6. Clean build artifacts"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        build_package
        ;;
    2)
        test_local
        ;;
    3)
        upload_testpypi
        ;;
    4)
        upload_pypi
        ;;
    5)
        full_cycle
        ;;
    6)
        clean_artifacts
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Build function
build_package() {
    echo ""
    echo -e "${BLUE}Building package...${NC}"
    python3 -m build
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Build failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}Build completed successfully!${NC}"
    echo "Artifacts in: dist/"
}

# Test local function
test_local() {
    echo ""
    echo -e "${BLUE}Building package...${NC}"
    python3 -m build
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Build failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${BLUE}Testing with pip...${NC}"
    python3 -m pip install -e .
    
    echo ""
    echo -e "${BLUE}Testing installation...${NC}"
    python3 -c "import archon_mcp; print('ArchonMCP installed successfully')"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Installation or import failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}Local test completed successfully!${NC}"
}

# Upload to TestPyPI function
upload_testpypi() {
    echo ""
    echo -e "${BLUE}Building package...${NC}"
    python3 -m build
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Build failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${YELLOW}Note: You will need TestPyPI credentials${NC}"
    echo -e "${BLUE}Uploading to TestPyPI...${NC}"
    python3 -m twine upload --repository testpypi dist/*
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: TestPyPI upload failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}Successfully uploaded to TestPyPI!${NC}"
    echo "To test the package, run:"
    echo "  pip install --index-url https://test.pypi.org/simple/ archon-mcp"
}

# Upload to PyPI function
upload_pypi() {
    echo ""
    echo -e "${YELLOW}WARNING: This will upload to production PyPI${NC}"
    echo "Ensure version is incremented in pyproject.toml"
    echo ""
    read -p "Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Upload cancelled"
        return 0
    fi
    
    echo ""
    echo -e "${BLUE}Building package...${NC}"
    python3 -m build
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Build failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${BLUE}Uploading to PyPI...${NC}"
    python3 -m twine upload dist/*
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: PyPI upload failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}Successfully uploaded to PyPI!${NC}"
}

# Full cycle function
full_cycle() {
    echo ""
    echo -e "${BLUE}Full deployment cycle: Clean > Build > TestPyPI > PyPI${NC}"
    echo ""
    
    clean_artifacts
    
    echo ""
    echo -e "${BLUE}Building package...${NC}"
    python3 -m build
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Build failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${BLUE}Uploading to TestPyPI...${NC}"
    python3 -m twine upload --repository testpypi dist/*
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: TestPyPI upload failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}TestPyPI upload successful. Testing installation...${NC}"
    echo "Press Enter to continue..."
    read
    
    python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps archon-mcp
    
    echo ""
    echo -e "${YELLOW}WARNING: This will upload to production PyPI${NC}"
    echo "Ensure version is incremented in pyproject.toml"
    echo ""
    read -p "Continue to PyPI? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}PyPI upload cancelled${NC}"
        return 0
    fi
    
    echo ""
    echo -e "${BLUE}Uploading to PyPI...${NC}"
    python3 -m twine upload dist/*
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: PyPI upload failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}Full deployment cycle completed successfully!${NC}"
}

# Clean artifacts function
clean_artifacts() {
    echo ""
    echo -e "${BLUE}Cleaning build artifacts...${NC}"
    rm -rf dist/ build/ *.egg-info 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}Clean completed!${NC}"
}

# Footer
echo ""
echo -e "${BLUE}========================================"
echo "Operation completed"
echo "========================================${NC}"
echo ""
