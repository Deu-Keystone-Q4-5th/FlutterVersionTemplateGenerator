import configparser
import json
import os
import threading

config_folder = "config"
config_path = config_folder + "/config.json"


class Config:
    def __init__(self, **kwargs):
        self.comment1: str = "알라딘 API Secret Key 입니다."
        self.secret_key: str = ""
        self.comment2: str = "하루에 가능한 API 요청 수를 정합니다."
        self.request_per_day: int = 5000

        if (kwargs.get("secret_key")) :
            self.secret_key = kwargs.get("secret_key")
        if (kwargs.get("request_per_day")) :
            self.request_per_day = kwargs.get("request_per_day")



class ConfigManager:
    def __init__(self):
        if os.path.exists(config_folder):
            if not os.path.isdir(config_folder):
                os.remove(config_folder)
            elif os.path.exists(config_path) and os.path.isfile(config_path):
                try:
                    self.load_config()
                    return
                except json.JSONDecodeError:
                    print("Error With Loading Config. Skipping...")
        else:
            os.mkdir(config_folder)

        self.config = Config()
        self.save_config()

    def save_config(self) -> None:
        json_str = json.dumps(self.config.__dict__, ensure_ascii=False, indent=4)
        thread = threading.Thread(target=self.__write_json, args=(json_str,))
        thread.run()

    def __write_json(self, data: str) -> None:
        file_stream = open('config/config.json', 'w')
        file_stream.write(data)
        file_stream.close()

    def load_config(self):
        thread = threading.Thread(target=self.__read_json__())
        thread.run()
        return self.config

    def __read_json__(self):
        file_stream = open(config_path, "r")
        s = file_stream.read()
        obj = json.loads(s)
        self.config = Config(secret_key= obj["secret_key"], request_per_day= obj["request_per_day"])


configManager = ConfigManager()

