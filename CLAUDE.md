# Music Screen API Guidelines

## Main Code Files
- **Main hook script**: `go_sonos_hook.py` - Main webhook/polling controller for display updates
- **Main display script**: `go_sonos_highres.py` - High resolution display controller
- **Display controller**: `display_controller.py` - GUI interface and hardware display management
- **Ink printer**: `ink_printer.py` - E-ink display formatting and rendering
- **Demaster module**: `demaster.py` - Strips "Remastered" and other text from track names
- **Async demaster**: `async_demaster.py` - Async version of demaster with API fallback
- **Sonos data**: `sonos_user_data.py` - Sonos API integration for track/player data
- **LastFM data**: `lastfm_user_data.py` - LastFM API integration for track statistics

## Commands
- Run main display: `python3 go_sonos_highres.py`
- Run main hook: `python3 go_sonos_hook.py [room_name]`
- Startup script: `./music-screen-api-startup.sh`
- Install dependencies: `pip3 install -r requirements.txt`
- Test Spotify integration: `python3 spotipy_auth_search_test.py`

## Running as a Service
To run the hook script as a systemd service, create a service file:

```bash
sudo nano /etc/systemd/system/go_sonos.service
```

Service file content:
```ini
[Unit]
Description=Go Sonos Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/music-screen-api
ExecStart=/usr/bin/python3 go_sonos_hook.py [room_name]
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable go_sonos.service
sudo systemctl start go_sonos.service
sudo systemctl status go_sonos.service
```

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