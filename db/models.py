from datetime import datetime

from tortoise import Model, fields


class Session(Model):
    id = fields.IntField(pk=True)

    tg_id = fields.BigIntField()
    name = fields.TextField()

    class Meta:
        table = 'sessions'


class Statistic(Model):
    id = fields.IntField(pk=True)

    session = fields.ForeignKeyField(model_name='models.Session')

    start_balance = fields.BigIntField(default=0)
    end_balance = fields.BigIntField(default=0)

    start_datetime = fields.DatetimeField(default=datetime.now())
    end_datetime = fields.DatetimeField(default=datetime.now())

    class Meta:
        table = 'statistics'


class Request(Model):
    id = fields.IntField(pk=True)

    session = fields.ForeignKeyField(model_name='models.Session')

    status = fields.TextField()
    send_warning = fields.BooleanField(default=False)

    requested_at = fields.DatetimeField(default=datetime.now())

    class Meta:
        table = 'requests'
