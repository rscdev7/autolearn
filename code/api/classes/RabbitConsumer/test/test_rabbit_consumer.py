"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 23/07/2021

Questo componente serve per testare RabbitConsumer
"""

import pytest
from ..lib.rabbit_consumer.RabbitConsumer   import RabbitConsumer
from typing                                 import Union
from aio_pika.exceptions                    import QueueEmpty

LOGIN_TOKEN                                                 = "amqp://guest:guest@rabbitmq:5672/"
QUEUE_NAME                                                  = "hello"


@pytest.mark.asyncio
async def test_consumer():

    cons:RabbitConsumer                                     = RabbitConsumer(LOGIN_TOKEN,QUEUE_NAME)
    outcome:Union[ None , Exception]                        = await cons.start()
    assert issubclass (type(outcome) , Exception) == False

    res:Union[ None , Exception]                            = await cons.consume()
    assert issubclass (type(res) , Exception) == False or type(res) == QueueEmpty
    print("[!] Messaggio Recuperato: {} ".format(res))


    res:Union[ None , Exception]                            = await cons.stop()
    assert issubclass (type(res) , Exception) == False
    