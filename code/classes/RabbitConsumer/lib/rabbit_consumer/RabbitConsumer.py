"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 16/07/2021

Questo componente serve per consumare i messaggi in una coda RabbitMQ
"""

import asyncio
from asyncio                                import AbstractEventLoop

import aio_pika
from aio_pika                               import connect, IncomingMessage
from aio_pika.channel                       import Channel
from aio_pika.queue                         import Queue
from aio_pika.connection                    import Connection

from ..network_serializer.NetworkSerializer import NetworkSerializer

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
        self._lastMessage:dict              = None


    async def start (self) -> None:
        """
        Questo metodo avvia il consumatore RabbitMQ

        Raises:
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


    async def stop (self) -> None:
        """
        Questo metodo stoppa il consumatore RabbitMQ

        Raises:
            Exception   : eccezzione generica
        """
        try:
            await self._connection.close()
        except Exception as exp:
            return exp


    def _on_message(self,pMessage:IncomingMessage) -> dict:
        """
        Chiamata di callback all'arrivo dei messaggi
        """
        decoded_msg:dict                    = self._serializer.decodeJson(pMessage.body)
        self._lastMessage:dict              = decoded_msg
        pMessage.ack()


    async def consume (self) -> dict:
        """ 
        Consuma un messaggio dalla coda

        Returns:
                        (dict)  : messaggio recuperato dalla coda

        Raises:
            Exception   : eccezzione generica
        """
        try:
            res:str                 = await self._queue.consume(self._on_message)

            if (self._lastMessage == None):
                return None
            else:
                msg:dict            = self._lastMessage
                self._lastMessage   = None

        except Exception as exp:
            return exp

        return msg
