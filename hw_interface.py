#!/usr/bin/python3
import logging, time, threading
from typing import NamedTuple
from RPLCD.i2c import CharLCD
from gpiozero import Button
import gather_info as gi
import info_ticker as intic

logger = logging.getLogger('HWI')

class HWInterface():
    def __init__(self):
        self.pi_lcd = CharLCD('PCF8574', 0x27)
        self.poll_source_button = False
        self.max_lcd_rows = int(gi.config_data['LCDDATA']['max_lcd_rows'])
        self.max_lcd_elements = int(gi.config_data['LCDDATA']['max_lcd_elements'])
        self.source_pin = gi.config_data['BASIC']['source_pin']

    def write_to_lcd_screen(self, info_to_write):
        '''
        function to write to the 20x4 LCD screen attached to the Raspberry Pi
        info_to_write = a nested list of data points
            Element[0] -- service = Where is it coming from (Reddit, Twitter, News)
            Element[1] -- source = Who is writing this? (Author, User, Etc.)
            Element[2] -- string_to_write = a sting of data to write (title, weather data, Etc.)
        '''
        class screen_data(NamedTuple):
            service: str
            source: str
            string_to_write: str

        screen_data = screen_data(info_to_write[0], info_to_write[1], info_to_write[2])
        for index, screen_item in enumerate(screen_data):
            length_of_data = len(screen_item)
            self.pi_lcd.cursor_pos(index, 0)  # move to the right row, and move to the Zero Position
            print('Put this on the LCD: %s' % screen_item)
            self.pi_lcd.write_string(screen_item)

    def start_button_poller(self):
        '''
        function to start a threaded process and poll for button pushes,
        starts self._source_button_poller()
        '''
        if not self.poll_source_button:
            logger.info('Starting the Source_Button polling Thread...')
            self.poll_source_button = True
            button_polling_thread = threading.Thread(name="button_polling_thread", target=self._source_button_poller)
            button_polling_thread.start()

    def stop_button_poller(self):
        '''
        function to stop a the threaded process that is polling for button pushes
        '''
        logger.info('Stopping the Source_Button polling Thread...')
        self.poll_source_button = False

    def _source_button_poller(self):
        ''' This is a function that is only to be called in a threaded fashion,
        and will run if the global flag is set to do so.
        '''
        source_button = Button(self.source_pin, pull_up=False)
        while self.poll_source_button:
            if source_button.is_pressed:
                intic.index_source()
            time.sleep(0.2)

    def scan_and_connect_wifi(self):
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
