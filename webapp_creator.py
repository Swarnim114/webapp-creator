#!/usr/bin/env python3
import os
import sys
import urllib.request
import shutil
import argparse
import re
from urllib.parse import urlparse

def get_input(prompt, default=None):
    try:
        text = input(f"{prompt} [{default}]: " if default else f"{prompt}: ").strip()
        return text if text else default
    except EOFError:
        return ""

def get_installed_browsers():
    """Returns a list of installed browsers found in PATH."""
    # Map of Display Name -> Binary Name
    known_browsers = {
        "Google Chrome": "google-chrome",
        "Chromium": "chromium",
        "Brave": "brave-browser",
        "Microsoft Edge": "microsoft-edge",
        "Vivaldi": "vivaldi",
        "Firefox": "firefox", # Firefox doesn't support --app mode natively the same way, but we can include it
        "Epiphany": "epiphany"
    }
    
    installed = []
    for name, binary in known_browsers.items():
        if shutil.which(binary):
            installed.append((name, binary))
            
    return installed

def select_browser(auto_select=False):
    installed = get_installed_browsers()
    
    if not installed:
        print("Warning: No supported browsers detected in PATH.")
        return "Google Chrome", "google-chrome" # Fallback
        
    if auto_select and installed:
        return installed[0]

    print("\nDetected Browsers:")
    for i, (name, _) in enumerate(installed, 1):
        print(f"{i}. {name}")
    print(f"{len(installed) + 1}. Custom Command")
    
    while True:
        choice = get_input("Select a browser")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(installed):
                return installed[idx]
            elif idx == len(installed):
                cmd = get_input("Enter browser command (e.g. google-chrome)")
                return "Custom", cmd
        print("Invalid selection.")

def fetch_favicon(url, app_name):
    """Attempts to fetch a high-res favicon using Google's service."""
    domain = urlparse(url).netloc
    icon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    return download_icon(icon_url, app_name, is_auto=True)

def download_icon(url, app_name, is_auto=False):
    if not url:
        return None
    
    icon_dir = os.path.expanduser("~/.local/share/icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    safe_name = re.sub(r'[^a-z0-9]', '_', app_name.lower()).strip('_')
    icon_path = os.path.join(icon_dir, f"{safe_name}_webapp.png")
    
    try:
        if not is_auto:
            print(f"Downloading icon from {url}...")
            
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        with urllib.request.urlopen(req) as response, open(icon_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
        if not is_auto:
            print(f"Icon saved to {icon_path}")
        return icon_path
    except Exception as e:
        if not is_auto:
            print(f"Failed to download icon: {e}")
        return None

def create_desktop_file(app_name, url, browser_cmd, icon_path):
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(desktop_dir, exist_ok=True)
    
    safe_name = re.sub(r'[^a-z0-9]', '_', app_name.lower()).strip('_')
    file_path = os.path.join(desktop_dir, f"webapp-{safe_name}.desktop")
    
    # Handle Firefox differently if needed, but standard chromium flags:
    if "firefox" in browser_cmd:
        exec_cmd = f"{browser_cmd} --new-window {url}"
    else:
        exec_cmd = f"{browser_cmd} --app={url}"
    
    # StartupWMClass helps the window manager group the window correctly
    # For Chromium apps, it's usually the domain or safe name
    wm_class = urlparse(url).netloc
    
    content = [
        "[Desktop Entry]",
        "Version=1.0",
        f"Name={app_name}",
        f"Comment=Web App for {app_name}",
        f"Exec={exec_cmd}",
        f"StartupWMClass={wm_class}", 
        "Terminal=false",
        "Type=Application",
        "Categories=Network;WebBrowser;",
        "StartupNotify=true"
    ]
    
    if icon_path:
        content.append(f"Icon={icon_path}")
    else:
        content.append("Icon=web-browser")
        
    with open(file_path, "w") as f:
        f.write("\n".join(content))
    
    os.chmod(file_path, 0o755)
    print(f"\nSUCCESS: Web app created at: {file_path}")
    return file_path

def list_webapps():
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    if not os.path.exists(desktop_dir):
        return []
        
    apps = []
    for f in os.listdir(desktop_dir):
        if f.startswith("webapp-") and f.endswith(".desktop"):
            path = os.path.join(desktop_dir, f)
            with open(path, 'r') as file:
                name = "Unknown"
                for line in file:
                    if line.startswith("Name="):
                        name = line.strip().split("=", 1)[1]
                        break
            apps.append((name, path))
    return apps

def remove_webapp():
    apps = list_webapps()
    if not apps:
        print("No webapps found to remove.")
        return

    print("\nInstalled Webapps:")
    for i, (name, path) in enumerate(apps, 1):
        print(f"{i}. {name} ({os.path.basename(path)})")
        
    choice = get_input("Select number to remove (or Enter to cancel)")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(apps):
            name, path = apps[idx]
            try:
                os.remove(path)
                print(f"Removed '{name}'")
                
                # Try to remove associated icon
                safe_name = re.sub(r'[^a-z0-9]', '_', name.lower()).strip('_')
                icon_path = os.path.expanduser(f"~/.local/share/icons/{safe_name}_webapp.png")
                if os.path.exists(icon_path):
                    os.remove(icon_path)
                    print("Removed associated icon.")
            except Exception as e:
                print(f"Error removing file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Create desktop web applications on Linux")
    parser.add_argument("-n", "--name", help="Name of the web app")
    parser.add_argument("-u", "--url", help="URL of the web app")
    parser.add_argument("-i", "--icon", help="URL to an icon (PNG)")
    parser.add_argument("-b", "--browser", help="Browser command to use (e.g. google-chrome)")
    parser.add_argument("--remove", action="store_true", help="List and remove existing webapps")
    
    args = parser.parse_args()

    if args.remove:
        remove_webapp()
        return

    print("=== Linux WebApp Creator ===")
    
    # 1. Name
    app_name = args.name
    if not app_name:
        app_name = get_input("Name of the Web App")
        if not app_name:
            print("Error: Name is required.")
            return

    # 2. URL
    url = args.url
    if not url:
        url = get_input("URL (e.g. google.com)")
        if not url:
            print("Error: URL is required.")
            return
            
    if not url.startswith("http"):
        url = "https://" + url

    # 3. Browser
    if args.browser:
        browser_cmd = args.browser
    else:
        _, browser_cmd = select_browser()

    # 4. Icon
    icon_path = None
    if args.icon:
        icon_path = download_icon(args.icon, app_name)
    else:
        # Ask user or auto-fetch
        choice = get_input("Icon URL (Press Enter to auto-fetch from website)", default="")
        if choice:
            icon_path = download_icon(choice, app_name)
        else:
            print("Attempting to fetch favicon...")
            icon_path = fetch_favicon(url, app_name)

    create_desktop_file(app_name, url, browser_cmd, icon_path)

if __name__ == "__main__":
    main()
