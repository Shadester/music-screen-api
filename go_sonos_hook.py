import time
import sonos_user_data_legacy as sonos_user_data
import sys
import ink_printer
import sonos_settings
import demaster
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# User variables
polling_frequency = 1 if sonos_settings.pi_zero else 4
pause_sleep_timeout = 5  # Sleep after 5 seconds of PAUSED_PLAYBACK
inactive_sleep_timeout = 40  # Sleep after 40 seconds of other inactivity
sleep_mode_output = "logo"  # can also be "blank"

# Global variables
previous_track_name = ""
sleep_mode_sleeping = False
last_activity_time = time.time()
last_status = "PLAYING"
sonos_room = ""

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

# Webhook handler
class SonosWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        update_display(source="webhook")

    def log_message(self, format, *args):
        # Suppress default logging from BaseHTTPRequestHandler
        return

def start_webhook_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SonosWebhookHandler)
    logging.info(f"Webhook server started on port {port}")
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

def update_display(source="polling"):
    global previous_track_name, sleep_mode_sleeping, last_activity_time, last_status

    current_track, current_artist, current_album, current_image, play_status = sonos_user_data.current(sonos_room)
    
    log_message = f"{source.capitalize()}: {play_status} - "
    current_time = time.time()

    if play_status == "PLAYING":
        last_activity_time = current_time
        last_status = play_status
        if sleep_mode_sleeping:
            sleep_mode_sleeping = False
            log_message += "Waking up. "

        if current_track != previous_track_name:
            previous_track_name = current_track
            if sonos_settings.demaster:
                current_track = demaster.strip_name(current_track)
            log_message += f"New track: {current_track} - {current_artist}"
            ink_printer.print_text_to_ink(current_track, current_artist, current_album)
        else:
            log_message += f"Current track: {current_track} (no change)"
    else:  # PAUSED_PLAYBACK or other non-playing states
        time_since_activity = current_time - last_activity_time
        sleep_timeout = pause_sleep_timeout if play_status == "PAUSED_PLAYBACK" else inactive_sleep_timeout

        if not sleep_mode_sleeping and time_since_activity >= sleep_timeout:
            sleep_mode_sleeping = True
            previous_track_name = ""
            log_message += f"Entered sleep mode after {time_since_activity:.1f} seconds of {play_status}. "
            ink_printer.show_image('/home/pi/music-screen-api/sonos-inky.png')
        elif sleep_mode_sleeping:
            log_message += "Sleep mode active"
        else:
            log_message += f"Inactive ({play_status}) for {time_since_activity:.1f} seconds"

        if last_status != play_status:
            last_activity_time = current_time  # Reset timer when status changes
            last_status = play_status

    logging.info(log_message)

# Main loop
def main():
    global sonos_room

    if len(sys.argv) == 1:
        sonos_room = input("Enter a Sonos room name >>> ")
    else:
        sonos_room = str(sys.argv[1])
    logging.info(f"Monitoring Sonos room: {sonos_room}")
    
    if sonos_settings.pi_zero:
        logging.info("Pausing for 60 seconds on startup to let pi zero catch up")
        time.sleep(60)

    use_webhook = getattr(sonos_settings, 'use_webhook', False)

    # Initial check on startup
    update_display(source="initial")

    if use_webhook:
        start_webhook_server()
        logging.info("Webhook mode active. Waiting for updates.")
        while True:
            time.sleep(1)  # Check every second for sleep mode in webhook mode
            update_display(source="sleep check")
    else:
        logging.info("Polling mode active. Checking for updates regularly.")
        while True:
            time.sleep(polling_frequency)
            update_display(source="polling")

if __name__ == "__main__":
    main()