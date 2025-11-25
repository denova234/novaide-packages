#!/usr/bin/env python3
import json
import sys
import hashlib
import requests
import os

def debug_log(message):
    """Print debug messages to stderr"""
    print(f"DEBUG: {message}", file=sys.stderr)

def calculate_checksums_from_github(url):
    """Calculate checksums by downloading from GitHub"""
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        response = session.get(url, stream=True, allow_redirects=True, timeout=30)
        response.raise_for_status()
        
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        total_size = 0
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                md5.update(chunk)
                sha256.update(chunk)
                total_size += len(chunk)
                
        return md5.hexdigest(), sha256.hexdigest(), total_size
    except Exception as e:
        debug_log(f"Could not calculate checksums for {url}: {e}")
        return None, None, 0

def parse_deb_filename(filename):
    """Parse .deb filename to extract package info"""
    if not filename.endswith('.deb'):
        return None, None, None
        
    base_name = filename.replace('.deb', '')
    parts = base_name.split('_')
    
    if len(parts) >= 3:
        package_name = parts[0]
        version = parts[1]
        architecture = parts[-1]
        return package_name, version, architecture
    else:
        debug_log(f"Could not parse filename: {filename}")
        return None, None, None

def generate_package_entry(asset, release):
    """Generate a Packages entry for a .deb file"""
    if not asset['name'].endswith('.deb'):
        debug_log(f"Skipping non-deb asset: {asset['name']}")
        return None
    
    package_name, version, architecture = parse_deb_filename(asset['name'])
    if not package_name:
        return None
    
    # Use your new approach: relative path to releases
    release_tag = release.get('tag_name', '1.0')
    filename_path = f"releases?tag={release_tag}&package={asset['name']}"
    
    # The actual download URL for checksum calculation
    download_url = asset['browser_download_url']
    
    debug_log(f"Processing: {package_name} {version} {architecture}")
    debug_log(f"Filename path: {filename_path}")
    debug_log(f"Actual URL for checksums: {download_url}")
    
    # Calculate checksums using the actual GitHub URL
    debug_log("Calculating checksums...")
    md5sum, sha256sum, calculated_size = calculate_checksums_from_github(download_url)
    
    if calculated_size == 0:
        debug_log(f"Failed to calculate checksums for {asset['name']}")
        return None
    
    debug_log(f"Checksums calculated: {calculated_size} bytes")
    
    # Get description
    description = release.get('body', '').split('\n')[0] or f"Package {package_name}"
    if len(description) > 200:
        description = description[:200] + "..."
    
    # Generate package entry using your relative path approach
    entry = f"""Package: {package_name}
Version: {version}
Architecture: {architecture}
Maintainer: Nova IDE <alexnova205@gmail.com>
Installed-Size: {calculated_size // 1024}
Description: {description}
Homepage: https://github.com/denova234/novaide-packages
Filename: {filename_path}
Size: {calculated_size}
MD5sum: {md5sum}
SHA256: {sha256sum}

"""
    
    return entry

def main():
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read().strip()
        debug_log(f"Input data length: {len(input_data)}")
        
        if not input_data:
            debug_log("No input data received")
            sys.exit(1)
            
        releases = json.loads(input_data)
        debug_log(f"Found {len(releases)} releases")
        
        if not isinstance(releases, list):
            debug_log("Expected JSON array but got something else")
            sys.exit(1)
        
        package_count = 0
        valid_packages = []
        
        for i, release in enumerate(releases):
            release_tag = release.get('tag_name', 'unknown')
            debug_log(f"Processing release {i+1}: {release_tag}")
            
            if release.get('draft', False):
                debug_log("Skipping draft release")
                continue
                
            if release.get('prerelease', False):
                debug_log("Skipping prerelease")
                continue
            
            assets = release.get('assets', [])
            debug_log(f"Release has {len(assets)} assets")
            
            for j, asset in enumerate(assets):
                debug_log(f"Checking asset {j+1}: {asset['name']}")
                package_entry = generate_package_entry(asset, release)
                if package_entry:
                    valid_packages.append(package_entry)
                    package_count += 1
                    debug_log(f"✓ Added package: {asset['name']}")
                else:
                    debug_log(f"✗ Skipped asset: {asset['name']}")
        
        # Write all valid packages
        debug_log(f"Writing {len(valid_packages)} packages to index")
        for package_entry in valid_packages:
            sys.stdout.write(package_entry)
        
        debug_log(f"Generated index with {package_count} valid packages")
        
        if package_count == 0:
            debug_log("No valid packages found!")
            # Create a minimal valid Packages file
            sys.stdout.write("# No packages available in releases\n")
            sys.stdout.write("# Upload .deb files to GitHub releases to populate repository\n")
                    
    except json.JSONDecodeError as e:
        debug_log(f"JSON decode error: {e}")
        sys.exit(1)
    except Exception as e:
        debug_log(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
