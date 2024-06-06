import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
config_folder = os.path.join(base_dir, "GoldenBough", "config")
config_file = "config.json"
config_path = os.path.join(config_folder, config_file)
user_data_path = os.path.join(config_folder, "user_data.json")


class Config:
    def __init__(self, **kwargs):
        self.comment1: str = "알라딘 API Secret Key 입니다."
        self.secret_key: str = ""
        self.comment3: str = "English APIs"
        self.eng_secret_key = ""
        self.comment2: str = "하루에 가능한 API 요청 수를 정합니다."
        self.request_per_day: int = 5000

        if kwargs.get("secret_key"):
            self.secret_key = kwargs.get("secret_key")
        if kwargs.get("request_per_day"):
            self.request_per_day = kwargs.get("request_per_day")

        if kwargs.get("eng_secret_key"):
            self.eng_secret_key = kwargs.get("eng_secret_key")


class UserData:
    def __init__(self, **kwargs):
        self.lang = "ko"

        if kwargs.get("lang"):
            self.lang = kwargs.get("lang")


class ConfigManager:
    def __init__(self):
        is_config_loaded = False
        is_user_data_loaded = False
        if os.path.exists(config_folder):
            if not os.path.isdir(config_folder):
                os.remove(config_folder)
                os.mkdir(config_folder)

            try:
                if os.path.exists(config_path) and os.path.isfile(config_path):
                    self.load_config()
                    is_config_loaded = True
                if os.path.exists(user_data_path) and os.path.isfile(user_data_path):
                    self.load_user_data()
                    is_user_data_loaded = True
                return
            except json.JSONDecodeError:
                print("Error With Loading Config. Skipping...")
        else:
            os.mkdir(config_folder)
        if not is_config_loaded:
            self.config = Config()
            self.save_config()
        if not is_user_data_loaded:
            self.user_data = UserData()
            self.save_user_data()

    def save_config(self) -> None:
        json_str = json.dumps(self.config.__dict__, ensure_ascii=False, indent=4)
        try:
            self.__write_json(json_str, config_path)
        except IOError as e:
            print(f"Error saving config: {e}")

    def save_user_data(self):
        json_str = json.dumps(self.user_data.__dict__, ensure_ascii=False, indent=4)
        try:
            self.__write_json(json_str, user_data_path)
        except IOError as e:
            print(f"Error saving user_data: {e}")

    def __write_json(self, data: str, path) -> None:
        with open(path, 'w') as file_stream:
            file_stream.write(data)

    def load_config(self):
        try:
            self.__read_json(config_path, True)
        except IOError as e:
            print(f"Error loading config: {e}")

    def load_user_data(self):
        try:
            self.__read_json(user_data_path, False)
        except IOError as e:
            print(f"Error loading user_data: {e}")

    def __read_json(self, path, is_config: bool):
        with open(path, "r") as file_stream:
            obj = json.load(file_stream)
            if is_config:
                self.config = Config(secret_key=obj["secret_key"], request_per_day=obj["request_per_day"],
                                     eng_secret_key=obj["eng_secret_key"])
            else:
                self.user_data = UserData(lang=obj["lang"])


configManager = ConfigManager()
