#!/bin/bash

set -e

REPO_OWNER="denova234"
REPO_NAME="novaide-packages"
ARCH="aarch64"
COMPONENT="main"

echo "Starting package index update..."
echo "Repository: $REPO_OWNER/$REPO_NAME"

# Create directory structure
mkdir -p "dists/stable/$COMPONENT/binary-$ARCH"
mkdir -p "pool/$COMPONENT"

# Initialize Packages file
echo "# Package index generated on $(date)" > "dists/stable/$COMPONENT/binary-$ARCH/Packages"
echo "# Repository: https://github.com/$REPO_OWNER/$REPO_NAME" >> "dists/stable/$COMPONENT/binary-$ARCH/Packages"

# Get releases from GitHub API
echo "Fetching releases from GitHub API..."
RELEASES_JSON=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases")

# Check if we got valid JSON
if ! echo "$RELEASES_JSON" | jq type > /dev/null 2>&1; then
    echo "Error: Invalid JSON response from GitHub API"
    echo "Response: $RELEASES_JSON"
    exit 1
fi

# Check if we have any releases
RELEASE_COUNT=$(echo "$RELEASES_JSON" | jq length)
echo "Found $RELEASE_COUNT releases"

if [ "$RELEASE_COUNT" -eq 0 ]; then
    echo "No releases found. Creating empty package index."
else
    # Process releases and generate package index
    echo "Processing releases..."
    echo "$RELEASES_JSON" | python3 scripts/generate-release-info.py >> "dists/stable/$COMPONENT/binary-$ARCH/Packages"
fi

# Create compressed Packages.gz
echo "Creating compressed Packages.gz..."
gzip -c "dists/stable/$COMPONENT/binary-$ARCH/Packages" > "dists/stable/$COMPONENT/binary-$ARCH/Packages.gz"

# Generate Release file
echo "Generating Release file..."
cd dists/stable

# Calculate checksums
PACKAGES_SIZE=$(stat -c%s "main/binary-$ARCH/Packages")
PACKAGES_MD5=$(md5sum "main/binary-$ARCH/Packages" | cut -d' ' -f1)
PACKAGES_SHA256=$(sha256sum "main/binary-$ARCH/Packages" | cut -d' ' -f1)

PACKAGES_GZ_SIZE=$(stat -c%s "main/binary-$ARCH/Packages.gz")
PACKAGES_GZ_MD5=$(md5sum "main/binary-$ARCH/Packages.gz" | cut -d' ' -f1)
PACKAGES_GZ_SHA256=$(sha256sum "main/binary-$ARCH/Packages.gz" | cut -d' ' -f1)

# Create Release file
cat > Release << EOF
Origin: Nova IDE Packages
Label: Nova IDE
Suite: stable
Version: 1.0
Codename: stable
Architectures: $ARCH
Components: $COMPONENT
Description: Custom packages for Nova IDE
$(date -u +"Date: %a, %d %b %Y %H:%M:%S UTC")
MD5Sum:
 $PACKAGES_MD5 $PACKAGES_SIZE main/binary-$ARCH/Packages
 $PACKAGES_GZ_MD5 $PACKAGES_GZ_SIZE main/binary-$ARCH/Packages.gz
SHA256:
 $PACKAGES_SHA256 $PACKAGES_SIZE main/binary-$ARCH/Packages
 $PACKAGES_GZ_SHA256 $PACKAGES_GZ_SIZE main/binary-$ARCH/Packages.gz
EOF

cd -

echo "Package index updated successfully!"
echo "Packages file size: $(stat -c%s "dists/stable/$COMPONENT/binary-$ARCH/Packages") bytes"
echo "Packages.gz file size: $(stat -c%s "dists/stable/$COMPONENT/binary-$ARCH/Packages.gz") bytes"
