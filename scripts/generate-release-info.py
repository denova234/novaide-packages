#!/usr/bin/env python3
import json
import sys
import hashlib
import requests
import os

def calculate_checksums(url):
    """Calculate MD5 and SHA256 for a file URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                md5.update(chunk)
                sha256.update(chunk)
                
        return md5.hexdigest(), sha256.hexdigest()
    except Exception as e:
        print(f"Warning: Could not calculate checksums for {url}: {e}", file=sys.stderr)
        return "0" * 32, "0" * 64

def parse_deb_filename(filename):
    """Parse .deb filename to extract package info"""
    # Remove .deb extension
    base_name = filename.replace('.deb', '')
    parts = base_name.split('_')
    
    if len(parts) >= 3:
        package_name = parts[0]
        version = parts[1]
        architecture = parts[-1]
    else:
        package_name = base_name
        version = '1.0'
        architecture = 'aarch64'
    
    return package_name, version, architecture

def generate_package_entry(asset, release):
    """Generate a Packages entry for a .deb file"""
    if not asset['name'].endswith('.deb'):
        return None
    
    package_name, version, architecture = parse_deb_filename(asset['name'])
    download_url = asset['browser_download_url']
    
    # Calculate file size and checksums
    size = asset['size']
    md5sum, sha256sum = calculate_checksums(download_url)
    
    # Get release description or use default
    description = release.get('body', f'Custom package - {package_name}').split('\n')[0]
    
    # Generate package entry
    entry = f"""Package: {package_name}
Version: {version}
Architecture: {architecture}
Maintainer: Nova IDE <alexnova205@gmail.com>
Installed-Size: {size // 1024}
Description: {description}
Homepage: https://github.com/nova-ide/novaide-packages
Filename: {download_url}
Size: {size}
MD5sum: {md5sum}
SHA256: {sha256sum}

"""
    
    return entry

def main():
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read().strip()
        
        if not input_data:
            print("Error: No input data received", file=sys.stderr)
            sys.exit(1)
            
        releases = json.loads(input_data)
        
        if not isinstance(releases, list):
            print("Error: Expected JSON array", file=sys.stderr)
            sys.exit(1)
        
        package_count = 0
        
        for release in releases:
            if release.get('draft', False):
                continue
                
            for asset in release.get('assets', []):
                package_entry = generate_package_entry(asset, release)
                if package_entry:
                    sys.stdout.write(package_entry)
                    package_count += 1
        
        print(f"Processed {package_count} packages", file=sys.stderr)
                    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        print(f"Input received: {input_data[:200]}...", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
