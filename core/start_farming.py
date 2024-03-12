import asyncio
import ssl
from base64 import b64decode
from math import floor
from random import randint
from time import time
from urllib.parse import unquote

import aiohttp
from aiohttp_proxy import ProxyConnector
from loguru import logger
from pyrogram import Client
from pyrogram.raw import functions

from data import config
from database import actions as db_actions
from exceptions import InvalidSession, TurboExpired, BadRequestStatus, ForbiddenStatus
from utils import eval_js, scripts
from .headers import headers, option_headers


class TLSv1_3_BYPASS:
    CIPHERS = "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA:AES256-SHA:DES-CBC3-SHA"

    @staticmethod
    def create_ssl_context():
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.set_ciphers(TLSv1_3_BYPASS.CIPHERS)
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        return ssl_context


class Farming:
    def __init__(self,
                 session_name: str,
                 client: Client):
        self.session_name: str = session_name
        self.client: Client = client

    async def get_access_token(self,
                               client: aiohttp.ClientSession,
                               tg_web_data: str) -> str:
        r: None = None

        while True:
            try:
                r: aiohttp.ClientResponse = await client.post(url='https://clicker-api.joincommunity.xyz/auth/'
                                                                  'webapp-session',
                                                              json={
                                                                  'webAppData': tg_web_data
                                                              })

                return (await r.json(content_type=None))['data']['accessToken']

            except Exception as error:
                if r:
                    status_code = r.status
                    logger.error(f'{self.session_name} | Неизвестная ошибка при получении Access Token: {error} | '
                                 f'Статус: {status_code} | Ответ: {await r.text()}')

                else:
                    logger.error(f'{self.session_name} | Неизвестная ошибка при получении Access Token: {error}')

                await asyncio.sleep(delay=2)

    async def get_tg_web_data(self,
                              session_proxy: str | None) -> str | None:
        while True:
            try:
                if session_proxy:
                    proxy_dict = scripts.get_proxy_dict(session_proxy=session_proxy)
                else:
                    proxy_dict: None = None

                self.client.proxy = proxy_dict

                with_tg = True

                if not self.client.is_connected:
                    with_tg = False
                    await self.client.connect()

                web_view = await self.client.invoke(
                    functions.messages.RequestWebView(
                        peer=await self.client.resolve_peer('notcoin_bot'),
                        bot=await self.client.resolve_peer('notcoin_bot'),
                        platform='android',
                        from_bot_menu=False,
                        url='https://clicker.joincommunity.xyz/clicker'
                    )
                )

                if with_tg is False:
                    await self.client.disconnect()

                auth_url = web_view.url


                tg_web_data: str = unquote(string=unquote(
                    string=auth_url.split(sep='tgWebAppData=',
                                          maxsplit=1)[1].split(sep='&tgWebAppVersion',
                                                               maxsplit=1)[0]
                ))

                return tg_web_data

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f'{self.session_name} | Неизвестная ошибка при авторизации: {error}')
                await asyncio.sleep(delay=2)

    async def get_profile_data(self,
                               client: aiohttp.ClientSession) -> dict:
        while True:
            try:
                r: aiohttp.ClientResponse = await client.get(
                    url='https://clicker-api.joincommunity.xyz/clicker/profile',
                    verify_ssl=False)

                status_code = r.status
                try:
                    await r.json(content_type=None)
                except:
                    logger.error(f'{self.session_name} | Неизвестный ответ при получении данных профиля | '
                                 f'Статус: {status_code} | Ответ: {await r.text()}')
                    await asyncio.sleep(delay=2)
                    continue

                return await r.json(content_type=None)

            except Exception as error:
                logger.error(f'{self.session_name} | Неизвестная ошибка при получении данных профиля: {error}')
                await asyncio.sleep(delay=2)

    async def send_clicks(self,
                          client: aiohttp.ClientSession,
                          opt_client: aiohttp.ClientSession,
                          clicks_count: int,
                          tg_web_data: str,
                          balance: int,
                          total_coins: str | int,
                          click_hash: str | None = None,
                          turbo: bool | None = None
                          ) -> tuple[int | str, int | str | None, int | None, str | None, bool | None]:
        while True:
            try:
                json_data: dict = {
                    'count': clicks_count,
                    'hash': -1,
                    'webAppData': tg_web_data
                }

                if click_hash:
                    json_data['hash']: str = click_hash

                if turbo:
                    json_data['turbo']: bool = True

                await opt_client.options(
                    url='https://clicker-api.joincommunity.xyz/clicker/core/click',
                    json=json_data,
                    timeout=10)

                r: aiohttp.ClientResponse = await client.post(
                    url='https://clicker-api.joincommunity.xyz/clicker/core/click',
                    json=json_data,
                    timeout=10,
                    verify_ssl=False)

                status_code = r.status
                if not str(status_code).startswith('2'):
                    return status_code, None, None, None, None

                response_json: dict = await r.json(content_type=None)

                if response_json.get('data') \
                        and isinstance(response_json['data'], dict) \
                        and response_json['data'].get('message', '') == 'Turbo mode is expired':
                    raise TurboExpired()

                if response_json.get('data') \
                        and isinstance(response_json['data'], dict) \
                        and response_json['data'].get('message', '') == 'Try later':
                    await asyncio.sleep(delay=1)
                    continue

                if response_json.get('ok'):
                    available_coins = response_json.get('data', [])[0].get('availableCoins')
                    logger.success(f'{self.session_name} | Успешно сделал Click | Balance: '
                                   f'{balance + clicks_count} (+{clicks_count}) | Total Coins: {total_coins}')

                    next_hash: str | None = eval_js(
                        function=b64decode(s=(await r.json())['data'][0]['hash'][0]).decode())

                    return (status_code, balance + clicks_count, available_coins, next_hash,
                            (await r.json())['data'][0]['turboTimes'] > 0)

                logger.error(f'{self.session_name} | Не удалось сделать Click, ответ: {await r.text()}')
                return status_code, None, None, None, None

            except Exception as error:
                logger.error(f'{self.session_name} | Неизвестная ошибка при попытке сделать Click: {error}')
                await asyncio.sleep(delay=2)

    async def get_merged_list(self,
                              client: aiohttp.ClientSession) -> dict | None:
        r: None = None

        try:
            r: aiohttp.ClientResponse = await client.get(
                url='https://clicker-api.joincommunity.xyz/clicker/store/merged')

            if (await r.json(content_type=None)).get('ok'):
                return await r.json(content_type=None)

            logger.error(f'{self.session_name} | Не удалось получить список товаров, ответ: {await r.text()}')

            return

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | Неизвестная ошибка при получении списка товаров: {error}, '
                             f'ответ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | Неизвестная ошибка при получении списка товаров: {error}')

            await asyncio.sleep(delay=2)

    async def buy_item(self,
                       client: aiohttp.ClientSession,
                       item_id: int | str) -> bool:
        r: None = None

        try:
            r: aiohttp.ClientResponse = await client.post(url=f'https://clicker-api.joincommunity.xyz/clicker/store/'
                                                              f'buy/{item_id}',
                                                          headers={
                                                              'accept-language': 'ru-RU,ru;q=0.9',
                                                          },
                                                          json=False)

            if (await r.json(content_type=None)).get('ok'):
                return True

            logger.error(f'{self.session_name} | Неизвестный ответ при покупке в магазине: {await r.text()}')

            return False

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | Неизвестная ошибка при покупке в магазине: {error}, '
                             f'ответ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | Неизвестная ошибка при покупке в магазине: {error}')

            await asyncio.sleep(delay=2)
            return False

    async def activate_turbo(self,
                             client: aiohttp.ClientSession) -> int | None:
        r: None = None

        try:
            r: aiohttp.ClientResponse = await client.post(url=f'https://clicker-api.joincommunity.xyz/clicker/core/'
                                                              'active-turbo',
                                                          headers={
                                                              'accept-language': 'ru-RU,ru;q=0.9',
                                                          },
                                                          json=False)

            return (await r.json(content_type=None))['data'][0].get('multiple', 1)

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | Неизвестная ошибка при активации Turbo: {error}, '
                             f'ответ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | Неизвестная ошибка при активации Turbo: {error}')

            await asyncio.sleep(delay=2)
            return

    async def activate_task(self,
                            client: aiohttp.ClientSession,
                            task_id: int | str) -> bool | None:
        r: None = None

        try:
            r: aiohttp.ClientResponse = await client.post(url=f'https://clicker-api.joincommunity.xyz/clicker/task/'
                                                              f'{task_id}',
                                                          headers={
                                                              'accept-language': 'ru-RU,ru;q=0.9',
                                                          },
                                                          json=False)

            if (await r.json(content_type=None)).get('ok'):
                return True

            logger.error(f'{self.session_name} | Неизвестный ответ при активации Task {task_id}: {await r.text()}')

            return False

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | Неизвестная ошибка при активации Task {task_id}: {error}, '
                             f'ответ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | Неизвестная ошибка при активации Task {task_id}: {error}')

            await asyncio.sleep(delay=2)
            return False

    async def get_free_buffs_data(self,
                                  client: aiohttp.ClientSession) -> tuple[bool, bool]:
        r: None = None
        max_turbo_times: int = 3
        max_full_energy_times: int = 3

        turbo_times_count: int = 0
        full_energy_times_count: int = 0

        try:
            r: aiohttp.ClientResponse = await client.get(url=f'https://clicker-api.joincommunity.xyz/clicker/task/'
                                                             'combine-completed')

            for current_buff in (await r.json(content_type=None))['data']:
                match current_buff['taskId']:
                    case 3:
                        max_turbo_times: int = current_buff['task']['max']

                        if current_buff['task']['status'] == 'active':
                            turbo_times_count += 1

                    case 2:
                        max_full_energy_times: int = current_buff['task']['max']

                        if current_buff['task']['status'] == 'active':
                            full_energy_times_count += 1

            return max_turbo_times > turbo_times_count, max_full_energy_times > full_energy_times_count

        except Exception as error:
            if r:
                logger.error(f'{self.session_name} | Неизвестная ошибка при получении статуса бесплатных баффов: '
                             f'{error}, ответ: {await r.text()}')

            else:
                logger.error(f'{self.session_name} | Неизвестная ошибка при получении статуса бесплатных баффов: '
                             f'{error}')

            await asyncio.sleep(delay=2)
            return False, False

    @staticmethod
    async def close_connectors(*connectors: aiohttp.TCPConnector):
        for connector in connectors:
            try:
                if connector:
                    await connector.close() if not connector.closed else ...
            except:
                ...

    async def run(self,
                  proxy: str | None = None):
        session_proxy: str = await db_actions.get_session_proxy_by_name(session_name=self.session_name)

        if not session_proxy and config.USE_PROXY_FROM_FILE:
            session_proxy: str = proxy

        access_token_created_time: float = 0
        tg_web_data: str | None = None
        click_hash: str | None = None
        active_turbo: bool = False
        turbo_multiplier: int = 1

        while True:
            ssl_context = TLSv1_3_BYPASS.create_ssl_context()

            ssl_conn = aiohttp.TCPConnector(ssl=ssl_context)
            proxy_conn = ProxyConnector.from_url(url=session_proxy) if session_proxy else None

            client = aiohttp.ClientSession(
                connector_owner=proxy_conn,
                connector=ssl_conn,
                headers=headers)

            opt_client = aiohttp.ClientSession(
                connector=ssl_conn,
                connector_owner=proxy_conn,
                headers=option_headers)

            try:
                while True:
                    try:
                        if time() - access_token_created_time >= (config.SLEEP_TO_UPDATE_USER_DATA * 60):
                            tg_web_data: str = await self.get_tg_web_data(session_proxy=session_proxy)

                            access_token: str = await self.get_access_token(client=client,
                                                                            tg_web_data=tg_web_data)
                            client.headers['Authorization']: str = f'Bearer {access_token}'
                            opt_client.headers['Authorization']: str = f'Bearer {access_token}'
                            headers['Authorization']: str = f'Bearer {access_token}'
                            option_headers['Authorization']: str = f'Bearer {access_token}'

                            access_token_created_time: float = time()

                        profile_data: dict = await self.get_profile_data(client=client)

                        if not active_turbo:
                            if config.MIN_CLICKS_COUNT > floor(profile_data['data'][0]['availableCoins'] \
                                                               / profile_data['data'][0]['multipleClicks']):
                                logger.info(f'{self.session_name} | Недостаточно монет для клика')
                                continue

                        if floor(profile_data['data'][0]['availableCoins'] \
                                 / profile_data['data'][0]['multipleClicks']) < 160:
                            max_clicks_count: int = floor(profile_data['data'][0]['availableCoins'] \
                                                          / profile_data['data'][0]['multipleClicks'])

                        else:
                            max_clicks_count: int = 160

                        clicks_count: int = randint(a=config.MIN_CLICKS_COUNT,
                                                    b=max_clicks_count) \
                                            * profile_data['data'][0]['multipleClicks'] * turbo_multiplier

                        try:
                            status_code, new_balance, available_coins, click_hash, have_turbo = \
                                await self.send_clicks(client=client,
                                                       opt_client=opt_client,
                                                       clicks_count=int(clicks_count),
                                                       tg_web_data=tg_web_data,
                                                       balance=int(profile_data['data'][0]['balanceCoins']),
                                                       total_coins=profile_data['data'][0]['totalCoins'],
                                                       click_hash=click_hash,
                                                       turbo=active_turbo)

                            if status_code == 400:
                                logger.warning(f"{self.session_name} | Недействительные данные: {status_code}")
                                await asyncio.sleep(delay=25)

                                await self.close_connectors(client, opt_client, ssl_conn, proxy_conn)
                                access_token_created_time = 0

                                raise BadRequestStatus()

                            if status_code == 403:
                                logger.warning(f"{self.session_name} | Доступ к API запрещен: {status_code}")
                                logger.info(f"{self.session_name} | Сплю {config.SLEEP_AFTER_FORBIDDEN_STATUS} сек")
                                await asyncio.sleep(delay=config.SLEEP_AFTER_FORBIDDEN_STATUS)

                                await self.close_connectors(client, opt_client, ssl_conn, proxy_conn)
                                access_token_created_time = 0

                                raise ForbiddenStatus()

                            if not str(status_code).startswith('2'):
                                logger.error(f"{self.session_name} | Неизвестный статус ответа: {status_code}")
                                await asyncio.sleep(delay=15)

                                continue

                        except TurboExpired:
                            active_turbo: bool = False
                            turbo_multiplier: int = 1

                            continue

                        if have_turbo:
                            random_sleep_time: int = randint(a=config.SLEEP_BEFORE_ACTIVATE_TURBO[0],
                                                             b=config.SLEEP_BEFORE_ACTIVATE_TURBO[1])

                            logger.info(f'{self.session_name} | Сплю {random_sleep_time} перед активацией '
                                        f'Turbo')

                            await asyncio.sleep(delay=random_sleep_time)

                            turbo_multiplier: int | None = await self.activate_turbo(client=client)

                            if turbo_multiplier:
                                logger.success(f'{self.session_name} | Успешно активировал Turbo: '
                                               f'x{turbo_multiplier}')
                                active_turbo: bool = True
                                continue

                            else:
                                turbo_multiplier: int = 1

                        if new_balance:
                            merged_data: dict | None = await self.get_merged_list(client=client)

                            if merged_data:
                                for current_merge in merged_data['data']:
                                    match current_merge['id']:
                                        case 1:
                                            if not config.AUTO_BUY_ENERGY_BOOST:
                                                continue

                                            energy_price: int | None = current_merge['price']

                                            if new_balance >= energy_price \
                                                    and current_merge['max'] > current_merge['count']:
                                                sleep_before_buy_merge: int = randint(
                                                    a=config.SLEEP_BEFORE_BUY_MERGE[0],
                                                    b=config.SLEEP_BEFORE_BUY_MERGE[1]
                                                )
                                                logger.info(f'{self.session_name} | Сплю {sleep_before_buy_merge} '
                                                            f'сек. перед покупкой Energy Boost')

                                                await asyncio.sleep(delay=sleep_before_buy_merge)

                                                if await self.buy_item(client=client,
                                                                       item_id=1):
                                                    logger.success(f'{self.session_name} | Успешно купил Energy '
                                                                   'Boost')
                                                    continue

                                        case 2:
                                            if not config.AUTO_BUY_SPEED_BOOST:
                                                continue

                                            speed_price: int | None = current_merge['price']

                                            if new_balance >= speed_price \
                                                    and current_merge['max'] > current_merge['count']:
                                                sleep_before_buy_merge: int = randint(
                                                    a=config.SLEEP_BEFORE_BUY_MERGE[0],
                                                    b=config.SLEEP_BEFORE_BUY_MERGE[1]
                                                )
                                                logger.info(f'{self.session_name} | Сплю {sleep_before_buy_merge} '
                                                            'сек. перед покупкой Speed Boost')

                                                await asyncio.sleep(delay=sleep_before_buy_merge)

                                                if await self.buy_item(client=client,
                                                                       item_id=2):
                                                    logger.success(
                                                        f'{self.session_name} | Успешно купил Speed Boost')
                                                    continue

                                        case 3:
                                            if not config.AUTO_BUY_CLICK_BOOST:
                                                continue

                                            click_price: int | None = current_merge['price']

                                            if new_balance >= click_price \
                                                    and current_merge['max'] > current_merge['count']:
                                                sleep_before_buy_merge: int = randint(
                                                    a=config.SLEEP_BEFORE_BUY_MERGE[0],
                                                    b=config.SLEEP_BEFORE_BUY_MERGE[1])
                                                logger.info(
                                                    f'{self.session_name} | Сплю {sleep_before_buy_merge} сек. '
                                                    f'перед покупкой Speed Boost')

                                                await asyncio.sleep(delay=sleep_before_buy_merge)

                                                if await self.buy_item(client=client,
                                                                       item_id=3):
                                                    logger.success(
                                                        f'{self.session_name} | Успешно купил Click Boost')
                                                    continue

                                        case 4:
                                            ...

                        free_daily_turbo, free_daily_full_energy = await self.get_free_buffs_data(client=client)

                        if config.SLEEP_BY_MIN_COINS:
                            if available_coins:
                                min_available_coins = config.MIN_AVAILABLE_COINS

                                if available_coins < min_available_coins:
                                    if free_daily_full_energy:
                                        random_sleep_time: int = randint(
                                            a=config.SLEEP_BEFORE_ACTIVATE_FREE_BUFFS[0],
                                            b=config.SLEEP_BEFORE_ACTIVATE_FREE_BUFFS[1])

                                        logger.info(
                                            f'{self.session_name} | Сплю {random_sleep_time} перед активацией '
                                            f'ежедневного Full Energy')

                                        await asyncio.sleep(delay=random_sleep_time)

                                        if await self.activate_task(client=client,
                                                                    task_id=2):
                                            logger.success(
                                                f'{self.session_name} | Успешно запросил ежедневный Full Energy')

                                            continue

                                    sleep_time_to_min_coins = config.SLEEP_BY_MIN_COINS_TIME

                                    logger.info(
                                        f"{self.session_name} | Достигнут минимальный баланс: {available_coins}")
                                    logger.info(f"{self.session_name} | Сплю {sleep_time_to_min_coins} сек.")

                                    await asyncio.sleep(delay=sleep_time_to_min_coins)

                                    logger.info(f"{self.session_name} | Продолжаю кликать!")

                                    continue

                        if free_daily_turbo:
                            random_sleep_time: int = randint(a=config.SLEEP_BEFORE_ACTIVATE_FREE_BUFFS[0],
                                                             b=config.SLEEP_BEFORE_ACTIVATE_FREE_BUFFS[1])

                            logger.info(f'{self.session_name} | Сплю {random_sleep_time} перед запросом '
                                        f'ежедневного Turbo')

                            await asyncio.sleep(delay=random_sleep_time)

                            if await self.activate_task(client=client,
                                                        task_id=3):
                                logger.success(f'{self.session_name} | Успешно запросил ежедневное Turbo')

                                random_sleep_time: int = randint(a=config.SLEEP_BEFORE_ACTIVATE_TURBO[0],
                                                                 b=config.SLEEP_BEFORE_ACTIVATE_TURBO[1])

                                logger.info(f'{self.session_name} | Сплю {random_sleep_time} перед активацией '
                                            f'Turbo')

                                await asyncio.sleep(delay=random_sleep_time)

                                turbo_multiplier: int | None = await self.activate_turbo(client=client)

                                if turbo_multiplier:
                                    logger.success(f'{self.session_name} | Успешно активировал Turbo: '
                                                   f'x{turbo_multiplier}')
                                    active_turbo: bool = True
                                    continue

                                else:
                                    turbo_multiplier: int = 1

                    except InvalidSession as error:
                        raise error

                    except Exception as error:
                        logger.error(f'{self.session_name} | Неизвестная ошибка: {error}')

                        random_sleep_time: int = randint(a=config.SLEEP_BETWEEN_CLICK[0],
                                                         b=config.SLEEP_BETWEEN_CLICK[1])

                        logger.info(f'{self.session_name} | Сплю {random_sleep_time} сек.')
                        await asyncio.sleep(delay=random_sleep_time)

                    else:
                        random_sleep_time: int = randint(a=config.SLEEP_BETWEEN_CLICK[0],
                                                         b=config.SLEEP_BETWEEN_CLICK[1])

                        logger.info(f'{self.session_name} | Сплю {random_sleep_time} сек.')
                        await asyncio.sleep(delay=random_sleep_time)

            except InvalidSession as error:
                await self.close_connectors(client, opt_client, ssl_conn, proxy_conn)
                raise error

            except Exception as error:
                await self.close_connectors(client, opt_client, ssl_conn, proxy_conn)

                logger.error(f'{self.session_name} | Неизвестная ошибка: {error}')
                await asyncio.sleep(delay=2)


async def start_farming(session_name: str,
                        client: Client,
                        proxy: str | None = None, ) -> None:
    try:
        await Farming(session_name=session_name, client=client).run(proxy=proxy)
    except (BadRequestStatus, ForbiddenStatus):
        await start_farming(session_name=session_name, client=client, proxy=proxy)
    except InvalidSession:
        logger.error(f'{session_name} | Invalid Session')
