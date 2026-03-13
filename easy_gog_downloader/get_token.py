#!/usr/bin/env python3
"""
Manual GOG Token Getter
Gets refresh token through manual browser workflow
"""

import requests
import json
import urllib.parse

CLIENT_ID = "46899977096215655"
CLIENT_SECRET = "9d85c43b1482497dbbce61f6e4aa173a433796eeae2ca8c5f6129f2dc4de46d9"
REDIRECT_URI = "https://embed.gog.com/on_login_success?origin=client"

print("="*70)
print("GOG Refresh Token - Manual Method")
print("="*70)
print()
print("STEP 1: Copy this URL and open it in your browser:")
print()

auth_url = (
    f"https://auth.gog.com/auth?"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
    f"response_type=code&"
    f"layout=client2"
)

print(auth_url)
print()
print("="*70)
print()
print("STEP 2: After logging in, you will be redirected to a page that shows:")
print('        "Login successful" or similar')
print()
print("STEP 3: Look at the URL in your browser address bar.")
print("        It will look something like:")
print("        https://embed.gog.com/on_login_success?origin=client&code=XXXXX...")
print()
print("STEP 4: Copy the ENTIRE URL and paste it below:")
print()

redirect_url = input("Paste the redirect URL here: ").strip()

if not redirect_url:
    print("\nERROR: No URL provided")
    exit(1)

# Extract code from URL
try:
    parsed = urllib.parse.urlparse(redirect_url)
    params = urllib.parse.parse_qs(parsed.query)
    
    if 'code' not in params:
        print("\nERROR: No 'code' parameter found in URL")
        print("Make sure you copied the complete URL")
        exit(1)
    
    auth_code = params['code'][0]
    print(f"\n✓ Found authorization code (length: {len(auth_code)})")

except Exception as e:
    print(f"\nERROR: Could not parse URL: {e}")
    exit(1)

# Exchange code for tokens
print("\nSTEP 5: Exchanging code for tokens...")

# Check if proxy is configured
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        proxies = None
        if config.get("proxy", {}).get("enabled", False):
            proxies = {
                "http": config["proxy"].get("http"),
                "https": config["proxy"].get("https")
            }
            print(f"Using proxy: {proxies.get('https')}")
except:
    proxies = None

token_url = "https://auth.gog.com/token"
data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": REDIRECT_URI
}

try:
    response = requests.post(token_url, data=data, proxies=proxies)
    response.raise_for_status()
    tokens = response.json()
    
    if 'refresh_token' not in tokens:
        print("\nERROR: No refresh_token in response")
        print("Response:", json.dumps(tokens, indent=2))
        exit(1)
    
    refresh_token = tokens['refresh_token']
    
    print("\n" + "="*70)
    print("SUCCESS! Here is your refresh token:")
    print("="*70)
    print()
    print(refresh_token)
    print()
    print("="*70)
    print()
    print("This token will be automatically saved to config.json")
    print()
    
    # Update config.json
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        config['credentials']['refresh_token'] = refresh_token
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✓ config.json updated successfully!")
        print()
        print("You can now run: python3 test_tool.py")
        print()
        
    except Exception as e:
        print(f"WARNING: Could not update config.json: {e}")
        print("Please manually add the token to config.json")
        print()
    
except requests.exceptions.HTTPError as e:
    print(f"\nERROR: Token exchange failed: {e}")
    print(f"Response: {e.response.text}")
    exit(1)
except Exception as e:
    print(f"\nERROR: {e}")
    exit(1)
