#!/usr/bin/env python3
import json
import sys
import hashlib
import requests
import os
from urllib.parse import urlparse

def calculate_checksums(url):
    """Calculate MD5 and SHA256 for a file URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        
        for chunk in response.iter_content(chunk_size=8192):
            md5.update(chunk)
            sha256.update(chunk)
            
        return md5.hexdigest(), sha256.hexdigest()
    except Exception as e:
        print(f"Warning: Could not calculate checksums for {url}: {e}", file=sys.stderr)
        return "0" * 32, "0" * 64

def parse_deb_filename(filename):
    """Parse .deb filename to extract package info"""
    # Format: package_version_arch.deb
    parts = filename.replace('.deb', '').split('_')
    if len(parts) >= 3:
        return parts[0], parts[1], parts[-1]
    return filename.replace('.deb', ''), '1.0', 'aarch64'

def generate_package_entry(asset, release):
    """Generate a Packages entry for a .deb file"""
    if not asset['name'].endswith('.deb'):
        return None
    
    package_name, version, architecture = parse_deb_filename(asset['name'])
    download_url = asset['browser_download_url']
    
    # Calculate file size and checksums
    size = asset['size']
    md5sum, sha256sum = calculate_checksums(download_url)
    
    # Generate package entry
    entry = f"""Package: {package_name}
Version: {version}
Architecture: {architecture}
Maintainer: Your Name <your-email@example.com>
Installed-Size: {size // 1024}
Description: Custom package - {package_name}
 Homepage: https://github.com/{os.getenv('REPO_OWNER', 'your-username')}/{os.getenv('REPO_NAME', 'your-repo')}
Filename: {download_url}
Size: {size}
MD5sum: {md5sum}
SHA256: {sha256sum}

"""
    
    return entry

def main():
    try:
        releases_json = json.load(sys.stdin)
        
        for release in releases_json:
            if release['draft']:
                continue
                
            for asset in release['assets']:
                package_entry = generate_package_entry(asset, release)
                if package_entry:
                    sys.stdout.write(package_entry)
                    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
