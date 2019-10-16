#!/usr/bin/python3
import sys, os, time, requests, logging, codecs, feedparser, datetime
from configparser import ConfigParser


logger = logging.getLogger('GAINFO')

def read_config():
    '''
    Goes out and reads the config files every few mins, so it can update in real
    time. Pulling from different new places and users.

    Updates a Global Config Dict
    '''
    global config_data
    config_data = {}
    parser = ConfigParser()
    with codecs.open('./config_files/local_config.ini', "r", "utf8") as f:
        parser.readfp(f)
    for section_name in parser.sections():
        section_dict = {}
        for name, value in parser.items(section_name):
            data = []
            if '\n' in value:
                for dat_step in value.split('\n'):
                    if dat_step and dat_step[0] != '#':
                        data.append(norm_data(dat_step))
            elif ',' in value:
                for dat_step in value.split(','):
                    if dat_step and dat_step[0] != '#':
                        data.append(norm_data(dat_step))
            else:
                if value:
                    if value[0] != '#':
                        try:
                            data = eval(norm_data(value))  # Eval to the correct Type
                        except Exception:
                            data = ''.join(norm_data(value))  # Eval to string if the type can't be found
            section_dict[name] = data
        config_data[section_name] = section_dict

def norm_data(text_blob, bad_list=None, replace_w=''):
    '''
    Function to Normalize a Text blob, removing a list of bad params the user passes.

    RETURNS --> String
        Function returns a formatted string blob.
    '''
    buffer_string = ''
    if not bad_list:
        bad_list = ['\r', '\t', '\n']
    else:
        bad_list = set(list(bad_list + ['\r', '\t', '\n']))
    if text_blob:
        for bad_step in bad_list:
            buffer_string = text_blob.replace(bad_step, replace_w)
            text_blob = buffer_string
    return text_blob

def get_source_index():
    '''
    returns the source index from the in memory config
    returns -- INT
    '''
    return int(config_data['BASIC']['source_index'])

def set_source_index(target_index):
    '''
    can update the current source_index stored in config_data,
    this happens if there is a button push.
    '''
    global config_data
    # If you are over the max source start loop back.
    if target_index >= int(config_data['BASIC']['max_source_index']):
        target_index = 0
    print('Setting source_index = %s' % target_index)
    logger.info('Setting source_index = %s' % target_index)
    config_data['BASIC']['source_index'] = str(target_index)

def get_request(target_url, params=None, headers=None, auth=None, timeout=30, response_type='JSON'):
    '''
    Uses the requests lib to GET the URL and returns the response or logs the
    error code, and returns None.

    target_url = the url you are getting
    params = the parameters for the request
    headers = the headers passed to the request
    auth = HTTP auth tuple passed to requests
    timeout = max time we will wait for a response
    response_type == the returned response format -- ['JSON' OR 'TEXT']

    Returns --> JSON, or String (depends on target_url and response_type)
                - if there is a non-200 response it will error and return a None
    '''
    response = requests.get(target_url, params=params, headers=headers, auth=auth, timeout=timeout)
    print(response.url)
    if response.status_code == 200:
        if response_type == 'JSON':
            return response.json()
        else:
            return response.text
    else:
        logger.error('Error: %s on Action GET, on URL: %s' % (response.status_code, target_url))
        logger.error('Response: %s' % response.text)
        return None


def gather_top_reddit():
    '''
    Gets data from target subreddits and returns the titles of said posts.

    returns -- Nested List
    '''
    reddit_posts = []
    base_sub_reddit_link = config_data['REDDIT']['sub_reddit_link']
    sub_reddits = config_data['REDDIT']['target_subs']
    for sub in sub_reddits:
        target_sub_url = base_sub_reddit_link % sub
        print(target_sub_url)
        feed = feedparser.parse(target_sub_url)
        if feed:
            feed_entries = feed.get('entries')
            for feed_dict in feed_entries:
                post_data = []
                service = 'Reddit-%s' % sub  # Creates a Site/Sub service name
                source = feed_dict.get('author')
                title = feed_dict.get('title')
                post_data = [service, source, title]
                reddit_posts.append(post_data)
    return reddit_posts

def gather_top_tweets():
    '''
    Gets the Top Tweets and returns the person and content

    returns -- Nested List
    '''
    return [['']]

def gather_weather():
    '''
    Gets the weather, based on configured Zip codes and gathers the data points

    returns -- Nested List
    '''
    master_weather_list = []
    city_names = config_data['WEATHER']['city_names']
    base_weather_url = config_data['WEATHER']['base_weather_url']
    location_search_url = config_data['WEATHER']['location_search_url']
    weather_data_url = config_data['WEATHER']['weather_data_url']
    for cit_name in city_names:
        WOEID = None  # WOEID == "Where on Earth ID"
        search_url = base_weather_url + location_search_url % cit_name
        response = get_request(search_url)
        if response:
            WOEID = response[0].get('woeid')
            weather_data = get_request(base_weather_url + weather_data_url % WOEID)
            weather_data_buffer = []
            if weather_data:
                for event_key, event_value in weather_data.get("consolidated_weather")[0].items():
                    if isinstance(event_value, float):
                        event_value = round(event_value, 2)
                    print("key: %s, val:%s" % (event_key, event_value))
                    # TODO -- Step the data -- https://www.metaweather.com/api/location/44418/
            else:
                logger.error('Unable to Gather weather data API -- https://www.metaweather.com/api/')
        else:
            logger.error('Unable to Gather the WOEID == "Where on Earth ID" -- https://www.metaweather.com/api')
    return master_weather_list

def gather_stocks():
    '''
    Gets stock data based on the configured values within the config file.

    returns -- Nested List
    '''
    return [['']]

def gather_today_in_history():
    '''
    Hits a http://history.muffinlabs.com/date and returns a number of events
    that happened on this date.

    returns -- Nested List
    '''
    master_data = []
    current_date = datetime.datetime.now()
    current_date = current_date.strftime("%m/%d")
    response = get_request('http://history.muffinlabs.com/date')
    if response:
        events = response.get('data')['Events']
        for event_dict in events:
            service = 'Today in History, %s' % current_date
            source = ''
            event_string = event_dict.get('year') + ' - ' + event_dict.get('text')
            master_data.append([service, source, event_string])
    return master_data

def gather_current_time():
    '''
    uses datetime and returns the current time...

    returns -- a datetime object
    '''
    time_format = config_data['CLOCK']['time_format']
    current_time = datetime.datetime.now()
    current_time = current_time.strftime(time_format)
    return current_time
