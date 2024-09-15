# Music Screen API Guidelines

## Commands
- Run main display: `python3 go_sonos_highres.py`
- Startup script: `./music-screen-api-startup.sh`
- Install dependencies: `pip3 install -r requirements.txt`
- Test Spotify integration: `python3 spotipy_auth_search_test.py`

## Code Style
- **Imports**: Standard library first, third-party second, local modules last
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Use try/except with specific exceptions
- **Documentation**: Docstrings for functions and classes
- **Async**: Use async/await for network operations
- **Configuration**: Store settings in sonos_settings.py (copy from example first)
- **Logging**: Use structured logging with appropriate levels
- **Type Hints**: Add type annotations to function parameters and returns

## Architecture
- Display controller interfaces with Sonos API via HTTP
- User data retrieval from Sonos/Spotify/LastFM APIs
- Image processing for album art display