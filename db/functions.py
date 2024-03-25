from datetime import datetime

from pyrogram import Client
from tortoise import Tortoise

from db.models import Session, Statistic, Request


async def on_startup_db():
    await Tortoise.init(
        db_url="sqlite://db/database.db",
        modules={'models': ['db.models']}
    )

    await Tortoise.generate_schemas()


async def register_session_to_db(session_name: str, tg_id: int) -> None:
    new_session = Session(tg_id=tg_id, name=session_name)
    await new_session.save()

async def check_sessions(session_names: list[str], tg_clients: list[Client]) -> None:
    exist_session_names = await Session.all().values_list('name', flat=True)

    if len(exist_session_names) < len(session_names):
        difference = set(session_names) - set(exist_session_names)

        tg_clients = [client for client in tg_clients if client.name in difference]

        new_sessions = []
        for client in tg_clients:
            async with client:
                session_name = client.name
                tg_id = client.me.id

            new_sessions.append(Session(tg_id=tg_id, name=session_name))

        await Session.bulk_create(new_sessions)


async def get_session_id(session_name: str = None, tg_id: int = None) -> int:
    if tg_id:
        session = await Session.get(tg_id=tg_id)
    elif session_name:
        session = await Session.get(name=session_name)

    return session.id

async def get_session_name(session_id: int):
    session = await Session.get(id=session_id)

    return session.name


async def start_statistics(session_id: int, start_balance: int) -> None:
    session = await Session.get(id=session_id)
    exist_stat = await Statistic.get_or_none(session=session)

    if exist_stat:
        exist_stat.start_balance = start_balance
        exist_stat.end_balance = start_balance
        exist_stat.start_datetime = datetime.now()
        exist_stat.end_datetime = datetime.now()

        await exist_stat.save()
    else:
        new_stat = Statistic(session=session, start_balance=start_balance)
        await new_stat.save()


async def update_end_balance(session_id: int, new_balance: int) -> None:
    session = await Session.get(id=session_id)
    stat = await Statistic.filter(session=session).first()

    stat.end_balance = new_balance
    stat.end_datetime = datetime.now()

    await stat.save()


async def add_request_status(session_id: int, status: str) -> None:
    session = await Session.get(id=session_id)
    request = Request(session=session, status=status)
    await request.save()


async def get_request_statuses(session_id: int) -> list[str]:
    session = await Session.get(id=session_id)
    statuses = await Request.filter(session=session, send_warning=False).values_list('status', flat=True)

    return statuses


async def after_send_warning(session_id: int) -> None:
    session = await Session.get(id=session_id)
    await Request.filter(session=session, status__not_like='2%').update(send_warning=True)


async def get_start_balance(session_id: int) -> int:
    session = await Session.get(id=session_id)
    stat = await Statistic.get(session=session)

    return stat.start_balance


async def get_end_balance(session_id: int) -> int:
    session = await Session.get(id=session_id)
    stat = await Statistic.get(session=session)

    return stat.end_balance


async def get_start_datetime(session_id: int) -> int:
    session = await Session.get(id=session_id)
    stat = await Statistic.get(session=session)

    return stat.start_datetime


async def get_end_datetime(session_id: int) -> int:
    session = await Session.get(id=session_id)
    stat = await Statistic.get(session=session)

    return stat.end_datetime
