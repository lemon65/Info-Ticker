#!/usr/bin/python3
import os, sys, time, logging
import gather_info as gi
import create_logger as cl
import hw_interface as hwi


logger = logging.getLogger('IINFO')
console = logging.getLogger('CONSOLE')
global runtime_flag

def _init_loggers():
    ''' This creates all the logger objects for the evironment, and allows the
        libs to call the logger objects, at a later Time.

        logger_object = logging.getLogger('LOGGER_NAME')
        logger_object.info('Data to log...')

    Logger Names = 'IINFO', 'HWI', 'GAINFO', 'CONSOLE', 'RPLCD'

    RETURNS --> No Return value
    '''
    logger_names = [['IINFO', False], ['HWI', False],
                    ['GAINFO', True], ['CONSOLE', False],
                    ['RPLCD', True]]
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
    target_source = gi.get_source_index()
    logger.info('Index Source: %s >> %s' % (target_source, target_source + 1))
    print('Index Source: %s >> %s' % (target_source, target_source + 1))
    gi.set_source_index(target_source + 1)

def main():
    hardware_interface = hwi.HardWareInterface()
    hardware_interface.start_button_poller()
    logger.info('#'*30 + ' Starting the Info Ticker ' + "#"*30)
    #weather_data = gi.gather_weather()

    today_in_history = gi.gather_today_in_history()
    reddit_posts = gi.gather_top_reddit()
    #current_time = gi.gather_current_time()
    twitter = [['Twitter-Test-1', 'Twitter-Test-2', 'Twitter-Test-3']]
    stocks = [['Stocks-Test-1', 'Stocks-Test-2', 'Stocks-Test-3']]
    weather = [['Weather-Test-1', 'Weather-Test-2', 'Weather-Test-3']]
    clock = [['clock-Test-1', 'clock-Test-2', 'clock-Test-3']]
    data_points = [reddit_posts, twitter, stocks, today_in_history, weather, clock]
    while True:
        # TODO -- if current time is over repoll_interval in the config.... gather and update the data_points LIST
        try:
            current_source = gi.get_source_index()  # (0=Reddit, 1=Twitter, 2=Stocks, 3=TodayInHistory, 4=Weather, 5=Clock)
            hardware_interface.write_to_lcd_screen(data_points[current_source])
        except KeyboardInterrupt:
            console.info('Ending Script.....')
    hardware_interface.stop_button_poller()
    

if __name__ == "__main__":
    runtime_flag = True
    _init_loggers()
    gi.read_config()  # Read the config data so we have an init data point.
    sys.exit(main())
