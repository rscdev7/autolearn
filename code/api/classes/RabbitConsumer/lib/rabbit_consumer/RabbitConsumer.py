"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 23/07/2021

Questo componente serve per consumare i messaggi in una coda RabbitMQ
"""

import asyncio
from asyncio                                import AbstractEventLoop

import aio_pika
from aio_pika                               import connect, IncomingMessage
from aio_pika.channel                       import Channel
from aio_pika.queue                         import Queue
from aio_pika.exceptions                    import QueueEmpty
from aio_pika.connection                    import Connection

from ..network_serializer.NetworkSerializer import NetworkSerializer
from typing                                 import Union


class RabbitConsumer (object):


    def __init__ (self, pLoginToken:str , pQueueName:str) -> object:
        """
        Costruttore

        Args:
            pLoginToken             (str)       : token per loggarsi a RabbitMQ
            pQueueName              (str)       : nome della coda da dove prelevare i messaggi

        """
        self._connectionToken:str           = pLoginToken
        self._queueName:str                 = pQueueName
        self._serializer:NetworkSerializer  = NetworkSerializer()


    async def start (self) -> Union[None , Exception]:
        """
        Questo metodo avvia il consumatore RabbitMQ

        Returns:\n
            Union[None , Exception]

        Raises:\n
            Exception   : eccezzione generica
        """
        loop:AbstractEventLoop                  = asyncio.get_event_loop()
    
        try:
            #Perform connection
            self._connection:Connection         = await connect(self._connectionToken, loop=loop)

            #Creating a channel
            self._channel:Channel               = await self._connection.channel()

            #Declaring queue
            self._queue:Queue                   = await self._channel.declare_queue(self._queueName, durable=True)

        except Exception as msg:
            return msg


    async def stop (self) -> Union[None , Exception]:
        """
        Questo metodo stoppa il consumatore RabbitMQ

        Returns:\n
            Union[None , Exception]

        Raises:\n
            Exception   : eccezzione generica
        """
        try:
            await self._connection.close()
        except Exception as exp:
            return exp


    async def consume (self) -> Union[ dict , QueueEmpty , Exception ]:
        """ 
        Consuma un messaggio dalla coda

        Returns:
            Union[ dict , QueueEmpty , Exception ]:  : messaggio recuperato dalla coda o Eccezione

        Raises:
            Exception   : eccezzione generica
            QueueEmpty  : la coda è vuota
        """
        try:
            incoming_message:IncomingMessage    = await self._queue.get()
            incoming_message.ack()

            retrieved_msg:dict                  = self._serializer.decodeJson(incoming_message.body)

            return retrieved_msg

        except QueueEmpty as qe:
            return qe

        except Exception as exp:
            return exp