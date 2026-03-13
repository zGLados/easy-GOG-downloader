#!/usr/bin/env python3
"""
Quick test script for GOG downloader
"""

import json
import sys
import os

def test_config():
    """Test if config.json is properly set up"""
    print("Step 1: Checking config.json...")
    
    if not os.path.exists("config.json"):
        print("  ERROR: config.json not found")
        return False
    
    with open("config.json", 'r') as f:
        config = json.load(f)
    
    token = config.get("credentials", {}).get("refresh_token", "")
    
    if not token or token == "YOUR_GOG_REFRESH_TOKEN_HERE":
        print("  ERROR: No valid refresh token in config.json")
        print("  Please add your GOG refresh token to config.json")
        return False
    
    print("  OK: Config file looks good")
    print(f"  Token length: {len(token)} characters")
    return True

def test_imports():
    """Test if all required modules are available"""
    print("\nStep 2: Checking Python dependencies...")
    
    try:
        import requests
        print(f"  OK: requests {requests.__version__}")
    except ImportError:
        print("  ERROR: requests not installed")
        return False
    
    try:
        import tqdm
        print(f"  OK: tqdm {tqdm.__version__}")
    except ImportError:
        print("  ERROR: tqdm not installed")
        return False
    
    return True

def test_authentication():
    """Test GOG authentication"""
    print("\nStep 3: Testing GOG authentication...")
    
    try:
        from gog_downloader import GOGAuthenticator, load_config
        
        config = load_config()
        token = config["credentials"]["refresh_token"]
        
        # Setup proxies if configured
        proxies = None
        if config.get("proxy", {}).get("enabled", False):
            proxies = {
                "http": config["proxy"].get("http"),
                "https": config["proxy"].get("https")
            }
            print(f"  Using proxy: {proxies.get('https')}")
        
        auth = GOGAuthenticator(token, proxies)
        access_token = auth.get_access_token()
        
        if access_token:
            print("  OK: Authentication successful!")
            print(f"  Access token received: {access_token[:30]}...")
            return True
        else:
            print("  ERROR: No access token received")
            return False
            
    except Exception as e:
        print(f"  ERROR: Authentication failed: {e}")
        return False

def test_library():
    """Test fetching library"""
    print("\nStep 4: Testing library access...")
    
    try:
        from gog_downloader import GOGAuthenticator, GOGLibrary, load_config
        
        config = load_config()
        
        # Setup proxies if configured
        proxies = None
        if config.get("proxy", {}).get("enabled", False):
            proxies = {
                "http": config["proxy"].get("http"),
                "https": config["proxy"].get("https")
            }
        
        auth = GOGAuthenticator(config["credentials"]["refresh_token"], proxies)
        library = GOGLibrary(auth)
        
        games = library.get_owned_games()
        
        print(f"  OK: Found {len(games)} games in your library")
        
        if games:
            print("\n  First 5 games:")
            for i, game in enumerate(games[:5], 1):
                print(f"    {i}. {game.get('title', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ERROR: Library access failed: {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("GOG Downloader - Test Suite")
    print("="*70)
    print()
    
    # Run tests
    tests_passed = 0
    tests_total = 4
    
    if test_config():
        tests_passed += 1
    else:
        print("\n" + "="*70)
        print("STOPPED: Fix config.json first")
        print("="*70)
        sys.exit(1)
    
    if test_imports():
        tests_passed += 1
    else:
        print("\n" + "="*70)
        print("STOPPED: Install missing dependencies")
        print("Run: pip install -r requirements.txt")
        print("="*70)
        sys.exit(1)
    
    if test_authentication():
        tests_passed += 1
    else:
        print("\n" + "="*70)
        print("STOPPED: Authentication failed")
        print("Check your refresh token in config.json")
        print("="*70)
        sys.exit(1)
    
    if test_library():
        tests_passed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("SUCCESS: All tests passed! The tool is ready to use.")
        print("\nTry these commands:")
        print("  python3 gog_downloader.py --list")
        print("  python3 gog_downloader.py --download 'Game Name'")
    else:
        print("FAILED: Some tests did not pass")
    print("="*70)
