#!/usr/bin/python3
import logging, threading, time
import i2c_driver
import gather_info as gi
import info_ticker as intic
import RPi.GPIO as GPIO

logger = logging.getLogger('HWI')

class HardWareInterface():
    def __init__(self):
        self.poll_source_button = False
        self.mylcd = i2c_driver.RPLCD()

    def write_to_lcd_screen(self, info_to_write):
        '''
        function to write to the LCD screen attached to the Raspberry Pi
        info_to_write = a nested list of data points
            Element[0] -- service = Where is it coming from (Reddit, Twitter, News)
            Element[1] -- source = Who is writing this? (Author, User, Etc.)
            Element[2] -- string_to_write = a sting of data to write (title, weather data, Etc.)
        '''
        self.mylcd.lcd_clear()
        service = info_to_write[0] 
        source = info_to_write[1]
        string_to_write = info_to_write[2]
        self.mylcd.lcd_display_string_pos('## Info Ticker ##', 1, 3)
        for index, data_val in enumerate([service, source, string_to_write]):
            if len(data_val) <= i2c_driver.LCD_MAX_CHAR:
                self.mylcd.lcd_display_string(data_val, index + 2)
            else:
                self.mylcd.scroll_text(data_val, index + 2)

    def stop_lcd_scroll(self):
        """ Function to stop the scrolling function in the i2c_driver, and force a return... """
        i2c_driver.STOP_SCROLL = True
        time.sleep(0.3)
        i2c_driver.STOP_SCROLL = False
        
    def start_button_poller(self):
        '''
        function to start a threaded process and poll for button pushes,
        starts _source_button_poller()
        '''
        if not self.poll_source_button:
            logger.info('Starting the Source_Button polling Thread...')
            self.poll_source_button = True
            button_polling_thread = threading.Thread(name="button_polling_thread",
                                                    target=self._source_button_poller)
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
        GPIO.setmode(GPIO.BOARD)
        source_pin = int(gi.config_data['BASIC']['source_pin'])
        GPIO.setup(source_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        while self.poll_source_button:
            source_button_state = GPIO.input(source_pin)
            if source_button_state:
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
