# WebApp Creator

A simple CLI tool to create desktop web applications on Linux. It generates standard `.desktop` files, allowing your favorite websites to appear in your application menu and launch in their own window.

## Features
- **Auto-Detection**: Automatically finds installed browsers (Chrome, Chromium, Brave, Edge, Vivaldi, Firefox, Epiphany).
- **Smart Icons**: Automatically fetches high-quality favicons if no icon URL is provided.
- **Native Integration**: Sets `StartupWMClass` for proper window grouping in docks/taskbars.
- **Management**: Built-in option to list and remove created webapps.
- **CLI Support**: Scriptable via command-line arguments.

## Installation

### Arch Linux (AUR)
You can install `webapp-creator` directly from the AUR using your favorite helper (e.g., `yay` or `paru`):

```bash
yay -S webapp-creator
```

### Manual Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Swarnim114/webapp-creator.git
   cd webapp-creator
   ```

2. Make the script executable and link it to your path:
   ```bash
   chmod +x webapp_creator.py
   sudo ln -s "$(pwd)/webapp_creator.py" /usr/local/bin/webapp-creator
   ```

## Usage

### Interactive Mode
Simply run the command and follow the prompts:
```bash
webapp-creator
```

### Command Line Mode
You can skip the prompts by passing arguments:

```bash
# Create a YouTube app using Chrome
webapp-creator -n "YouTube" -u "youtube.com" -b google-chrome

# Create a Gmail app with a specific icon
webapp-creator -n "Gmail" -u "mail.google.com" -i "https://example.com/gmail.png"
```

### Remove WebApps
To list and delete installed webapps:
```bash
webapp-creator --remove
```

## Requirements
- Linux OS
- Python 3
- A supported web browser
