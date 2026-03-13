"""Easy GOG Downloader - Download offline installers from your GOG library."""

__version__ = "1.0.3"
__author__ = "zGLados"
__license__ = "MIT"

from easy_gog_downloader.gog_downloader import (
    GOGAuthenticator,
    GOGLibrary,
    GOGDownloader,
)

__all__ = [
    "GOGAuthenticator",
    "GOGLibrary",
    "GOGDownloader",
]
