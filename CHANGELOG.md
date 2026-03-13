# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
