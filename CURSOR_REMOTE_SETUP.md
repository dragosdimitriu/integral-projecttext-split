# Remote Development Setup in Cursor

This guide explains how to connect to the production server using Cursor's remote development features.

## Cursor Remote SSH Setup

Cursor is based on VS Code and supports Remote - SSH extensions. Here's how to set it up:

### Step 1: Install Remote - SSH Extension in Cursor

1. **Open Cursor**
2. **Open Extensions**:
   - Press `Ctrl+Shift+X` or click the Extensions icon in the sidebar
   
3. **Search for Remote - SSH**:
   - Search for: `ms-vscode-remote.remote-ssh`
   - Or search for: "Remote - SSH" and verify publisher is **Microsoft**
   - Extension ID: `ms-vscode-remote.remote-ssh`
   
4. **Install the Extension**:
   - Click "Install" on the Microsoft Remote - SSH extension
   - Wait for installation to complete

### Step 2: Verify SSH Config

Your SSH config should already be set up at:
```
C:\Users\Dragos Dimitriu\.ssh\config
```

It contains:
```
Host pt.schrack.lastchance.ro
    HostName 185.125.109.150
    User lastchance
    Port 2324
    IdentityFile ~/.ssh/integral_projecttext_prod
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### Step 3: Connect to Remote Server

1. **Open Command Palette**:
   - Press `F1` or `Ctrl+Shift+P`
   
2. **Connect to Host**:
   - Type: `Remote-SSH: Connect to Host`
   - Select: `pt.schrack.lastchance.ro`
   
3. **Wait for Connection**:
   - Cursor will open a new window
   - It will install the Cursor server on the remote machine (first time only)
   - Wait for "SSH: pt.schrack.lastchance.ro" to appear in bottom-left corner

### Step 4: Open Project Folder

1. **Open Folder**:
   - Click "Open Folder" button or press `Ctrl+K Ctrl+O`
   - Navigate to: `/home/lastchance/ProjectTextApp`
   - Click "OK"

2. **Trust the Folder** (if prompted):
   - Click "Yes, I trust the authors"

## Features Available in Cursor

✅ **Integrated Terminal**: Full terminal access to remote server  
✅ **File Explorer**: Browse and edit files directly on server  
✅ **Cursor AI**: Works with remote files!  
✅ **IntelliSense**: Code completion and syntax highlighting  
✅ **Git Integration**: Use Git directly from Cursor  
✅ **Extensions**: Install Cursor extensions on remote server  
✅ **Debugging**: Debug Python code remotely  

## Quick Commands

- **Open Terminal**: `` Ctrl+` `` (backtick)
- **Open Command Palette**: `F1` or `Ctrl+Shift+P`
- **Reload Window**: `Ctrl+Shift+P` → "Developer: Reload Window"
- **Disconnect**: `Ctrl+Shift+P` → "Remote-SSH: Close Remote Connection"
- **Show Log**: `Ctrl+Shift+P` → "Remote-SSH: Show Log"

## Troubleshooting

### Extension Not Found

If you can't find the Microsoft extension:

1. **Try Direct Marketplace Link**:
   - Open: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh
   - Click "Install" - it should open in Cursor

2. **Install via Command Line** (if Cursor CLI is available):
   ```powershell
   cursor --install-extension ms-vscode-remote.remote-ssh
   ```

3. **Manual Installation**:
   - Download the VSIX file from marketplace
   - In Cursor: `Ctrl+Shift+P` → "Extensions: Install from VSIX..."

### Connection Issues

**Test SSH connection manually first**:
```powershell
ssh -p 2324 -i "$env:USERPROFILE\.ssh\integral_projecttext_prod" lastchance@185.125.109.150
```

**Check SSH config**:
- Verify config file exists: `C:\Users\Dragos Dimitriu\.ssh\config`
- Check IdentityFile path is correct
- Ensure SSH key permissions are correct

**View Connection Logs**:
- `F1` → "Remote-SSH: Show Log"
- Look for error messages

### Cursor Server Installation Fails

If Cursor server fails to install on remote:

1. **Check Python on Server**:
   ```bash
   python3 --version
   ```

2. **Check Disk Space**:
   ```bash
   df -h
   ```

3. **Manual Server Installation**:
   - The server installs automatically, but if it fails, check logs
   - Server location: `~/.cursor-server/`

### Permission Issues

- Verify SSH key is added to server: `~/.ssh/authorized_keys`
- Check file permissions: `chmod 600 ~/.ssh/integral_projecttext_prod`
- Ensure user has access to `/home/lastchance/ProjectTextApp`

### Slow Connection

- Connection uses SSH encryption (secure but can be slower)
- Use `ServerAliveInterval` in SSH config (already configured)
- Consider using compression: Add `Compression yes` to SSH config

## Alternative: Use Cursor's Built-in Terminal

If Remote SSH doesn't work, you can still use Cursor with SSH terminal:

1. **Open Integrated Terminal** in Cursor: `` Ctrl+` ``
2. **SSH into Server**:
   ```powershell
   ssh -p 2324 -i "$env:USERPROFILE\.ssh\integral_projecttext_prod" lastchance@185.125.109.150
   ```
3. **Edit Files Remotely**:
   - Use `nano`, `vim`, or other terminal editors
   - Or use Cursor's file sync features

## Recommended Cursor Extensions for Remote

Once connected, install these extensions on the remote server:

- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **GitLens** (eamodio.gitlens)

## Next Steps

1. Install Remote - SSH extension in Cursor
2. Connect to `pt.schrack.lastchance.ro`
3. Open `/home/lastchance/ProjectTextApp`
4. Start coding with full Cursor AI features on remote files!

## Notes

- Cursor AI works with remote files just like local files
- All Cursor features are available when connected remotely
- Changes are saved directly to the server
- No need to sync files manually

