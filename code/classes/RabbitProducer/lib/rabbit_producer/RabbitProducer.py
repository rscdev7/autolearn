"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 16/07/2021

Questo componente serve per scrivere messaggi in una coda di RabbitMQ
"""


import asyncio
from asyncio                                import AbstractEventLoop
from aio_pika                               import connect, Message,DeliveryMode
from aiormq.types                           import DeliveredMessage
from aio_pika.channel                       import Channel
from aio_pika.connection                    import Connection

from ..network_serializer.NetworkSerializer import NetworkSerializer


class RabbitProducer (object):

    def __init__ (self, pQueueName:str , pLoginToken:str) -> object:
        """
        Costruttore

        Args:
            pQueueName          (str)      : nome della coda su cui scrivere
            pLoginToken         (str)      : token di loggin a RabbitMQ
        """
        self._queueName:str                 = pQueueName
        self._loginToken:str                = pLoginToken
        self._serializer:NetworkSerializer  = NetworkSerializer()

    
    async def start (self) -> None:
        """
        Questo metodo avvia un Produttore RabbitMQ

        Raises:
            Exception   : eccezzione generica
        """
        #Getting event loop
        loop:AbstractEventLoop = asyncio.get_event_loop()

        try:
            #Perform connection 
            self._connection:Connection         = await connect(self._loginToken, loop=loop)
            self._channel:Channel               = await self._connection.channel()
        except Exception as msg:
            return msg


    async def stop (self) -> None:
        """
        Questo metodo stoppa un Produttore RabbitMQ

        Raises:
            Exception   : eccezione generica
        """
        try:
            await self._connection.close()
        except Exception as msg:
            return msg


    async def pubblish (self, pRecord:dict) -> DeliveredMessage:
        """
        Questo metodo pubblica un messaggio sulla coda configurata nell'oggetto corrente.\n

        Args:\n
            pRecord         (dict)                  : record da inviare

        Returns:\n
                            (DeliveredMessage)      : notifica messaggio inviato

        Raises:\n
            Exception                               : eccezione generica
        """ 
        ser_data:bytes              = self._serializer.encodeJson(pRecord)
        msg:Message                 = Message(ser_data , delivery_mode=DeliveryMode.PERSISTENT )

        try:
            result:DeliveredMessage = await self._channel.default_exchange.publish(msg,routing_key=self._queueName)
            return result
        except Exception as msg:
            return msg