# Nova Chat Permissions

## Permission Commands

| Command | Description | Granted Permissions |
|---------|-------------|-------------------|
| `;edit` | Grant file editing permission | Edit files only |
| `;all` | Grant all permissions | Full access to all tools |
| `;suno` | Grant extended permissions | All tools including file operations |

## Tool Permissions Matrix

| Tool | Requires Permission | Command | Notes |
|------|-------------------|---------|-------|
| **File Operations** | | | |
| Edit files | Yes | `;edit`, `;all`, `;suno` | Can modify existing files |
| Create files | Yes | `;all`, `;suno` | Can create new files |
| Delete files | Yes | `;all`, `;suno` | Requires confirmation |
| Rename files | Yes | `;all`, `;suno` | Can rename files |
| Create directories | Yes | `;all`, `;suno` | Can create new directories |
| Read files | No | Always available | Read-only access |
| Search files | No | Always available | Read-only access |
| **Code Quality** | | | |
| Lint code | No | Always available | Read-only analysis |
| Debug code | No | Always available | Read-only debugging |
| View history | No | Always available | Read-only backup viewing |
| **Execution** | | | |
| Run files | No | Always available | Execute with installed interpreters |
| **Package Management** | | | |
| Install packages | Yes | `;all`, `;suno` | Install Python packages via pip |
| **System** | | | |
| Share file info | No | Always available | Read-only file tree and content |
| View settings | No | Always available | Read-only settings access |
| Clear memory | No | Always available | Manage AI memory |

## Permission Levels

### Level 0: No Permissions (Default)
- Read files
- Search files
- Lint code
- Debug code
- View history
- Run files
- Share file info
- View settings
- Clear memory

### Level 1: Edit Permission (`;edit`)
- All Level 0 permissions
- Edit existing files

### Level 2: All Permissions (`;all`)
- All Level 0 and Level 1 permissions
- Create files
- Delete files (with confirmation)
- Rename files
- Create directories
- Install packages

### Level 3: Extended Permissions (`;suno`)
- Same as Level 2 (All Permissions)

## Security Restrictions

All operations are restricted to the **current working directory only**. Nova cannot:

- Access files outside the current directory
- Modify system files
- Execute system-level commands
- Access root or sudo privileges
- Make network connections (except Groq API)
- Modify files without explicit permission
- Delete files without confirmation

## Permission Persistence

- Permissions are **session-only** and do not persist across restarts
- Each new chat session starts with Level 0 (No Permissions)
- Use `;edit`, `;all`, or `;suno` each session to grant permissions

## Examples

### Basic Usage
```bash
you> ;edit                    # Grant edit permission
you> ;all                     # Grant all permissions
you> ;suno                    # Grant extended permissions
```

## Permission Check

```bash
you> ;read config.json          # Always works (no permission needed)
you> ;edit config.json          # Requires ;edit or higher
you> ;create test.py "print()"  # Requires ;all or ;suno
you> ;delete broken.py          # Requires ;all or ;suno + confirmation
```

## Best Practices

1. Start with minimal permissions - Only grant what you need
2. Use `;edit` for minor changes - Safer than granting all permissions
3. Review changes before confirming - Especially for delete operations
4. Use verbose mode (`-v`) - To see what Nova is doing
5. Check backup history - Before and after edits to verify changes
