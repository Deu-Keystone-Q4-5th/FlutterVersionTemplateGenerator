import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
config_folder = os.path.join(base_dir, "GoldenBough", "config")
config_file = "config.json"
config_path = os.path.join(config_folder, config_file)


class Config:
    def __init__(self, **kwargs):
        self.comment1: str = "알라딘 API Secret Key 입니다."
        self.secret_key: str = ""
        self.comment2: str = "하루에 가능한 API 요청 수를 정합니다."
        self.request_per_day: int = 5000

        if kwargs.get("secret_key"):
            self.secret_key = kwargs.get("secret_key")
        if kwargs.get("request_per_day"):
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
        try:
            self.__write_json(json_str)
        except IOError as e:
            print(f"Error saving config: {e}")

    def __write_json(self, data: str) -> None:
        with open(config_path, 'w') as file_stream:
            file_stream.write(data)

    def load_config(self):
        try:
            self.__read_json()
        except IOError as e:
            print(f"Error loading config: {e}")

    def __read_json(self):
        with open(config_path, "r") as file_stream:
            obj = json.load(file_stream)
            self.config = Config(secret_key=obj["secret_key"], request_per_day=obj["request_per_day"])


configManager = ConfigManager()
