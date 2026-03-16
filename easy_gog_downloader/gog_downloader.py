#!/usr/bin/env python3
"""
Easy GOG Downloader
Downloads offline installers from your GOG library
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm
import time
import signal
import select

# Global flag for graceful shutdown
_stop_requested = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global _stop_requested
    if not _stop_requested:
        print("\n\nDownload interrupted by user. Progress has been saved.")
        print("   Run the command again to resume from where you left off.\n")
        _stop_requested = True
        sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)


class GOGAuthenticator:
    """Handles GOG API authentication"""
    
    AUTH_URL = "https://auth.gog.com/token"
    CLIENT_ID = "46899977096215655"
    CLIENT_SECRET = "9d85c43b1482497dbbce61f6e4aa173a433796eeae2ca8c5f6129f2dc4de46d9"
    REDIRECT_URI = "https://embed.gog.com/on_login_success?origin=client"
    
    def __init__(self, refresh_token: str, proxies: Optional[Dict] = None):
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expiry = 0
        self.proxies = proxies
    
    def get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
        
        data = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(self.AUTH_URL, data=data, proxies=self.proxies)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            self.token_expiry = time.time() + token_data["expires_in"] - 60
            
            return self.access_token
        except Exception as e:
            raise Exception(f"Authentication failed: {e}")


class GOGLibrary:
    """Manages GOG library operations"""
    
    API_BASE = "https://api.gog.com"
    EMBED_BASE = "https://embed.gog.com"
    
    def __init__(self, authenticator: GOGAuthenticator):
        self.auth = authenticator
        self.proxies = authenticator.proxies
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated API request"""
        headers = {
            "Authorization": f"Bearer {self.auth.get_access_token()}"
        }
        response = requests.get(url, headers=headers, params=params, proxies=self.proxies)
        response.raise_for_status()
        return response.json()
    
    def get_owned_games(self) -> List[Dict]:
        """Fetch all owned games from library"""
        games = []
        page = 1
        
        print("Fetching your GOG library...")
        
        while True:
            url = f"{self.EMBED_BASE}/account/getFilteredProducts"
            params = {
                "mediaType": "1",  # Games
                "page": page
            }
            
            data = self._make_request(url, params)
            products = data.get("products", [])
            
            if not products:
                break
            
            games.extend(products)
            
            if len(products) < data.get("limit", 50):
                break
            
            page += 1
        
        print(f"Found {len(games)} games in your library")
        return games
    
    def get_game_details(self, game_id: int) -> Dict:
        """Get detailed information about a specific game"""
        url = f"{self.API_BASE}/products/{game_id}"
        params = {"expand": "downloads"}
        return self._make_request(url, params)
    
    def get_download_links(self, game_id: int) -> Dict:
        """Get download links for a game"""
        url = f"{self.EMBED_BASE}/account/gameDetails/{game_id}.json"
        return self._make_request(url)


