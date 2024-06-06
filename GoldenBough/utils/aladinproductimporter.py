from GoldenBough.utils import Config
from GoldenBough.utils.requestAPI import apiImporter


class AladinProductImporter (apiImporter):
    def __init__(self):
        self.ttb_key = Config.configManager.config.secret_key
        self.version = "20131101"
        self.opts = []