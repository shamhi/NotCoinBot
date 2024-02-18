from enum import Enum


class ClientType(str, Enum):
    Pyrogram = 'P'
    Telethon = 'T'
