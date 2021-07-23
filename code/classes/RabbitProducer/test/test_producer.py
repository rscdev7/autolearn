"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last_update        :  Fri 23/07/2021

Questo componente serve per testare RabbitProducer.
"""

from ..lib.rabbit_producer.RabbitProducer   import RabbitProducer
from aiormq.types                           import DeliveredMessage
import pytest
from typing                                 import Union


DATA                                            = {"request_id": 50, "value":870}
QUEUE_NAME                                      = "hello"
LOGIN_TOKEN                                     = "amqp://guest:guest@rabbitmq:5672/"


@pytest.mark.asyncio
async def test_rabbit_prod ():

    pr:RabbitProducer                           = RabbitProducer(QUEUE_NAME,LOGIN_TOKEN)

    res:Union[None , Exception]                 = await pr.start()
    assert issubclass(type(res) , Exception)    == False

    res:Union[DeliveredMessage, Exception]      = await pr.pubblish(DATA)
    assert issubclass(type(res) , Exception)    == False
    print ("\n[!] Messaggio Pubblicato Correttamente: {}".format(res))

    res:Union[None , Exception]                 = await pr.stop()
    assert issubclass(type(res) , Exception)    == False