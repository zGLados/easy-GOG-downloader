# Easy GOG Downloader

A tool for downloading offline installers and packages from your GOG library.

## Features

- Download offline installers from your GOG library
- Support for multiple languages (German, English)
- Support for multiple platforms (Windows, Linux)
- Automatic download organization
- Resume interrupted downloads
- Secure authentication via GOG API
- Optional proxy support for corporate/restricted networks

## Installation

1. Install Python 3.8+
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration:
```bash
cp config.example.json config.json
```

4. Get your GOG refresh token:
   ```bash
   python3 manual_get_token.py
   ```
   Follow the instructions to authenticate via browser

5. Test your setup:
```bash
python3 test_tool.py
```

## Usage

### List your library
```bash
python gog_downloader.py --list
```

### Download all games (German + English, Windows + Linux)
```bash
python gog_downloader.py --download-all
```

### Download specific game
```bash
python gog_downloader.py --download "Game Name"
```

### Using filters
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
- **Default languages and platforms**: Filter settings
- **Download settings**: Resume support, parallel downloads, etc.

### File Naming

Downloaded files are automatically named using this format:
```
Title (Version) (ReleaseYear).extension
```

Examples:
- `Lego Star Wars (1.0) (2005).zip`
- `Witcher 3 (4.04) (2015).exe`

When multiple language or platform versions exist:
- `Title (Version) (Year) (DE) (W).zip` - German, Windows
- `Title (Version) (Year) (EN) (L).bin` - English, Linux

Platform codes: W=Windows, L=Linux, M=Mac

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
