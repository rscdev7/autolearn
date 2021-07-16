"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 16/07/2021

Questo componente serve per testare RabbitConsumer
"""

import pytest
from ..lib.rabbit_consumer.RabbitConsumer import RabbitConsumer

LOGIN_TOKEN                 = "amqp://guest:guest@rabbitmq:5672/"
QUEUE_NAME                  = "Test"


@pytest.mark.asyncio
async def test_consumer():

    cons:RabbitConsumer     = RabbitConsumer(LOGIN_TOKEN,QUEUE_NAME)
    await cons.start()

    res:dict                 = await cons.consume()
    await cons.stop()

    if ( type(res) != None):
        print ("\n[!] Nessun messaggio presente nella coda")
    else:
        print (res) 