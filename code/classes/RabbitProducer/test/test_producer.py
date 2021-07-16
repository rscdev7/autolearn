"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last_update        :  Fri 16/07/2021

Questo componente serve per testare RabbitProducer.
"""

from ..lib.rabbit_producer.RabbitProducer   import RabbitProducer
from aiormq.types                           import DeliveredMessage
import pytest

DATA            = {"request_id": 50, "value":870}
QUEUE_NAME      = "Test"
LOGIN_TOKEN     = "amqp://guest:guest@rabbitmq:5672/"


@pytest.mark.asyncio
async def test_rabbit_prod ():

    pr:RabbitProducer           = RabbitProducer(QUEUE_NAME,LOGIN_TOKEN)
    await pr.start()

    res:DeliveredMessage        = await pr.pubblish(DATA)

    await pr.stop()