#!/usr/bin/python3
import os
import sys
import time
import random
import logging
import gather_info as gi
import create_logger as cl
import hw_interface as hwi


logger = logging.getLogger('IINFO')
console = logging.getLogger('CONSOLE')
gi_obj = gi.GatherInfo()
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
    target_source = gi_obj.get_source_index()
    console.info('Index Source: %s >> %s' % (target_source, target_source + 1))
    gi_obj.set_source_index(target_source + 1)

def main():
    local_hwi = hwi.HWInterface()
    local_hwi.start_button_poller()
    rp_interval = gi_obj.config_data['BASIC']['repoll_interval']
    dp_interval = gi_obj.config_data['BASIC']['display_interval']
    display_blob = gi_obj.build_data_blob()
    repoll_timer = time.time() + rp_interval
    display_timer = None
    last_source_state = None
    logger.info('#'*30 + ' Starting the Info Ticker ' + "#"*30)

    while runtime_flag:
        current_source_button = gi_obj.get_source_index()
        if not last_source_state:
            last_source_state = current_source_button
        if last_source_state != current_source_button:
            display_timer = None
        content_key = gi_obj.eval_source_state(current_source_button)
        if repoll_timer < time.time() or content_key == "clock":
            display_blob = gi_obj.build_data_blob(target_key=content_key)
            repoll_timer = time.time() + rp_interval
        if not display_timer or display_timer < time.time():
            display_list = display_blob.get(content_key)
            if display_list:
                display_choice = random.choice(display_list)
            else:
                continue
            console.info(display_choice)
            local_hwi.display_data(display_choice)
            display_timer = time.time() + dp_interval
        last_source_state = current_source_button
        time.sleep(0.5)


if __name__ == "__main__":
    runtime_flag = True
    _init_loggers()
    sys.exit(main())
