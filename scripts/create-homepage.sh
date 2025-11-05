#!/bin/bash
set -e

echo "Creating repository homepage..."

cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Nova IDE Packages</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
               max-width: 800px; margin: 0 auto; padding: 20px; 
               background: #f8f9fa; color: #333; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); 
                 color: white; padding: 30px; border-radius: 15px; 
                 margin-bottom: 30px; text-align: center; }
        .card { background: white; padding: 25px; border-radius: 10px; 
               margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        code { background: #f1f3f4; padding: 8px 12px; border-radius: 6px; 
              font-family: 'Monaco', 'Consolas', monospace; display: block; 
              margin: 10px 0; overflow-x: auto; }
        .status { display: inline-flex; align-items: center; gap: 8px;
                 padding: 8px 16px; border-radius: 20px; font-size: 14px;
                 background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; 
                     background: #28a745; animation: pulse 2s infinite; }
        @keyframes pulse {
            0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Nova IDE Package Repository</h1>
        <p>Exclusive Termux package repository for Nova IDE</p>
    </div>

    <div class="card">
        <h2>📥 Installation</h2>
        <p>Add this repository to your Termux installation:</p>
        <code>echo "deb [trusted=yes] https://denova234.github.io/novaide-packages/ stable main" >> $PREFIX/etc/apt/sources.list</code>
        
        <p>Update package lists:</p>
        <code>pkg update</code>
        
        <p>Install packages:</p>
        <code>pkg install &lt;package-name&gt;</code>
    </div>

    <div class="card">
        <h2>ℹ️ Repository Information</h2>
        <div class="status">
            <div class="status-dot"></div>
            Repository Status: Operational
        </div>
        <p><strong>Architecture:</strong> This repository uses GitHub Releases for package storage with automatic redirects.</p>
        <p><strong>Note:</strong> Packages are hosted on GitHub Releases for better scalability.</p>
    </div>

    <div class="card">
        <h2>🔧 Available Packages</h2>
        <div id="packages">
            <p>Loading package list...</p>
        </div>
    </div>

    <script>
        async function loadPackages() {
            try {
                const response = await fetch('dists/stable/main/binary-aarch64/Packages');
                const text = await response.text();
                const packages = parsePackages(text);
                displayPackages(packages);
            } catch (error) {
                document.getElementById('packages').innerHTML = 
                    '<p>Unable to load package list. Repository might be updating.</p>';
            }
        }

        function parsePackages(text) {
            const packages = [];
            const entries = text.split('\n\n');
            
            entries.forEach(entry => {
                if (entry.trim()) {
                    const pkg = {};
                    entry.split('\n').forEach(line => {
                        const [key, ...value] = line.split(':');
                        if (key && value) pkg[key.trim()] = value.join(':').trim();
                    });
                    if (pkg.Package) packages.push(pkg);
                }
            });
            
            return packages;
        }

        function displayPackages(packages) {
            const container = document.getElementById('packages');
            
            if (packages.length === 0) {
                container.innerHTML = '<p>No packages available yet.</p>';
                return;
            }
            
            container.innerHTML = packages.map(pkg => `
                <div style="border: 1px solid #e9ecef; padding: 15px; margin: 10px 0; border-radius: 8px;">
                    <h3 style="margin: 0 0 8px 0; color: #667eea;">${pkg.Package}</h3>
                    <div style="display: flex; gap: 15px; font-size: 14px; color: #666; margin-bottom: 8px;">
                        <span>Version: ${pkg.Version}</span>
                        <span>Arch: ${pkg.Architecture}</span>
                        <span>Size: ${(pkg.Size / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                    <p style="margin: 0; color: #555;">${pkg.Description || 'No description'}</p>
                </div>
            `).join('');
        }

        loadPackages();
    </script>
</body>
</html>
EOF

echo "Homepage created successfully"
