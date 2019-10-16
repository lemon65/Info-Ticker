import logging


'''
Logging Level Values -- >
     ____________________________
    Level       |   Numeric value
    CRITICAL    |   50
    ERROR       |   40
    WARNING     |   30
    INFO        |   20
    DEBUG       |   10
    NOTSET      |   0
     ____________________________

Example Logging Commands -- > (Note the "logger." Call/Name will change based on what your logger object is called.)
    logger.critical('Example Text - 4')
    logger.error('Example Text - 3')
    logger.warning('Example Text - 2')
    logger.info('Example Text - 1')

More info - https://docs.python.org/2/library/logging.html

'''

def setup_logging(name, create_file=False, stream_to_console=False):
    ''' Function to create a basic logger and log to the /Logs folder
    If you need to create a new log file, just call this function with create_file=True


    RETURNS --> Obj
        This returns a logger object for later use
    '''
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.propagate = False
    formatter = logging.Formatter('%(asctime)s - %(name)s_%(levelno)s|%(funcName)s - %(message)s')
    logging_level = 'INFO'
    if stream_to_console:
        consoleHandler = logging.StreamHandler()
        logger.addHandler(consoleHandler)
    logger.setLevel(logging_level)
    if create_file:
        file_handler = logging.FileHandler('Logs/' + name + '_Logger' + '.log')  # if you want to, pass create_file=True to create its own file (Example Low level Logging ** )
    else:
        file_handler = logging.FileHandler('Logs/Basic_Logger' + '.log')  # Basic landing zone for logging **
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
