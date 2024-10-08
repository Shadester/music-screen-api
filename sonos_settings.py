### Sonos settings

## General settings

# Connection details for `node-sonos-http-api`
sonos_http_api_address = "192.168.1.31"
sonos_http_api_port = "5005"

# Location of log file to write in addition to printing to screen. Comment out to disable
log_file = "/home/pi/music-screen-api.log"

# One of ERROR, WARNING, INFO, DEBUG (in order of least to most verbose)
log_level = "INFO"

# Crop song and album names to remove nonsense such as "Remastered" or "live at"
demaster = True

# Send track and album names to http://demaster.hankapi.com for more advanced track name cleanup
demaster_query_cloud = True

## High-res only settings

#Spotify Developer API Details (only required if show_spotify_code = True or show_spotify_albumart = True), uncomment and add your apps details to use
#spotify_client_id = ""
#spotify_client_secret = ""
spotify_market = None

# Show a Spotify Code graphic for the currently playing song if playing from Spotify, can be displayed if 'show_details' is either True or False.
show_spotify_code = False

#Overide the albumart with that from Spotify if available
show_spotify_albumart = False

# Room name of Sonos speaker(s) to track
room_name_for_highres = ""

# Display track name in addition to album art
show_details = False

# Seconds to show detail view on track changes before returning to full-screen album art. Ignored if 'show_details' is False. Comment out to disable feature.
show_details_timeout = 10

# Also display artist and album with track name. Ignored if 'show_details' is False.
show_artist_and_album = True

# Display artist and album with track name with a new look. Ignored if 'show_details' is False.
artist_and_album_newlook = True

# Display Track, Album and Artist Information over fullscreen Album Art
overlay_text = True

# Also displaying state (volume, repeat, shuffle and crossfade) . Ignored if 'show_details' is False.
show_play_state = True

# Turn off display (and backlight) when Sonos is playing from a TV source
sleep_on_tv = False

# Turn off display (and backlight) when Sonos is playing from a Line-In source
sleep_on_linein = False


## e-ink only settings

# Set to True if running on a Pi Zero along with `node-sonos-http-api` to mitigate long startup times and other performance limitations.
pi_zero = False
