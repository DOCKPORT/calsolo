#!/bin/bash

# Build the Calsolo AppImage using an Ubuntu 22.04 Docker container.
# This script MUST be run from the PROJECT ROOT (the parent of Binary/)
# so that the Docker build context contains calsolo.py, calc_engine/, Binary/, etc.

set -e

# Resolve paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install it first:"
    echo "sudo apt update && sudo apt install docker.io"
    echo "sudo usermod -aG docker \$USER (then log out and back in)"
    exit 1
fi

echo "🚀 Building Calsolo AppImage using Ubuntu 22.04 Docker container..."
echo "   Project root : $PROJECT_ROOT"
echo "   Binary dir   : $SCRIPT_DIR"

# Build the docker image FROM THE PROJECT ROOT so that the Dockerfile
# can COPY source files (calsolo.py, calc_engine/, etc.) into the image.
docker build \
    -t calsolo-builder \
    -f "$SCRIPT_DIR/Dockerfile" \
    "$PROJECT_ROOT"

# Run the container to build the AppImage.
# Mount the project root as /build so the output appears there.
docker run --rm -v "$PROJECT_ROOT":/build calsolo-builder

echo "✅ Done! Your Calsolo AppImage should be in the project root."