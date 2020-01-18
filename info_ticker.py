#!/usr/bin/python3
import os, sys, time, logging
import gather_info as gi
import create_logger as cl
import hw_interface as hwi


logger = logging.getLogger('IINFO')
global runtime_flag


def _init_loggers():
    ''' This creates all the logger objects for the evironment, and allows the
        libs to call the logger objects, at a later Time.

        logger_object = logging.getLogger('LOGGER_NAME')
        logger_object.info('Data to log...')

    Logger Names = 'IINFO', 'HWI', 'GAINFO', 'CONSOLE'

    RETURNS --> No Return value
    '''
    logger_names = [['IINFO', False], ['HWI', False],
                    ['GAINFO', True], ['CONSOLE', False]]
    if not os.path.isdir('./Logs'):
        os.mkdir('./Logs')
    for logger_data in logger_names:
        to_console = False
        if logger_data[0] == 'CONSOLE':
            to_console = True
        # Call the setup_logging function, to load all the loggers into MEM
        cl.setup_logging(logger_data[0],
                         create_file=logger_data[1],
                         stream_to_console=to_console)


def _abort():
    ''' Sets the runtime_flag == False, stopping the Main Loop '''
    global runtime_flag
    runtime_flag = False


def index_source():
    ''' This will index the config_data -- source_index,
    so we can pull different media
    '''
    gi.set_source_index(gi.get_source_index() + 1)


def main():
    to_call = 0
    logger.info('#'*30 + ' Starting the Info Ticker ' + "#"*30)

    if to_call == 1:
        weather_data = gi.gather_weather()
        for i in weather_data:
            print(i)
    if to_call == 2:
        today_in_history = gi.gather_today_in_history()
        for i in today_in_history:
            print(i)
    if to_call == 3:
        reddit_posts = gi.gather_top_reddit()
        for i in reddit_posts:
            print(i)
    if to_call == 4:
        while True:
            current_time = gi.gather_current_time()
            print(current_time)
            time.sleep(1)
    local_hwi = hwi.HWInterface()
    local_hwi.write_to_lcd_screen(['test1', 'test2', 'test3'])

if __name__ == "__main__":
    runtime_flag = True
    _init_loggers()
    gi.read_config()  # Read the config data so we have an init data point.
    sys.exit(main())
