#!/usr/bin/env python3
import json
import sys
import hashlib
import requests
import os
import base64

def calculate_checksums_from_github(url):
    """Calculate checksums by downloading from GitHub with proper redirect handling"""
    try:
        session = requests.Session()
        response = session.get(url, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                md5.update(chunk)
                sha256.update(chunk)
                
        return md5.hexdigest(), sha256.hexdigest(), len(response.content)
    except Exception as e:
        print(f"Warning: Could not calculate checksums for {url}: {e}", file=sys.stderr)
        return "0" * 32, "0" * 64, 0

def parse_deb_filename(filename):
    """Parse .deb filename to extract package info"""
    base_name = filename.replace('.deb', '')
    parts = base_name.split('_')
    
    if len(parts) >= 3:
        package_name = parts[0]
        version = parts[1]
        architecture = parts[-1]
    else:
        package_name = base_name
        version = '1.0'
        architecture = 'all'
    
    return package_name, version, architecture

def generate_package_entry(asset, release):
    """Generate a Packages entry for a .deb file"""
    if not asset['name'].endswith('.deb'):
        return None
    
    package_name, version, architecture = parse_deb_filename(asset['name'])
    
    # Use direct GitHub releases URL but we need to handle redirects
    download_url = asset['browser_download_url']
    
    print(f"Processing package: {package_name} {version} {architecture}", file=sys.stderr)
    print(f"Download URL: {download_url}", file=sys.stderr)
    
    # Calculate checksums by actually downloading the file
    print(f"Calculating checksums for {asset['name']}...", file=sys.stderr)
    md5sum, sha256sum, calculated_size = calculate_checksums_from_github(download_url)
    
    if calculated_size == 0:
        print(f"✗ Failed to calculate checksums for {asset['name']}", file=sys.stderr)
        return None
    
    print(f"✓ Checksums calculated: {calculated_size} bytes", file=sys.stderr)
    
    # Get release description or use default
    description = release.get('body', f'Custom package - {package_name}').split('\n')[0]
    if not description or description.strip() == "":
        description = f"Package {package_name} from Nova IDE repository"
    
    # Use the direct GitHub URL - APT should handle redirects for downloads
    entry = f"""Package: {package_name}
Version: {version}
Architecture: {architecture}
Maintainer: Nova IDE <alexnova205@gmail.com>
Installed-Size: {calculated_size // 1024}
Description: {description}
Homepage: https://github.com/denova234/novaide-packages
Filename: {download_url}
Size: {calculated_size}
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
        valid_packages = []
        
        for release in releases:
            if release.get('draft', False):
                print(f"Skipping draft release: {release.get('tag_name', 'unknown')}", file=sys.stderr)
                continue
                
            print(f"Processing release: {release.get('tag_name', 'unknown')}", file=sys.stderr)
            print(f"Release assets: {len(release.get('assets', []))}", file=sys.stderr)
            
            for asset in release.get('assets', []):
                if not asset['name'].endswith('.deb'):
                    continue
                    
                print(f"Checking asset: {asset['name']}", file=sys.stderr)
                package_entry = generate_package_entry(asset, release)
                if package_entry:
                    valid_packages.append(package_entry)
                    package_count += 1
                    print(f"✓ Added package: {asset['name']}", file=sys.stderr)
                else:
                    print(f"✗ Skipped asset: {asset['name']}", file=sys.stderr)
        
        # Write all valid packages
        for package_entry in valid_packages:
            sys.stdout.write(package_entry)
        
        print(f"Generated index with {package_count} valid packages", file=sys.stderr)
        
        if package_count == 0:
            print("Warning: No valid packages found in releases!", file=sys.stderr)
            print("Make sure your releases have .deb files uploaded as assets.", file=sys.stderr)
                    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
