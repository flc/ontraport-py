class Config(object):

    def __init__(self):
        self.app_id = None
        self.api_key = None
        self.api_base_url = 'https://api.ontraport.com/'


config = Config()


from .resources import *
