# Tutorial

## Step-by-Step Guide

### 1. Installation

Ensure Python 3.8+ is installed:
```bash
python3 --version
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Obtain GOG Refresh Token

You need a refresh token to authenticate with the GOG API.

**Use the automated token helper:**
```bash
python3 get_token.py
```

The script will:
1. Display an authentication URL
2. You open it in your browser and log in to GOG
3. After login, copy the redirect URL from your browser
4. Paste it into the script
5. The script automatically exchanges it for a refresh token and saves it to config.json

**Manual steps if needed:**
1. Run `python3 get_token.py`
2. Copy the displayed URL
3. Open it in your browser
4. Log in to GOG
5. After redirect, copy the complete URL from address bar (contains `code=...`)
6. Paste it when prompted

### 3. Create Configuration

```bash
cp config.example.json config.json
```

Open `config.json` and insert your refresh token:
```json
{
  "credentials": {
    "refresh_token": "YOUR_TOKEN_HERE"
  },
  "download": {
    "directory": "./downloads",
    "languages": ["de", "en"],
    "platforms": ["windows", "linux"],
    "parallel_downloads": 2,
    "resume": true
  },
  "filters": {
    "include_dlc": true,
    "include_extras": true
  }
}
```

### 4. Testing

List your library:
```bash
python3 gog_downloader.py --list
```

### 5. Start Download

Download all games:
```bash
python3 gog_downloader.py --download-all
```

Download specific game:
```bash
python3 gog_downloader.py --download "The Witcher 3"
```

Windows versions only:
```bash
python3 gog_downloader.py --download-all --platform windows
```

German installers only:
```bash
python3 gog_downloader.py --download-all --language de
```

## Advanced Options

### Customize Configuration

In `config.json` you can configure:

- **languages**: List of desired languages (`["de", "en", "fr", "pl"]`)
- **platforms**: Platforms (`["windows", "linux", "mac"]`)
- **directory**: Target directory for downloads
- **resume**: Resume interrupted downloads
- **include_dlc**: Include DLCs in downloads
- **include_extras**: Include extras (wallpapers, soundtracks, etc.)

### Downloaded File Naming

Files are automatically named using a standardized format:

**Format:** `Title (Version) (ReleaseYear).extension`

**Examples:**
```
Lego Star Wars (1.0) (2005).zip
Witcher 3 (4.04) (2015).exe
Cyberpunk 2077 (1.5) (2020).bin
```

**When multiple versions exist** (different languages/platforms):
```
Title (Version) (Year) (DE) (W).zip  - German, Windows
Title (Version) (Year) (EN) (L).bin  - English, Linux
```

Platform codes:
- **W** = Windows
- **L** = Linux  
- **M** = Mac

This naming scheme makes it easy to:
- Identify game versions at a glance
- Sort files chronologically
- Manage multi-platform installations

### Proxy Configuration

If you need to connect through a proxy server, edit the proxy section in `config.json`:

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://your-proxy.com:8080",
    "https": "http://your-proxy.com:8080"
  }
}
```

**Important notes:**
- Set `enabled: true` to activate proxy
- Use `http://` prefix even for HTTPS proxy (this is the proxy protocol)
- Leave `enabled: false` and empty strings if no proxy is needed
- The tool will show "Using proxy: ..." when proxy is active

Example with corporate proxy:
```json
{
  "proxy": {
    "enabled": true,
    "http": "http://proxy.company.com:8080",
    "https": "http://proxy.company.com:8080"
  }
}
```

### Examples

Linux + English only:
```bash
python3 gog_downloader.py --download-all --platform linux --language en
```

Specific game with all languages:
```bash
python3 gog_downloader.py --download "Cyberpunk 2077"
```

## Troubleshooting

### Authentication failed
- Check if your refresh token is correct
- Tokens may expire - get a new one with `get_token.py`

### No matching installers found
- The game may not be available for the selected platform/language
- Check available options with `--list`

### Download fails
- Check your internet connection
- Try again - the tool supports resume

## Tips

1. **Large Library**: Downloading all games can take a very long time and require a lot of storage space
2. **Network**: Downloads may be interrupted with slow connections - enable `resume: true`
3. **API Limits**: The tool waits 2 seconds between games to avoid overloading the API
4. **Organization**: Each game is saved in its own subdirectory
