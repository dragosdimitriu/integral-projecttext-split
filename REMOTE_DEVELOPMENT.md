# Remote Development Setup Guide

This guide explains how to connect to the production server for remote development using VS Code.

## Option 1: VS Code Remote SSH (Recommended)

### Installation

1. **Install VS Code Remote - SSH Extension**:
   - Open VS Code
   - Press `Ctrl+Shift+X` to open Extensions
   - Search for: `ms-vscode-remote.remote-ssh` (extension ID)
   - Or search for: "Remote - SSH" and look for publisher: **Microsoft**
   - Extension ID: `ms-vscode-remote.remote-ssh`
   - Publisher: **Microsoft**
   - Install the extension

2. **SSH Config File**:
   The SSH config has been automatically created at:
   ```
   C:\Users\YourUsername\.ssh\config
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

### Connecting

1. **Connect to Server**:
   - Press `F1` or `Ctrl+Shift+P`
   - Type "Remote-SSH: Connect to Host"
   - Select "pt.schrack.lastchance.ro"
   - VS Code will open a new window connected to the server

2. **Open Project Folder**:
   - Once connected, click "Open Folder" or press `Ctrl+K Ctrl+O`
   - Navigate to: `/home/lastchance/ProjectTextApp`
   - Click "OK"

### Features Available

✅ **Integrated Terminal**: Full terminal access to remote server  
✅ **File Explorer**: Browse and edit files directly  
✅ **IntelliSense**: Code completion and syntax highlighting  
✅ **Git Integration**: Use Git directly from VS Code  
✅ **Extensions**: Install VS Code extensions on remote server  
✅ **Debugging**: Debug Python code remotely  

### Quick Commands

- **Open Terminal**: `` Ctrl+` `` (backtick)
- **Open Command Palette**: `F1` or `Ctrl+Shift+P`
- **Reload Window**: `Ctrl+Shift+P` → "Developer: Reload Window"
- **Disconnect**: `Ctrl+Shift+P` → "Remote-SSH: Close Remote Connection"

## Option 2: SSHFS (Mount Remote Filesystem)

### Windows (Using WinFsp + SSHFS-Win)

1. **Install Prerequisites**:
   - Download WinFsp: https://winfsp.dev/rel/
   - Download SSHFS-Win: https://github.com/winfsp/sshfs-win/releases

2. **Mount Remote Directory**:
   ```powershell
   # Create mount point
   New-Item -ItemType Directory -Path "Z:\" -Force
   
   # Mount remote directory
   net use Z: \\sshfs.r\lastchance@185.125.109.150!2324\home\lastchance\ProjectTextApp
   ```

3. **Access Files**:
   - Remote files will appear in Windows Explorer at `Z:\`
   - Edit files directly using any Windows application

### Linux/Mac (Using sshfs)

```bash
# Install sshfs
sudo apt install sshfs  # Linux
brew install sshfs      # Mac

# Create mount point
mkdir -p ~/remote-projecttext

# Mount remote directory
sshfs -p 2324 lastchance@185.125.109.150:/home/lastchance/ProjectTextApp ~/remote-projecttext

# Unmount when done
fusermount -u ~/remote-projecttext  # Linux
umount ~/remote-projecttext         # Mac
```

## Option 3: Manual SSH + SCP

### Connect via SSH Terminal

```bash
ssh -p 2324 -i ~/.ssh/integral_projecttext_prod lastchance@185.125.109.150
```

### Transfer Files

**Upload file to server**:
```bash
scp -P 2324 -i ~/.ssh/integral_projecttext_prod file.txt lastchance@185.125.109.150:/home/lastchance/ProjectTextApp/
```

**Download file from server**:
```bash
scp -P 2324 -i ~/.ssh/integral_projecttext_prod lastchance@185.125.109.150:/home/lastchance/ProjectTextApp/file.txt ./
```

**Sync entire directory**:
```bash
rsync -avz -e "ssh -p 2324 -i ~/.ssh/integral_projecttext_prod" \
  lastchance@185.125.109.150:/home/lastchance/ProjectTextApp/ \
  ./local-copy/
```

## VS Code Remote SSH Tips

### Install Python Extension on Remote

1. Connect to remote server
2. Go to Extensions
3. Search for "Python"
4. Install (it will install on the remote server)

### Recommended Remote Extensions

- **Python** (by Microsoft)
- **Pylance** (Python language server)
- **GitLens** (Git integration)
- **Remote - SSH** (already installed)

### Terminal Setup

Once connected, you can:
- Open multiple terminal tabs
- Split terminal panes
- Run commands directly
- Access Git, Python, and all server tools

### File Editing

- Edit files directly on the server
- Changes are saved immediately
- Use Git to commit changes
- No need to sync files manually

## Troubleshooting

### Connection Fails

1. **Test SSH connection manually**:
   ```bash
   ssh -p 2324 -i ~/.ssh/integral_projecttext_prod lastchance@185.125.109.150
   ```

2. **Check SSH config**:
   - Verify config file at `~/.ssh/config`
   - Check IdentityFile path is correct
   - Ensure SSH key permissions: `chmod 600 ~/.ssh/integral_projecttext_prod`

3. **VS Code Logs**:
   - `F1` → "Remote-SSH: Show Log"
   - Check for error messages

### Permission Denied

- Verify SSH key is added to server's `~/.ssh/authorized_keys`
- Check file permissions on server
- Ensure user has access to `/home/lastchance/ProjectTextApp`

### Slow Connection

- Use `ServerAliveInterval` in SSH config (already added)
- Consider using compression: Add `Compression yes` to SSH config
- Use VS Code's "Remote - SSH: Kill VS Code Server on Host" if needed

## Security Notes

- SSH key is stored locally and never transmitted
- All connections are encrypted via SSH
- VS Code Remote SSH uses secure tunneling
- No need to expose additional ports

## Next Steps

1. Install VS Code Remote - SSH extension
2. Connect using the configured host: `pt.schrack.lastchance.ro`
3. Open `/home/lastchance/ProjectTextApp` folder
4. Start developing!

