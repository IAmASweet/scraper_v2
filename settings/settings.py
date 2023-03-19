import configparser
import logging

import yaml
from typing import Any
from yaml import CLoader as Loader

config = configparser.ConfigParser()
config.read('settings/config.ini')
logger = logging.getLogger("logger")
file_handler = logging.FileHandler('settings/py.log',
                                   'a',
                                   encoding=config['Default']['encoding'])
logger.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(file_handler)
LINK_YAML = "channels.yaml"


def get_config(section: str, key: str) -> str:
    value = config[section][key]
    return value


def set_config(section: str, key: str, value: str) -> None:
    config[section][key] = value


def read_yaml(file_path: str) -> Any:
    with open(file_path) as f:
        data = yaml.load(f, Loader=Loader)
        print(data)
        return data


def write_yaml(file_path: str, data: Any) -> None:
    with open(file_path, 'w') as file:
        yaml.dump(data, file)


def change_value_in_yaml(prev_value: Any,
                         new_value: Any,
                         key: str,
                         file_path: str) -> None:
    result: dict = read_yaml(file_path)
    data: list = result[key]
    for idx, item in enumerate(data):
        if item == prev_value:
            data[idx] = new_value
    write_yaml(file_path, {key: data})


if __name__ == "__main__":
    # 'https://t.me/nodejs_ru'
    change_value_in_yaml('https://t.me/nodejs_ru', "https://t.me/anothertestcanal", 'links', LINK_YAML)
    # read_yaml()'https://t.me/nodejs_ru'
    # write_yaml()

# Выгружаю чаты
