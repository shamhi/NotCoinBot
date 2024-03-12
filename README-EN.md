[<img src="https://img.shields.io/badge/Telegram-%40Me-orange">](https://t.me/sho6ot)

![alt text](https://i.imgur.com/PDYwSJ9.png)

> 🇷🇺 README на русском доступен [здесь](README.md)

## Functionality  
+ _Multithreading_
+ _Proxy binding to session_
+ _Auto-purchase items when there is enough money (energy boost, speed boost, click boost)_
+ _Random sleep time between clicks_
+ _Random number of clicks per request_
+ _Support for tdata / pyrogram .session / telethon .session_

## [Settings](https://github.com/shamhi/NotCoinBot/blob/main/data/config.py)
+ **API_ID / API_HASH** - Platform data to run Telegram session (default - Android)
***
+ **MIN_CLICKS_COUNT** - Minimum number of clicks per request (without multiplier, e.g. with x9 multiplier: 1 click will be equal to 9 coins, not one)
***
+ **MIN_AVAILABLE_COINS** - Minimum number of coins to trigger delay (e.g. 200)
***
+ **AUTO_BUY_ENERGY_BOOST** - Automatic purchase of Energy Boost when balance is reached (True / False)
***
+ **AUTO_BUY_SPEED_BOOST** - Automatic purchase of Speed Boost when balance is reached (True / False)
***
+ **AUTO_BUY_CLICK_BOOST** - Automatic purchase of Click Boost when balance is reached (True / False)
***
+ **SLEEP_BY_MIN_COINS** - Use delay when minimum number of coins is reached (True / False)
***
+ **USE_PROXY_FROM_FILE** - Use Proxy from data/proxies.txt file for accounts without Proxy binding (True / False)
***
+ **SLEEP_BETWEEN_CLICK** - Range of delay between clicks (in seconds)
***
+ **SLEEP_BEFORE_BUY_MERGE** - Range of delay before purchasing boosts (in seconds)
***
+ **SLEEP_BEFORE_ACTIVATE_FREE_BUFFS** - Range of delay before activating daily boosts (in seconds)
***
+ **SLEEP_BEFORE_ACTIVATE_TURBO** - Range of delay before activating Turbo (in seconds)
***
+ **SLEEP_TO_UPDATE_USER_DATA** - Delay before updating user data (in minutes)
***
+ **SLEEP_BY_MIN_COINS_TIME** - Delay when minimum number of coins is reached (in seconds)

## Installation
You can download the [**Git Repo**](https://github.com/shamhi/NotCoinBot) by cloning on your system and installing its requirements:
```
~ >>> git clone https://github.com/shamhi/NotCoinBot.git 
~ >>> cd NotCoinBot

# Linux
~/NotCoinBot >>> python3 -m venv venv
~/NotCoinBot >>> source venv/bin/activate
~/NotCoinBot >>> pip3 install -r requirements.txt
~/NotCoinBot >>> python3 main.py

# Windows
~/NotCoinBot >>> python -m venv venv
~/NotCoinBot >>> .\venv\Scripts\activate
~/NotCoinBot >>> pip install -r .\requirements.txt
~/NotCoinBot >>> python .\main.py
```

You can also use arguments for quick launch, for example:
```
~/NotCoinBot >>> python3 main.py --action (1/2)
# Or
~/NotCoinBot >>> python3 main.py -a (1/2)

# 1 - Launches session registrar
# 2 - Launches with the ability to control via telegram
# 3 - Launches without the ability to control via telegram
```

## Docker
Manual installation:
```shell
# Creating an image
~/NotCoinBot >>> docker build -t notcoin_image .

# Run interactively
~/NotCoinBot >>> docker run --name notcoin_app -it notcoin_image

# Running in daemon mode
~/NotCoinBot >>> docker run --name notcoin_app -d notcoin_image
```

Installation via docker-compose:
```shell
# Run interactively
~/NotCoinBot >>> docker-compose up

# Running in daemon mode
~/NotCoinBot >>> docker-compose up -d
```