class GOGDownloader:
    """Handles game downloads"""
    
    def __init__(self, authenticator: GOGAuthenticator, config: Dict):
        self.auth = authenticator
        self.config = config
        self.library = GOGLibrary(authenticator)
        self.download_dir = Path(config["download"]["directory"])
        self.proxies = authenticator.proxies
        self.tracker_file = Path("downloaded_games.json")
        self.downloaded_games = self._load_tracker()
        self.tracker_file = Path("downloaded_games.json")
        self.downloaded_games = self._load_tracker()
    
    def _load_tracker(self) -> Dict:
        """Load the download tracker from file"""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load tracker file: {e}")
                return {"games": {}}
        return {"games": {}}
    
    def _save_tracker(self) -> None:
        """Save the download tracker to file"""
        try:
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(self.downloaded_games, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save tracker file: {e}")
    
    def _mark_game_downloaded(self, game_id: int, title: str) -> None:
        """Mark a game as downloaded in the tracker"""
        import datetime
        self.downloaded_games["games"][str(game_id)] = {
            "title": title,
            "downloaded_at": datetime.datetime.now().isoformat()
        }
        self._save_tracker()
    
    def _is_game_downloaded(self, game_id: int) -> bool:
        """Check if a game has already been downloaded"""
        return str(game_id) in self.downloaded_games["games"]
    
    def reset_tracker(self) -> None:
        """Reset the download tracker"""
        self.downloaded_games = {"games": {}}
        self._save_tracker()
        print(f"Download tracker reset: {self.tracker_file}")
    
    def download_file(self, url: str, filepath: Path, resume: bool = True) -> bool:
        """Download a file with progress bar and resume support"""
        global _stop_requested
        
        if _stop_requested:
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth.get_access_token()}"
        }
        
        # Check if file exists and get size for resume
        start_byte = 0
        if resume and filepath.exists():
            start_byte = filepath.stat().st_size
            headers["Range"] = f"bytes={start_byte}-"
        
        mode = "ab" if start_byte > 0 else "wb"
        
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=30, proxies=self.proxies)
            
            # Handle 416 Range Not Satisfiable - file is already complete
            if response.status_code == 416:
                print(f"Already downloaded (complete): {filepath.name}")
                return True
            
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            if start_byte > 0:
                total_size += start_byte
            
            # Create parent directory if needed
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, mode, encoding=None) as f:
                with tqdm(
                    total=total_size,
                    initial=start_byte,
                    unit="B",
                    unit_scale=True,
                    desc=filepath.name + " (Press 'q' to stop)"
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if _stop_requested:
                            print("\nDownload paused. Progress saved.")
                            return False
                        
                        # Check for 'q' key press (non-blocking)
                        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                            key = sys.stdin.read(1)
                            if key.lower() == 'q':
                                print("\n\nDownload stopped by user. Progress has been saved.")
                                print("   Run the command again to resume from where you left off.\n")
                                _stop_requested = True
                                return False
                        
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 416:
                print(f"Already downloaded (complete): {filepath.name}")
                return True
            print(f"HTTP Error downloading {filepath.name}: {e}")
            return False
        except Exception as e:
            print(f"Error downloading {filepath.name}: {e}")
            return False
    
    def filter_downloads(self, downloads: List[Dict]) -> List[Dict]:
        """Filter downloads by language and platform"""
        languages = self.config["download"]["languages"]
        platforms = self.config["download"]["platforms"]
        
        filtered = []
        
        for download in downloads:
            # Check language
            lang = download.get("language", "en")
            if lang not in languages and "en" not in [lang, "English"]:
                continue
            
            # Check platform
            platform = download.get("os", "").lower()
            if not any(p in platform for p in platforms):
                continue
            
            filtered.append(download)
        
        return filtered
    
    def download_game(self, game_id: int, game_title: str) -> bool:
        """Download all files for a game
        
        Returns True if at least one file was successfully downloaded or already exists, False otherwise
        """
        print(f"\nProcessing: {game_title}")
        
        success = False
        
        try:
            details = self.library.get_download_links(game_id)
        except Exception as e:
            print(f"Failed to get download links: {e}")
            return False
        
        # Get additional game info for filename formatting
        try:
            game_info = self.library.get_game_details(game_id)
            release_year = None
            if game_info.get("release_date"):
                # Extract year from release_date
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', str(game_info.get("release_date")))
                if year_match:
                    release_year = year_match.group(0)
        except:
            release_year = None
        
        # Parse downloads structure - GOG API returns list of [language, platforms]
        downloads_data = details.get("downloads", [])
        
        all_installers = []
        if isinstance(downloads_data, list):
            # New API format: list of [language, {platform: [installers]}]
            for item in downloads_data:
                if not isinstance(item, list) or len(item) < 2:
                    continue
                language = item[0]  # e.g. "English", "German"
                platforms = item[1]  # dict with "windows", "linux", "mac"
                
                for platform_name, installers in platforms.items():
                    if not isinstance(installers, list):
                        continue
                    for installer in installers:
                        # Add metadata for filtering
                        installer['language'] = language.lower()[:2]  # "English" -> "en"
                        installer['os'] = platform_name
                        all_installers.append(installer)
        elif isinstance(downloads_data, dict):
            # Old API format: dict with "installers" key
            all_installers = downloads_data.get("installers", [])
        
        filtered_installers = self.filter_downloads(all_installers)
        
        if not filtered_installers:
            print("No matching installers found")
            return False
        
        print(f"Found {len(filtered_installers)} installer(s) to download")
        
        # Create game directory with formatted name
        safe_title = "".join(c for c in game_title if c.isalnum() or c in " -_").strip()
        game_dir = self.download_dir / safe_title
        
        for installer in filtered_installers:
            name = installer.get("name", "installer")
            language = installer.get("language", "unknown")
            os_name = installer.get("os", "unknown")
            version = installer.get("version", "")
            
            print(f"\n{name} ({language}, {os_name})")
            
            # Get download link
            manual_url = installer.get("manualUrl")
            file_id = installer.get("id")
            
            if not manual_url and not file_id:
                print("No download URL available")
                continue
            
            # Construct download URL
            if manual_url:
                # New API format with manualUrl
                download_url = f"https://www.gog.com{manual_url}"
            else:
                # Old API format with file_id
                download_url = f"https://api.gog.com/products/{game_id}/downlink/installer/{file_id}"
            
            try:
                # Get actual download URL
                headers = {"Authorization": f"Bearer {self.auth.get_access_token()}"}
                link_response = requests.get(download_url, headers=headers, allow_redirects=False, proxies=self.proxies)
                
                if link_response.status_code in [301, 302, 303, 307, 308]:
                    actual_url = link_response.headers.get("Location")
                else:
                    actual_url = link_response.json().get("downlink")
                
                if not actual_url:
                    print("Could not get download URL")
                    continue
                
                # Determine correct file extension based on installer type
                # Check if this is a multi-part installer (e.g., "Game (Part 2 of 5)")
                import re
                part_match = re.search(r'\(Part (\d+) of (\d+)\)', name)
                
                if part_match:
                    # Multi-part installer
                    part_num = int(part_match.group(1))
                    if part_num == 1:
                        # Part 1 is the executable installer
                        if "windows" in os_name.lower():
                            file_extension = "exe"
                        elif "linux" in os_name.lower():
                            file_extension = "sh"
                        elif "mac" in os_name.lower():
                            file_extension = "pkg"
                        else:
                            file_extension = "bin"
                    else:
                        # Part 2+ are data archives, keep as .bin
                        file_extension = "bin"
                else:
                    # Single installer - use platform-specific extension
                    if "windows" in os_name.lower():
                        file_extension = "exe"
                    elif "linux" in os_name.lower():
                        file_extension = "sh"
                    elif "mac" in os_name.lower():
                        file_extension = "pkg"
                    else:
                        file_extension = "bin"
                
                # Build filename parts
                filename_parts = [safe_title]
                if version:
                    filename_parts.append(f"({version})")
                if release_year:
                    filename_parts.append(f"({release_year})")
                
                # Add part number for multi-part installers
                if part_match:
                    part_num = int(part_match.group(1))
                    total_parts = int(part_match.group(2))
                    filename_parts.append(f"(Part {part_num})")
                
                # Add language and platform if multiple options exist
                if len(filtered_installers) > 1:
                    if language and language != "en":
                        filename_parts.append(f"({language.upper()})")
                    if os_name:
                        os_short = "W" if "windows" in os_name.lower() else "L" if "linux" in os_name.lower() else "M"
                        filename_parts.append(f"({os_short})")
                
                filename = f"{' '.join(filename_parts)}.{file_extension}"
                filepath = game_dir / filename
                
                if filepath.exists() and filepath.stat().st_size == installer.get("size", 0):
                    print(f"Already downloaded: {filename}")
                    success = True
                    continue
                
                # Download
                if self.download_file(actual_url, filepath, self.config["download"]["resume"]):
                    print(f"Downloaded: {filename}")
                    success = True
                else:
                    print(f"Failed: {filename}")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        # Process extras if enabled
        if self.config["filters"]["include_extras"]:
            all_extras = []
            if isinstance(downloads_data, list):
                # New API format: find bonus content in the structure
                # Usually bonus content is in a separate section
                bonus_data = details.get("bonus_content", [])
                if isinstance(bonus_data, list):
                    for item in bonus_data:
                        if isinstance(item, dict):
                            all_extras.append(item)
            else:
                # Old API format
                all_extras = downloads_data.get("bonus_content", [])
            
            if all_extras:
                print(f"\nFound {len(all_extras)} extra(s)")
                extras_dir = game_dir / "extras"
                
                for extra in all_extras[:5]:  # Limit extras for now
                    name = extra.get("name", "extra")
                    print(f"  • {name}")
        
        return success
    
    def list_library(self) -> None:
        """List all games in library"""
        games = self.library.get_owned_games()
        
        print("\nYour GOG Library:\n")
        for i, game in enumerate(games, 1):
            title = game.get("title", "Unknown")
            print(f"{i}. {title}")
    
    def download_all(self) -> None:
        """Download all games from library"""
        games = self.library.get_owned_games()
        
        # Count how many are already downloaded
        already_downloaded = sum(1 for g in games if self._is_game_downloaded(g.get("id")))
        to_download = len(games) - already_downloaded
        
        print(f"\nLibrary: {len(games)} games")
        print(f"Already downloaded: {already_downloaded}")
        print(f"To download: {to_download}")
        print(f"\nStarting downloads...")
        
        downloaded_count = 0
        skipped_count = 0
        
        for i, game in enumerate(games, 1):
            if _stop_requested:
                break
            
            title = game.get("title", "Unknown")
            game_id = game.get("id")
            
            if not game_id:
                continue
            
            # Skip already downloaded games
            if self._is_game_downloaded(game_id):
                print(f"\n[{i}/{len(games)}] Already downloaded: {title}")
                skipped_count += 1
                continue
            
            print(f"\n[{i}/{len(games)}] Downloading: {title}")
            
            if self.download_game(game_id, title):
                self._mark_game_downloaded(game_id, title)
                downloaded_count += 1
                print(f"Marked as downloaded: {title}")
            
            # Be nice to the API
            time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"Download Summary:")
        print(f"  Downloaded: {downloaded_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Total: {len(games)}")
        print(f"{'='*70}")
    
    def download_by_title(self, search_title: str) -> None:
        """Download a specific game by title"""
        games = self.library.get_owned_games()
        
        # Find matching game
        matches = [g for g in games if search_title.lower() in g.get("title", "").lower()]
        
        if not matches:
            print(f"No game found matching: {search_title}")
            return
        
        if len(matches) > 1:
            print(f"Multiple matches found:")
            for i, game in enumerate(matches, 1):
                print(f"{i}. {game.get('title')}")
            print("\nDownloading all matches...")
        
        for game in matches:
            self.download_game(game.get("id"), game.get("title"))


