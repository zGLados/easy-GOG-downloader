# Easy GOG Downloader

A tool for downloading offline installers and packages from your GOG library.

## Features

- Download offline installers from your GOG library
- **Smart Download Tracking**: Automatically tracks downloaded games, enabling incremental downloads
- **Incremental Downloads**: Only download new games, skip already downloaded ones
- Support for multiple languages (German, English)
- Support for multiple platforms (Windows, Linux)
- Automatic download organization
- Resume interrupted downloads
- Secure authentication via GOG API
- Optional proxy support for corporate/restricted networks
- Auto-create configuration on first run

## Installation

### Option 1: Via pip (recommended)

```bash
pip install easy-gog-downloader
```

**First-time setup:**

1. Create a config.json file in your working directory:
```bash
cat > config.json << 'EOF'
{
  "credentials": {
    "refresh_token": ""
  },
  "proxy": {
    "enabled": false,
    "http": "",
    "https": ""
  },
  "download": {
    "directory": "./downloads",
    "languages": ["en"],
    "platforms": ["windows"],
    "parallel_downloads": 2,
    "resume": true
  },
  "filters": {
    "include_dlc": true,
    "include_extras": true
  }
}
EOF
```

2. Get your GOG authentication token:
```bash
gog-get-token
```
This will guide you through browser-based authentication and automatically save the token to config.json.

3. Verify your setup:
```bash
gog-test
```

4. Start downloading:
```bash
gog-downloader --list
```

### Option 2: From source

1. Clone or download this repository
2. Install Python 3.8+
3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create configuration:
```bash
cp config.example.json config.json
```

5. Get your GOG refresh token:
   ```bash
   python3 get_token.py
   ```
   Follow the instructions to authenticate via browser

6. Test your setup:
```bash
python3 test_tool.py
```

## Usage

### If installed via pip:

```bash
# List your library
gog-downloader --list

# Download all games (German + English, Windows + Linux)
gog-downloader --download-all

# Download specific game
gog-downloader --download "Game Name"

# Reset download tracker (re-download everything)
gog-downloader --reset-tracker
```

### If running from source:

```bash
# List your library
python gog_downloader.py --list

# Download all games
python gog_downloader.py --download-all

# Download specific game
python gog_downloader.py --download "Game Name"

# Reset download tracker
python gog_downloader.py --reset-tracker
```

### Download Tracking

The tool automatically tracks which games you've downloaded in `downloaded_games.json`. This enables:

- **Incremental downloads**: Run `--download-all` multiple times, only new games are downloaded
- **Resume interrupted sessions**: If downloads are interrupted, restart and continue where you left off
- **Smart updates**: When you buy new games, just run `--download-all` again

**Example workflow:**
```bash
# First time: Download all 50 games
gog-downloader --download-all
# Output: Downloaded: 50, Skipped: 0, Total: 50

# Later: Buy 3 new games
gog-downloader --download-all
# Output: Downloaded: 3, Skipped: 50, Total: 53

# If you want to re-download everything:
gog-downloader --reset-tracker
gog-downloader --download-all
```

The tracker file format:
```json
{
  "games": {
    "1234567": {
      "title": "Cyberpunk 2077",
      "downloaded_at": "2026-03-13T15:30:45"
    }
  }
}
```

### Filtering downloads

With pip installation:
```bash
# Windows versions only
gog-downloader --download-all --platform windows

# German installers only
gog-downloader --download-all --language de

# Specific combination
gog-downloader --download "Cyberpunk 2077" --platform linux --language en
```

With source installation:
```bash
# Windows versions only
python gog_downloader.py --download-all --platform windows

# German installers only
python gog_downloader.py --download-all --language de

# Specific combination
python gog_downloader.py --download "Cyberpunk 2077" --platform linux --language en
```

## Configuration

The `config.json` file contains:
- **GOG credentials**: Refresh token from your GOG account
- **Proxy settings**: Optional HTTP/HTTPS proxy configuration
- **Download directory**: Where files will be saved
- **Default languages and platforms**: By default, only English and Windows installers are downloaded. To download other languages or platforms, add them to the config:
  - Languages: `"languages": ["en", "de", "fr", ...]`
  - Platforms: `"platforms": ["windows", "linux", "mac"]`
- **Download settings**: Resume support, parallel downloads, etc.

### File Naming

Downloaded files are automatically named using this format:
```
Title (Version) (ReleaseYear).extension
```

Examples:
- `Beneath a Steel Sky 1994 (1.0) (2008).exe` - Windows installer
- `Beneath a Steel Sky 1994 (gog-2) (2008).sh` - Linux installer

**Multi-part installers** (large games split across multiple files):
- `BioShock Remastered (1.0.122872) (Part 1).exe` - Setup executable
- `BioShock Remastered (1.0.122872) (Part 2).bin` - Data archive
- `BioShock Remastered (1.0.122872) (Part 3).bin` - Data archive

When multiple language or platform versions exist, they are labeled:
- `Title (Version) (Year) (DE) (W).exe` - German, Windows
- `Title (Version) (Year) (EN) (L).sh` - English, Linux

**Platform codes:** W=Windows, L=Linux, M=Mac

**File extensions:**
- `.exe` - Windows installers (Part 1 of multi-part)
- `.sh` - Linux installers (Part 1 of multi-part)
- `.pkg` - macOS installers (Part 1 of multi-part)
- `.bin` - Data archives (Part 2+ of multi-part installers)

### Proxy Configuration

If you need to use a proxy server, set it in `config.json`:
```json
{
  "proxy": {
    "enabled": true,
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080"
  }
}
```

Leave `enabled: false` and empty strings if no proxy is needed.

## Notes

- Authentication is done via the official GOG API
- Your credentials are stored locally only
- Downloads are only possible for games you own
- Large downloads may take time

## License

MIT License
