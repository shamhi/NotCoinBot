import json
from os.path import isfile

if isfile(path='settings.json'):
    try:
        with open('settings.json', 'r') as file:
            config_data = json.load(file)
    except:
        config_data = {}
else:
    config_data = {}

API_ID: int = config_data.get('API_ID')
API_HASH: str = config_data.get('API_HASH')
MIN_CLICKS_COUNT: int = 1
AUTO_BUY_ENERGY_BOOST: bool = False
AUTO_BUY_SPEED_BOOST: bool = False
AUTO_BUY_CLICK_BOOST: bool = False
USE_PROXY_FROM_FILE: bool = False
SLEEP_BETWEEN_CLICK: list[int] = [10, 15]
SLEEP_BEFORE_BUY_MERGE: list[int] = [10, 15]
SLEEP_BEFORE_ACTIVATE_FREE_BUFFS: list[int] = [10, 15]
SLEEP_BEFORE_ACTIVATE_TURBO: list[int] = [10, 15]
SLEEP_AFTER_FORBIDDEN_STATUS: int = 5