def load_config(config_path: str = "config.json") -> Dict:
    """Load configuration from file"""
    if not os.path.exists(config_path):
        print(f"\nConfiguration file not found: {config_path}")
        print("\nFirst time setup:")
        print("   1. Create a config file:")
        print(f"      cat > {config_path} << 'EOF'")
        print("      {")
        print("        \"credentials\": {")
        print("          \"refresh_token\": \"\"")
        print("        },")
        print("        \"proxy\": {")
        print("          \"enabled\": false,")
        print("          \"http\": \"\",")
        print("          \"https\": \"\"")
        print("        },")
        print("        \"download\": {")
        print("          \"directory\": \"./downloads\",")
        print("          \"languages\": [\"de\", \"en\"],")
        print("          \"platforms\": [\"windows\", \"linux\"],")
        print("          \"parallel_downloads\": 2,")
        print("          \"resume\": true")
        print("        },")
        print("        \"filters\": {")
        print("          \"include_dlc\": true,")
        print("          \"include_extras\": true")
        print("        }")
        print("      }")
        print("      EOF")
        print("\n   2. Get your GOG token:")
        print("      gog-get-token")
        print("\n   3. Test your setup:")
        print("      gog-test")
        print("\n   4. List your games:")
        print("      gog-downloader --list")
        print("\nFor more info: https://github.com/zGLados/easy-GOG-downloader\n")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Easy GOG Downloader - Download offline installers from your GOG library"
    )
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--list", action="store_true", help="List all games in library")
    parser.add_argument("--download-all", action="store_true", help="Download all games")
    parser.add_argument("--download", type=str, help="Download specific game by title")
    parser.add_argument("--platform", type=str, help="Filter by platform (windows, linux)")
    parser.add_argument("--language", type=str, help="Filter by language (de, en)")
    parser.add_argument("--reset-tracker", action="store_true", help="Reset the download tracker (forget all downloaded games)")
    
    args = parser.parse_args()
    
    # Handle reset-tracker command (doesn't require authentication)
    if args.reset_tracker:
        tracker_file = Path("downloaded_games.json")
        if tracker_file.exists():
            tracker_file.unlink()
            print(f"Download tracker reset: {tracker_file}")
        else:
            print(f"No tracker file found (already clean)")
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with CLI arguments
    if args.platform:
        config["download"]["platforms"] = [args.platform]
    if args.language:
        config["download"]["languages"] = [args.language]
    
    # Check for refresh token
    refresh_token = config.get("credentials", {}).get("refresh_token")
    if not refresh_token or refresh_token == "YOUR_GOG_REFRESH_TOKEN_HERE":
        print("No valid refresh token found in config.json")
        print("\nTo get your refresh token:")
        print("1. Log into GOG.com in your browser")
        print("2. Open browser console (F12)")
        print("3. Go to Application/Storage -> Cookies -> https://gog.com")
        print("4. Find 'gog_al' cookie and copy its value")
        print("5. That's your refresh token - add it to config.json")
        sys.exit(1)
    
    # Setup proxies if configured
    proxies = None
    if config.get("proxy", {}).get("enabled", False):
        proxies = {
            "http": config["proxy"].get("http"),
            "https": config["proxy"].get("https")
        }
        print(f"Using proxy: {proxies.get('https')}")
    
    # Initialize
    print("Authenticating with GOG...")
    auth = GOGAuthenticator(refresh_token, proxies)
    downloader = GOGDownloader(auth, config)
    
    try:
        auth.get_access_token()
        print("Authentication successful")
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)
    
    # Execute command
    if args.list:
        downloader.list_library()
    elif args.download_all:
        downloader.download_all()
    elif args.download:
        downloader.download_by_title(args.download)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
