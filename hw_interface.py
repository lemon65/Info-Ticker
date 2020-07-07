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
        # Variables for the LCD
        self.max_lcd_rows = int(gi.config_data['LCDDATA']['max_lcd_rows'])
        self.max_lcd_elements = int(gi.config_data['LCDDATA']['max_lcd_elements'])
        self.lcd_address = gi.config_data['LCDDATA']['lcd_address']
        self.lcd_expander = gi.config_data['LCDDATA']['lcd_expander']
        self.pi_lcd = CharLCD(i2c_expander=self.lcd_expander, address=self.lcd_address,
                              cols=self.max_lcd_elements, rows=self.max_lcd_rows, auto_linebreaks=True)
        # Variables for the Source Button
        self.poll_source_button_flag = False
        self.source_pin = gi.config_data['BASIC']['source_pin']

        # variables for the scrolling text
        self.scrolling_text_flag = False

    def write_to_lcd_screen(self, string_to_write: str, row_start: int, element_start: int, clear_lcd: bool = False):
        """ This function writes a string to the LCD, and will auto scroll the text if its over
        the self.max_lcd_elements varaible.    
        
        Arguments:
            string_to_write {str} -- [This is the string payload that you are writing to the LCD]
        
        Keyword Arguments:
            row_start {[int]} -- [Starting ROW for the write operation] (default: {0:int})
            element_start {[int]} -- [Starting ELEMENT for the write operation] (default: {0:int})
            clear_lcd {[bool]} -- [clear the LCD before writing your data] (default: {False:bool})
        """
        if clear_lcd:
            self.pi_lcd.clear()
        print("Cursor Move -- %s, %s" % (row_start, element_start))
        self.pi_lcd.cursor_pos = (row_start, element_start) # move to the (row, element) position
        self.pi_lcd.write_string(string_to_write)

    def display_data(self, data_list):
        """Takes a list of data from the info_ticker main and displays in on the LCD
        
        Arguments:
            data_list {list} -- list of strings to display onto the LCD -- len(4)
        """
        self.stop_text_scroll()
        for index, line in enumerate(data_list):
            print("Line: %s, Data: %s" % (index, line))
            line_length = len(line)
            if line_length < self.max_lcd_elements:
                self.write_to_lcd_screen(line, index, 0)
            else:
                self.start_text_scroll(line, index, 0)

    def start_text_scroll(self, long_string: str, row: int, element_start: int):
        logger.info('Starting the Scrolling_Text polling Thread, for Row: %s' % row)
        scroll_args = (long_string, row, element_start)
        scroll_polling_thread = threading.Thread(name="scrolling_text_thread_%s" % int(time.time()), target=self._scroll_text_on_lcd, args=scroll_args)
        scroll_polling_thread.start()

    def stop_text_scroll(self):
        """ Stops the scrolling of text, by stoping"""
        logger.info('Stopping the Scrolling_Text polling Thread...')
        self.scrolling_text_flag = False
        time.sleep(0.9)

    def _scroll_text_on_lcd(self, long_string: str, row_start: int, element_start: int):
        """ This scrolls text accross the LCD screen once, to be called
        Arguments:
            long_string {str} -- this is the long string that you want to display
        Keyword Arguments:
            row_start {int} -- row that you want to display your data on (default: {0})
            element_start {int} -- element that you want to display your data on (default: {0})
        """
        self.scrolling_text_flag = True
        while self.scrolling_text_flag:
            print("Scroll -- %s, %s" % (row_start, element_start))
            for idex in range(len(long_string) - self.max_lcd_elements + 1):
                print("Scroll2 -- %s, %s" % (row_start, element_start))
                if not self.scrolling_text_flag:  # Full Stop scrolling_text_flag == False
                    break
                string_to_write = long_string[idex:idex + self.max_lcd_elements]
                self.write_to_lcd_screen(string_to_write, row_start, element_start)
                time.sleep(0.5)
        print("Scrolling_Text Thread is stopped")
        self.pi_lcd.clear()
        return

    def start_button_poller(self):
        '''
        function to start a threaded process and poll for button pushes,
        starts self._source_button_poller()
        '''
        if not self.poll_source_button_flag:
            logger.info('Starting the Source_Button polling Thread...')
            self.poll_source_button_flag = True
            button_polling_thread = threading.Thread(name="button_polling_thread", target=self._source_button_poller)
            button_polling_thread.start()

    def stop_button_poller(self):
        '''
        function to stop a the threaded process that is polling for button pushes
        '''
        logger.info('Stopping the Source_Button polling Thread...')
        self.poll_source_button_flag = False

    def _source_button_poller(self):
        ''' This is a function that is only to be called in a threaded fashion,
        and will run if the global flag is set to do so.
        '''
        source_button = Button(self.source_pin, pull_up=False)
        while self.poll_source_button_flag:
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
