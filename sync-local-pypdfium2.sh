#!/bin/bash

# sync-local-pypdfium2.sh
# Bash script to sync with local pypdfium2 submodule
# Handles GitHub CLI attestation bypass automatically

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to find GitHub CLI executable
find_gh_cli() {
    local gh_paths=(
        "gh"
        "/usr/local/bin/gh"
        "/opt/homebrew/bin/gh"
        "/usr/bin/gh"
        "/snap/bin/gh"
        "$HOME/.local/bin/gh"
        "/usr/local/github/bin/gh"
    )

    for path in "${gh_paths[@]}"; do
        if command -v "$path" >/dev/null 2>&1 || [[ -x "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    return 1
}

# Function to disable GitHub CLI
disable_gh_cli() {
    local gh_path=$(find_gh_cli)
    if [[ -n "$gh_path" && -f "$gh_path" ]]; then
        mv "$gh_path" "${gh_path}.backup"
        print_status "GitHub CLI temporarily disabled: $gh_path"
        return 0
    else
        print_warning "GitHub CLI not found - no need to disable"
        return 1
    fi
}

# Function to restore GitHub CLI
restore_gh_cli() {
    local gh_path=$(find_gh_cli)
    local backup_path="${gh_path}.backup"

    # Try to restore using original path
    if [[ -f "$backup_path" ]]; then
        mv "$backup_path" "$gh_path"
        print_success "GitHub CLI restored: $gh_path"
        return 0
    else
        # Try to find any .backup file in common locations
        local found=false
        for path in "/usr/local/bin/gh.backup" "/opt/homebrew/bin/gh.backup" "/usr/bin/gh.backup" "$HOME/.local/bin/gh.backup" "/snap/bin/gh.backup"; do
            if [[ -f "$path" ]]; then
                local original_path="${path%.backup}"
                mv "$path" "$original_path"
                print_success "GitHub CLI restored: $original_path"
                found=true
                break
            fi
        done

        if [[ "$found" == false ]]; then
            print_warning "GitHub CLI backup not found for restoration"
            return 1
        fi
        return 0
    fi
}

# Function to run uv sync
run_uv_sync() {
    print_status "Running uv sync with local pypdfium2 submodule..."

    # Install the correct ctypesgen version FIRST (pypdfium2 fork)
    print_status "Installing pypdfium2-team's ctypesgen fork (required for build)..."
    if uv pip install "ctypesgen @ git+https://github.com/pypdfium2-team/ctypesgen@pypdfium2"; then
        print_status "✓ Correct ctypesgen version installed"
    else
        print_error "Failed to install correct ctypesgen version"
        return 1
    fi

    # Force use of pre-generated bindings to avoid build conflicts
    print_status "Using pre-generated bindings to avoid build conflicts..."
    export PYPDFIUM2_BUILD_BINDINGS=0
    export PYPDFIUM2_PREBUILT_BINDINGS=1

    # Copy pre-generated bindings to the expected location to ensure they exist
    if [[ -f "pypdfium2/data/bindings/bindings.py" ]]; then
        print_status "Pre-generated bindings found, using them..."
    else
        print_warning "Pre-generated bindings not found, build may fail..."
    fi

    if uv sync; then
        print_success "uv sync completed successfully!"
        print_status "Local pypdfium2 submodule is now installed as editable dependency"
        print_status "Using pre-generated bindings (build skipped)"

        # Re-install correct ctypesgen after sync (in case it was replaced)
        print_status "Verifying correct ctypesgen version..."
        uv pip install "ctypesgen @ git+https://github.com/pypdfium2-team/ctypesgen@pypdfium2" --quiet

        # Show installed package info
        if command -v uv pip >/dev/null 2>&1; then
            print_status "Installed pypdfium2 info:"
            uv pip show pypdfium2 | head -5
        fi
        return 0
    else
        print_error "uv sync failed!"
        print_warning "Attempting alternative approach with editable install..."

        # Try alternative: install as build dependency
        if uv pip install -e ./pypdfium2 --no-build-isolation; then
            print_success "Alternative install completed successfully!"
            return 0
        else
            print_error "All install attempts failed!"
            return 1
        fi
    fi
}

# Main execution
main() {
    print_header "🚀 pypdfium2 Local Submodule Sync - Unix Script (devbuild branch)"
    print_header "================================================================="
    echo

    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        print_error "Please run this script from the project root directory containing pyproject.toml"
        exit 1
    fi

    if [[ ! -d "pypdfium2" ]]; then
        print_error "pypdfium2 directory not found. Please ensure the submodule is initialized."
        exit 1
    fi

    # Check if uv is installed
    if ! command -v uv >/dev/null 2>&1; then
        print_error "uv is not installed or not in PATH. Please install uv first."
        print_status "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    # Store whether we disabled GitHub CLI
    disabled_gh=false
    gh_path=""

    # Disable GitHub CLI if found
    gh_path=$(find_gh_cli)
    if [[ -n "$gh_path" && -f "$gh_path" ]]; then
        if disable_gh_cli; then
            disabled_gh=true
        fi
    else
        print_warning "GitHub CLI not found - no need to disable attestation verification"
    fi

    # Make sure we restore GitHub CLI even if something goes wrong
    cleanup() {
        if [[ "$disabled_gh" == true ]]; then
            restore_gh_cli
        fi
    }
    trap cleanup EXIT

    # Run uv sync
    if run_uv_sync; then
        echo
        print_success "All done! Your local pypdfium2 submodule (devbuild branch) is ready to use."
        echo
        print_status "You can now make changes in ./pypdfium2 and they will be reflected immediately."
        print_status "Remember to use 'initialize_with_fonts()' for proper font rendering!"
    else
        print_error "Script failed. Please check the error messages above."
        exit 1
    fi
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}Script interrupted. Cleaning up...${NC}"; cleanup; exit 1' INT

# Run main function
main "$@"