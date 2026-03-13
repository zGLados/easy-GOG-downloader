# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-03-13

### Added
- **Download Tracking System**: Automatically tracks downloaded games in `downloaded_games.json`
- **Incremental Downloads**: `--download-all` now skips already downloaded games
- **Download Summary**: Shows statistics (downloaded/skipped/total) after batch downloads
- **Reset Tracker**: New `--reset-tracker` option to clear download history
- **Auto-create Config**: `get_token.py` automatically creates `config.json` from example on first run

### Changed
- `download_game()` now returns boolean success status for better tracking
- Download progress shows "already downloaded" status for skipped games

### Improved
- Efficient re-running of `--download-all` without re-downloading existing games
- Better user feedback during incremental downloads with progress counters
- Timestamps recorded for each downloaded game for reference

## [1.0.3] - 2026-03-13

### Added
- Automated PyPI publishing via GitHub Actions
- Trusted publishing support (no API tokens needed)

### Changed
- PyPI releases now automatic when pushing version tags
- Simplified release process: just push git tag

## [1.0.2] - 2026-03-13

### Improved
- First-time user experience for pip installations
- Helpful error message with complete setup instructions when config.json is missing
- README with detailed step-by-step first-time setup guide
- Copy-paste ready config.json template in error output

### Fixed
- Missing guidance for pip install users on how to create config.json
- Confusing error message referencing non-existent config.example.json

## [1.0.1] - 2026-03-13

### Added
- PyPI package structure for easy installation via pip
- Console entry points: `gog-downloader`, `gog-get-token`, `gog-test`
- pyproject.toml for modern Python packaging
- MANIFEST.in for including additional files in package

### Changed
- README updated with pip installation instructions as Option 1
- Release workflow simplified to use GitHub source archives
- Root scripts maintained for backward compatibility

### Improved
- Installation now possible via `pip install easy-gog-downloader`
- Cleaner release process using GitHub's automatic archives

## [1.0.0] - 2026-03-13

### Added
- Initial release of Easy GOG Downloader
- Download offline installers from GOG library
- Support for multiple languages (German, English)
- Support for multiple platforms (Windows, Linux, Mac)
- OAuth2 authentication via browser-based token flow
- Resume support for interrupted downloads
- Progress bars with download speed
- Proxy support for corporate networks
- Automatic file naming with version and release year
- Multi-part installer support with correct extensions
- Command-line interface with `--list`, `--download`, `--download-all`
- Configuration via `config.json`
- Token generation helper script (`get_token.py`)
- Validation test tool (`test_tool.py`)

### Features
- **Smart file extensions**: 
  - Single installers: `.exe` (Windows), `.sh` (Linux), `.pkg` (Mac)
  - Multi-part installers: Part 1 gets executable extension, Part 2+ gets `.bin`
- **Organized downloads**: Files saved to `downloads/GameTitle/` directory
- **Custom filename format**: `Title (Version) (Year) (Lang) (Platform).ext`
- **Resume downloads**: Automatically resume interrupted downloads
- **Proxy support**: HTTP/HTTPS proxy configuration
- **Progress tracking**: Real-time progress bars with tqdm

## [Unreleased]

### Planned
- DLC download support
- Extras (artwork, manuals) download
- Parallel downloads
- Language filtering via command-line
- Platform filtering via command-line
