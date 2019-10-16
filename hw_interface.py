#!/usr/bin/python3
import logging
import threading
import time

import gather_info as gi
import info_ticker as intic
# import RPi.GPIO as GPIO


global poll_source_button
poll_source_button = False

logger = logging.getLogger('HWI')


def write_to_lcd_screen(info_to_write):
    '''
    function to write to the 20x4 LCD screen attached to the Raspberry Pi
    info_to_write = a nested list of data points
        Element[0] -- service = Where is it coming from (Reddit, Twitter, News)
        Element[1] -- source = Who is writing this? (Author, User, Etc.)
        Element[2] -- string_to_write = a sting of data to write (title, weather data, Etc.)
    '''
    service = info_to_write[0]
    source = info_to_write[1]
    string_to_write = info_to_write[2]
    # TODO -- Take this data and Write it to the LCD
    # TODO -- if the string_to_write is longer than the display, walk it accross

    # Use the Lib -- RPLCD -- https://rplcd.readthedocs.io/en/stable/index.html

def start_button_poller():
    '''
    function to start a threaded process and poll for button pushes,
    starts _source_button_poller()
    '''
    global poll_source_button
    if not poll_source_button:
        logger.info('Starting the Source_Button polling Thread...')
        poll_source_button = True
        button_polling_thread = threading.Thread(name="button_polling_thread",
                                                 target=_source_button_poller)
        button_polling_thread.start()

def stop_button_poller():
    '''
    function to stop a the threaded process that is polling for button pushes
    '''
    global poll_source_button
    logger.info('Stopping the Source_Button polling Thread...')
    poll_source_button = False

def _source_button_poller():
    ''' This is a function that is only to be called in a threaded fashion,
    and will run if the global flag is set to do so.
    '''
    # GPIO.setmode(GPIO.BCM)
    source_pin = int(gi.config_data['BASIC']['source_pin'])
    # GPIO.setup(source_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    while poll_source_button:
        # source_button_state = GPIO.input(source_pin)
        source_button_state = True
        if not source_button_state:
            intic.index_source()
            time.sleep(0.2)

def scan_and_connect_wifi():
    '''
    scans for configured networks, and connects if possible. if it can connect
    to a network it will display a warning on the LCD and stop the script from
    attempting to continue.
    '''
    # TODO -- Connect to a network
    #      -- If you can't stop the script and display the error codes
    #      -- If you can, display the device's IP address so the user can
    #      connect if needed.
    return None
