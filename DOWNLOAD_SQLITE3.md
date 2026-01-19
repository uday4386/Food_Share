# How to Download and Install SQLite3 on Windows

## Method 1: Automated Installation (Recommended)

### Using PowerShell Script:
```powershell
powershell.exe -ExecutionPolicy Bypass -File install_sqlite3.ps1
```

### Or double-click:
```
install_sqlite3.bat
```

---

## Method 2: Manual Download (One-time setup)

### Option A: Direct Download Command (PowerShell)
```powershell
# Download SQLite3
Invoke-WebRequest -Uri "https://www.sqlite.org/2024/sqlite-tools-win-x64-3500100.zip" -OutFile "sqlite3.zip"

# Extract
Expand-Archive -Path "sqlite3.zip" -DestinationPath "sqlite3" -Force

# Copy sqlite3.exe to project folder
Copy-Item -Path "sqlite3\sqlite-tools-win-x64-3500100\sqlite3.exe" -Destination "sqlite3.exe" -Force

# Cleanup
Remove-Item -Path "sqlite3.zip" -Force
Remove-Item -Path "sqlite3" -Recurse -Force
```

### Option B: Manual Steps
1. Visit: https://www.sqlite.org/download.html
2. Under "Precompiled Binaries for Windows", download:
   - `sqlite-tools-win-x64-XXXXX.zip`
3. Extract the ZIP file
4. Copy `sqlite3.exe` to your project folder (or add to PATH)

---

## Method 3: Using Chocolatey (if installed)

```cmd
choco install sqlite
```

---

## Method 4: Using winget (Windows Package Manager)

```cmd
winget install SQLite.SQLite
```

---

## Verify Installation

After installation, test with:
```cmd
sqlite3 --version
```

Or test with your database:
```cmd
sqlite3 instance\food_redistribution.db
```

Then in SQLite prompt:
```sql
.tables
SELECT * FROM user;
.exit
```

---

## Quick Commands After Installation

### View tables:
```cmd
sqlite3 instance\food_redistribution.db ".tables"
```

### View all users:
```cmd
sqlite3 instance\food_redistribution.db "SELECT * FROM user;"
```

### Export to CSV:
```cmd
sqlite3 instance\food_redistribution.db -header -csv "SELECT * FROM user;" > users.csv
```

### Interactive mode:
```cmd
sqlite3 instance\food_redistribution.db
```

---

## Troubleshooting

**If PowerShell script is blocked:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**If download fails:**
- Check your internet connection
- Visit https://www.sqlite.org/download.html manually
- Download the latest version

**If sqlite3 not found after installation:**
- Make sure sqlite3.exe is in your project folder, OR
- Add the folder containing sqlite3.exe to your system PATH

