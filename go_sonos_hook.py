import time
import sonos_user_data_legacy as sonos_user_data
import sys
import ink_printer
import sonos_settings
import demaster
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration
SLEEP_TIMEOUT = 5  # Sleep after 5 seconds of inactivity
POLLING_INTERVAL = 4  # 4 seconds between polls if not using webhook

# Global variables
previous_track = ""
sleep_mode_active = False
last_activity_time = time.time()
sonos_room = ""

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        update_display("webhook")

    def log_message(self, format, *args):
        return

def start_webhook_server(port=8080):
    server = HTTPServer(('', port), WebhookHandler)
    logging.info(f"Webhook server started on port {port}")
    threading.Thread(target=server.serve_forever, daemon=True).start()

def update_display(source):
    global previous_track, sleep_mode_active, last_activity_time

    track, artist, album, _, status = sonos_user_data.current(sonos_room)
    current_time = time.time()

    if status == "PLAYING":
        last_activity_time = current_time
        sleep_mode_active = False
        if track != previous_track:
            previous_track = track
            if sonos_settings.demaster:
                track = demaster.strip_name(track)
            ink_printer.print_text_to_ink(track, artist, album)
            logging.info(f"{source.capitalize()}: New track: {track} - {artist}")
    elif not sleep_mode_active and (current_time - last_activity_time) >= SLEEP_TIMEOUT:
        sleep_mode_active = True
        ink_printer.show_image('/home/pi/music-screen-api/sonos-inky.png')
        logging.info(f"{source.capitalize()}: Entered sleep mode")
    
    if status != "PLAYING":
        logging.info(f"{source.capitalize()}: {status}")

def main():
    global sonos_room

    sonos_room = sys.argv[1] if len(sys.argv) > 1 else input("Enter a Sonos room name >>> ")
    logging.info(f"Monitoring Sonos room: {sonos_room}")

    update_display("initial")

    if getattr(sonos_settings, 'use_webhook', False):
        start_webhook_server()
        while True:
            time.sleep(3600)
    else:
        while True:
            time.sleep(POLLING_INTERVAL)
            update_display("polling")

if __name__ == "__main__":
    main()