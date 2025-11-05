#!/bin/bash

set -e

REPO_OWNER="your-username"
REPO_NAME="your-repo-name"
ARCH="aarch64"
COMPONENT="main"

# Create directory structure
mkdir -p "dists/stable/$COMPONENT/binary-$ARCH"
mkdir -p "pool/$COMPONENT"

# Generate Packages file
echo "# Package index generated on $(date)" > "dists/stable/$COMPONENT/binary-$ARCH/Packages"

# Get releases from GitHub API
RELEASES_JSON=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases")

# Process each release
echo "$RELEASES_JSON" | python3 scripts/generate-release-info.py >> "dists/stable/$COMPONENT/binary-$ARCH/Packages"

# Create compressed Packages.gz
gzip -c "dists/stable/$COMPONENT/binary-$ARCH/Packages" > "dists/stable/$COMPONENT/binary-$ARCH/Packages.gz"

echo "Package index updated successfully!"
