#!/bin/bash
set -e

echo "Creating redirect structure for releases..."

# Create base directories
mkdir -p releases/download

# Get all release tags and create redirects for each
releases_json=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/denova234/novaide-packages/releases")

echo "$releases_json" | jq -r '.[] | select(.draft == false and .prerelease == false) | .tag_name' | while read tag; do
  echo "Creating redirect for release: $tag"
  mkdir -p "releases/download/$tag"
  cat > "releases/download/$tag/index.html" << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <script>
        // Redirect package downloads to actual GitHub Releases
        const path = window.location.pathname;
        const filename = path.split('/').pop();
        
        if (filename.endsWith('.deb')) {
            const redirectUrl = `https://github.com/denova234/novaide-packages/releases/download/__TAG__/${filename}`;
            console.log('Redirecting to:', redirectUrl);
            window.location.href = redirectUrl;
        } else {
            document.body.innerHTML = `
                <h1>Nova IDE Package Redirect</h1>
                <p>Release: __TAG__</p>
                <p>This page redirects package downloads to GitHub Releases.</p>
                <p>If you see this page, APT is not following JavaScript redirects properly.</p>
            `;
        }
    </script>
    <!-- Meta refresh fallback -->
    <meta http-equiv="refresh" content="0; url=https://github.com/denova234/novaide-packages">
</head>
<body>
    <noscript>
        <h1>JavaScript Required</h1>
        <p>This page requires JavaScript to redirect to the package download.</p>
        <p>If you are APT, this redirect method may not work.</p>
        <p>Manual download: <a href="https://github.com/denova234/novaide-packages/releases">GitHub Releases</a></p>
    </noscript>
    Redirecting to GitHub Releases...
</body>
</html>
HTML
  # Replace the placeholder with actual tag
  sed -i "s/__TAG__/$tag/g" "releases/download/$tag/index.html"
done

# Create generic redirect for root releases path
cat > releases/download/index.html << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <title>Nova IDE Package Redirects</title>
    <meta http-equiv="refresh" content="0; url=https://github.com/denova234/novaide-packages/releases">
</head>
<body>
    <h1>Nova IDE Package Redirects</h1>
    <p>Redirecting to GitHub Releases...</p>
    <p>If not redirected, <a href="https://github.com/denova234/novaide-packages/releases">click here</a>.</p>
</body>
</html>
HTML

echo "Redirect structure created successfully"
