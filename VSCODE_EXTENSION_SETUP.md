# VS Code Remote SSH Extension Setup

## Finding the Correct Extension

The official Remote - SSH extension is published by **Microsoft**. If you're seeing a different publisher, follow these steps:

### Method 1: Direct Extension ID

1. Open VS Code
2. Press `Ctrl+Shift+X` to open Extensions
3. Click the `...` menu (top right of Extensions panel)
4. Select "Install from VSIX..." OR use the search box
5. Search for: `ms-vscode-remote.remote-ssh`
6. Install the extension with ID: `ms-vscode-remote.remote-ssh`

### Method 2: Marketplace Link

Open this URL in your browser:
```
https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh
```

Click "Install" - it will open VS Code and install the extension.

### Method 3: Command Line Installation

Open PowerShell and run:
```powershell
code --install-extension ms-vscode-remote.remote-ssh
```

### Method 4: Verify Correct Extension

The correct extension should show:
- **Name**: Remote - SSH
- **Publisher**: Microsoft (not Anysphere or any other)
- **ID**: ms-vscode-remote.remote-ssh
- **Description**: "Open any folder on a remote machine using SSH"

### If You See Anysphere Extension

**DO NOT** install the Anysphere extension - it's a different product. The Microsoft extension is the official one for remote development.

### Alternative: Install Remote Development Extension Pack

The Remote - SSH extension is part of the Remote Development extension pack:

1. Search for: `ms-vscode-remote.vscode-remote-extensionpack`
2. This installs:
   - Remote - SSH
   - Remote - Containers
   - Remote - WSL

### Troubleshooting

**Extension not showing in search?**
- Make sure you're using VS Code (not VS Code Insiders, unless you want that)
- Try searching for the exact ID: `ms-vscode-remote.remote-ssh`
- Check VS Code is up to date

**Verify Installation:**
- After installing, you should see "Remote" in the bottom-left corner of VS Code
- Press `F1` and type "Remote-SSH" - you should see Remote-SSH commands

## Quick Install Command

```powershell
code --install-extension ms-vscode-remote.remote-ssh
```

## After Installation

1. Press `F1` or `Ctrl+Shift+P`
2. Type: `Remote-SSH: Connect to Host`
3. Select: `pt.schrack.lastchance.ro`
4. Open folder: `/home/lastchance/ProjectTextApp`

