# This file is for use with the Pimoroni inky wHAT display
# it integrates with your local Sonos system to display what is currently playing

import asyncio
import logging
import os
import signal
import sys
import time

from aiohttp import ClientSession

import sonos_user_data_legacy as sonos_user_data  # the API which pulls the lastfm data
import ink_printer  # does the printing to ink
import sonos_settings
import demaster

# Assuming SonosWebhook is already implemented
from webhook_handler import SonosWebhook

_LOGGER = logging.getLogger(__name__)

# User variables
if sonos_settings.pi_zero:
    frequency = 1  # number of seconds between checks of the API
    sleep_mode_sheep_to_count = 20
else:
    frequency = 4
    sleep_mode_sheep_to_count = 10
sleep_mode_enabled = True
sleep_mode_frequency = 5
sleep_mode_output = "logo"  # can also be "blank"

# Set globals to nil at the start of the script
previous_track_name = ""
sleep_mode_sleeping = False
number_of_sheep_counted = 0

# Check if a command line argument has been passed to identify the user, if not ask
if len(sys.argv) == 1:
    # if no room name passed then ask the user to input a room name
    sonos_room = input("Enter a Sonos room name >>> ")
else:
    # if command line includes username then set it to that
    sonos_room = str(sys.argv[1])
    print(sonos_room)

if sonos_settings.pi_zero:
    print("Pausing for 60 seconds on startup to let pi zero catch up")
    time.sleep(60)

async def redraw(sonos_data):
    """Redraw the screen with current data."""
    global previous_track_name
    global sleep_mode_sleeping
    global number_of_sheep_counted

    current_track, current_artist, current_album, current_image, play_status = sonos_data

    # Check if anything is playing
    if play_status == "PLAYING":
        # Wake from sleep mode if we're in it
        sleep_mode_sleeping = False
        number_of_sheep_counted = 0

        # See if there is new data to display
        if current_track == previous_track_name:  # check if the track name is the same as what we displayed last time
            print("No change to data - not refreshing")
        else:
            print("New data found from API - refreshing screen")
            previous_track_name = current_track

            # Demaster the track name if set to do so
            if sonos_settings.demaster:
                current_track = demaster.strip_name(current_track)

            # Print to the ink
            ink_printer.print_text_to_ink(current_track, current_artist, current_album)
    else:
        # Nothing is playing right now
        if number_of_sheep_counted <= sleep_mode_sheep_to_count:
            # Not enough sleep counted yet to go to sleep - add one
            number_of_sheep_counted += 1
            print(f"Counting {number_of_sheep_counted} sheep")
        else:
            # If enough sheep have been counted then put into sleep mode
            if not sleep_mode_sleeping:
                # Set the screen depending on settings
                if sleep_mode_output == "logo":
                    ink_printer.show_image('/home/pi/music-screen-api/sonos-inky.png')
                else:
                    ink_printer.blank_screen()
                sleep_mode_sleeping = True
                previous_track_name = ""
                print("Nothing playing, sleep mode")

    if not sleep_mode_sleeping:
        await asyncio.sleep(frequency)
        print(f"Waiting {frequency} seconds")
    else:
        await asyncio.sleep(sleep_mode_frequency)
        print(f"Waiting {sleep_mode_frequency} seconds as in sleep mode")


async def get_sonos_data(session, room_name):
    """Get the current data from the Sonos system."""
    return sonos_user_data.current(room_name)


def setup_logging():
    """Set up logging facilities for the script."""
    log_level = getattr(sonos_settings, "log_level", logging.INFO)
    log_file = getattr(sonos_settings, "log_file", None)
    if log_file:
        log_path = os.path.expanduser(log_file)
    else:
        log_path = None

    fmt = "%(asctime)s %(levelname)7s - %(message)s"
    logging.basicConfig(format=fmt, level=log_level)

    # Suppress overly verbose logs from libraries that aren't helpful
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)

    if log_path is None:
        return

    log_path_exists = os.path.isfile(log_path)
    log_dir = os.path.dirname(log_path)

    if (log_path_exists and os.access(log_path, os.W_OK)) or (
        not log_path_exists and os.access(log_dir, os.W_OK)
    ):
        _LOGGER.info("Writing to log file: %s", log_path)
        logfile_handler = logging.FileHandler(log_path, mode="a")

        logfile_handler.setLevel(log_level)
        logfile_handler.setFormatter(logging.Formatter(fmt))

        logger = logging.getLogger("")
        logger.addHandler(logfile_handler)
    else:
        _LOGGER.error(
            "Cannot write to %s, check permissions and ensure directory exists", log_path)


async def main(loop):
    """Main process for script."""
    setup_logging()

    session = ClientSession()

    async def cleanup():
        """Cleanup tasks on shutdown."""
        _LOGGER.debug("Shutting down")
        await session.close()

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    for signame in ('SIGINT', 'SIGTERM', 'SIGQUIT'):
        loop.add_signal_handler(getattr(signal, signame), lambda: asyncio.ensure_future(cleanup()))

    async def webhook_callback():
        """Callback to trigger after webhook is processed."""
        sonos_data = await get_sonos_data(session, sonos_room)
        await redraw(sonos_data)

    webhook = SonosWebhook(webhook_callback)
    await webhook.listen()

    while True:
        sonos_data = await get_sonos_data(session, sonos_room)
        await redraw(sonos_data)
        await asyncio.sleep(frequency)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main(loop))
        loop.run_forever()
    finally:
        loop.close()
