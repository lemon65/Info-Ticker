#!/usr/bin/python3
import sys
import os
import time
import requests
import logging
import codecs
import feedparser
import datetime
from configparser import ConfigParser


logger = logging.getLogger('GAINFO')
console = logging.getLogger('CONSOLE')

class GatherInfo():
    def __init__(self):
        self.data_blob = {}
        self.read_config()
        self.build_data_blob()    

    def read_config(self):
        '''
        Goes out and reads the config files every few mins, so it can update in real
        time. Pulling from different new places and users.

        Updates a Global Config Dict
        '''
        self.config_data = {}
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
                            data.append(self.norm_data(dat_step))
                elif ',' in value:
                    for dat_step in value.split(','):
                        if dat_step and dat_step[0] != '#':
                            data.append(self.norm_data(dat_step))
                else:
                    if value:
                        if value[0] != '#':
                            try:
                                data = eval(self.norm_data(value))  # Eval to the correct Type
                            except Exception:
                                data = ''.join(self.norm_data(value))  # Eval to string if the type can't be found
                section_dict[name] = data
            self.config_data[section_name] = section_dict
        return self.config_data

    def norm_data(self, text_blob, bad_list=None, replace_w=''):
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

    def get_source_index(self):
        '''
        returns the source index from the in memory config
        returns -- INT
        '''
        return int(self.config_data['BASIC']['source_index'])

    def set_source_index(self, target_index):
        '''
        can update the current source_index stored in config_data,
        this happens if there is a button push.
        '''
        # If you are over the max source start loop back.
        if target_index >= int(self.config_data['BASIC']['max_source_index']):
            target_index = 0
        logger.info('Setting source_index = %s' % target_index)
        logger.info('Setting source_index = %s' % target_index)
        self.config_data['BASIC']['source_index'] = str(target_index)

    def build_data_blob(self, target_key=None):
        """
        Calls all the gathering functions and builds a blob of data for display.

        Map - (0=Reddit, 1=Twitter, 2=Stocks, 3=TodayInHistory, 4=Weather)
        """
        # targets = {"reddit": self.gather_top_reddit,
        #            "twitter": self.gather_top_tweets,
        #            "stocks": self.gather_stocks,
        #            "today_in_history": self.gather_today_in_history,
        #            "weather": self.gather_weather}
        targets = {"today_in_history": self.gather_today_in_history,
                   "clock": self.gather_current_time}
        possible_keys = targets.keys()
        if not target_key:  # Update all data points in the blob
            for func_name, function in targets.items():
                self.data_blob[func_name] = function()
        else:  # Update only a single data point in the data blob (Ex: only Clock)
            if target_key not in possible_keys:
                console.error("given key is not in the targets dict, Try: %s" % possible_keys)
                return
            self.data_blob[target_key] = targets.get(target_key)()  # call the function of target_key()
        console.info('Done building data blob...')
        return self.data_blob

    def eval_source_state(self, current_source_index):
        """Evals an int into a key for the data blob

        Arguments:
            current_source_index {[INT]} -- Value to equate an INT to a String value(Key in a dict)
        """
        int_map = {0: "reddit",
                1: "twitter",
                2: "stocks",
                3: "today_in_history",
                4: "weather",
                5: "clock"}
        return int_map.get(current_source_index)

    def get_request(self, target_url, params=None, headers=None, auth=None, timeout=30, response_type='JSON'):
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
        logger.info(response.url)
        if response.status_code == 200:
            if response_type == 'JSON':
                return response.json()
            else:
                return response.text
        else:
            logger.error('Error: %s on Action GET, on URL: %s' % (response.status_code, target_url))
            logger.error('Response: %s' % response.text)
            return None

    def gather_top_reddit(self):
        '''
        Gets data from target subreddits and returns the titles of said posts.

        returns -- Nested List
        '''
        reddit_posts = []
        base_sub_reddit_link = self.config_data['REDDIT']['sub_reddit_link']
        sub_reddits = self.config_data['REDDIT']['target_subs']
        for sub in sub_reddits:
            target_sub_url = base_sub_reddit_link % sub
            logger.info('Getting Data on TargetSub: %s' % target_sub_url)
            feed = feedparser.parse(target_sub_url)
            if feed:
                feed_entries = feed.get('entries')
                for feed_dict in feed_entries:
                    post_data = []
                    service = 'Reddit-%s' % sub  # Creates a Site/Sub service name
                    source = feed_dict.get('author')
                    title = feed_dict.get('title')
                    post_data = service + source + title
                    reddit_posts.append(post_data)
        return reddit_posts

    def gather_top_tweets(self):
        '''
        Gets the Top Tweets and returns the person and content

        returns -- Nested List
        '''
        return ['Twitter']

    def gather_weather(self):
        '''
        Gets the weather, based on configured Zip codes and gathers the data points

        returns -- Nested List
        '''
        master_weather_list = []
        city_names = self.config_data['WEATHER']['city_names']
        base_weather_url = self.config_data['WEATHER']['base_weather_url']
        location_search_url = self.config_data['WEATHER']['location_search_url']
        weather_data_url = self.config_data['WEATHER']['weather_data_url']
        for cit_name in city_names:
            WOEID = None  # WOEID == "Where on Earth ID"
            search_url = base_weather_url + location_search_url % cit_name
            response = self.get_request(search_url)
            if response:
                WOEID = response[0].get('woeid')
                weather_data = self.get_request(base_weather_url + weather_data_url % WOEID)
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

    def gather_stocks(self):
        '''
        Gets stock data based on the configured values within the config file.

        returns -- Nested List
        '''
        return ['Stocks']

    def gather_today_in_history(self):
        '''
        Hits a http://history.muffinlabs.com/date and returns a number of events
        that happened on this date.

        returns -- Nested List
        '''
        master_data = []
        current_date = datetime.datetime.now()
        current_date = current_date.strftime("%m/%d")
        response = self.get_request('http://history.muffinlabs.com/date')
        if response:
            events = response.get('data')['Events']
            for event_dict in events:
                service = "THI - "
                event_string = event_dict.get('year') + ': ' + event_dict.get('text')
                master_data.append(service + event_string)
        return master_data

    def gather_current_time(self):
        '''
        uses datetime and returns the current time...

        returns -- a datetime object
        '''
        time_format = self.config_data['CLOCK']['time_format']
        current_time = datetime.datetime.now()
        current_time = current_time.strftime(time_format)
        return [current_time]
