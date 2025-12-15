#!/usr/bin/env python3
import os
import sys
import urllib.request
import shutil

def get_input(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""

def select_browser():
    browsers = {
        "1": ("Google Chrome", "google-chrome"),
        "2": ("Chromium", "chromium"),
        "3": ("Brave", "brave-browser"),
        "4": ("Microsoft Edge", "microsoft-edge"),
        "5": ("Vivaldi", "vivaldi")
    }
    
    print("\nSelect a browser to launch the webapp:")
    for key, (name, _) in browsers.items():
        print(f"{key}. {name}")
    
    while True:
        choice = get_input("Enter number (1-5): ")
        if choice in browsers:
            return browsers[choice]
        print("Invalid selection. Please try again.")

def download_icon(url, app_name):
    if not url:
        return None
    
    # Save icons to ~/.local/share/icons
    icon_dir = os.path.expanduser("~/.local/share/icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    # Create a safe filename
    safe_name = "".join(c for c in app_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_').lower()
    icon_path = os.path.join(icon_dir, f"{safe_name}_webapp.png")
    
    try:
        print(f"Downloading icon from {url}...")
        # Add a User-Agent to avoid 403 Forbidden on some sites
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        with urllib.request.urlopen(req) as response, open(icon_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
        print(f"Icon saved to {icon_path}")
        return icon_path
    except Exception as e:
        print(f"Failed to download icon: {e}")
        return None

def create_desktop_file(app_name, url, browser_cmd, icon_path):
    # Standard location for user desktop entries
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(desktop_dir, exist_ok=True)
    
    safe_name = "".join(c for c in app_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_').lower()
    file_path = os.path.join(desktop_dir, f"webapp-{safe_name}.desktop")
    
    # Chromium-based browsers use --app=URL for windowed mode
    exec_cmd = f"{browser_cmd} --app={url}"
    
    content = [
        "[Desktop Entry]",
        "Version=1.0",
        f"Name={app_name}",
        f"Comment=Web App for {app_name}",
        f"Exec={exec_cmd}",
        "Terminal=false",
        "Type=Application",
        "Categories=Network;WebBrowser;",
        "StartupNotify=true"
    ]
    
    if icon_path:
        content.append(f"Icon={icon_path}")
    else:
        # Fallback to a generic web browser icon if available
        content.append("Icon=web-browser")
        
    with open(file_path, "w") as f:
        f.write("\n".join(content))
    
    # Make executable (optional for .desktop files in this dir, but good practice)
    os.chmod(file_path, 0o755)
    
    print(f"\nSUCCESS: Web app created at: {file_path}")
    print("You should now be able to find it in your application menu.")
    return file_path

def main():
    print("=== Linux WebApp Creator ===")
    print("This script creates a standalone web app shortcut in your application menu.\n")
    
    app_name = get_input("1. Enter the name of the Web App: ")
    if not app_name:
        print("Error: Name is required.")
        return

    url = get_input("2. Enter the URL (e.g., google.com): ")
    if not url:
        print("Error: URL is required.")
        return
        
    if not url.startswith("http"):
        url = "https://" + url
        
    browser_name, browser_cmd = select_browser()
    
    # Check if browser is actually installed
    if not shutil.which(browser_cmd):
        print(f"\nWARNING: '{browser_name}' ({browser_cmd}) was not found in your PATH.")
        confirm = get_input("Do you want to continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            return

    icon_url = get_input("3. Enter URL for PNG icon (optional, press Enter to skip): ")
    icon_path = download_icon(icon_url, app_name)
    
    create_desktop_file(app_name, url, browser_cmd, icon_path)

if __name__ == "__main__":
    main()
