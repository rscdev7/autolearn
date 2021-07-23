"""
@author           	:  rscalia
@build-date         :  Sun 09/05/2021
@last_update        :  Fri 23/07/2021

Questo componente serve per scrivere record di log all'interno di uno Specifico Topic di Apache Kafka
"""

import os
import asyncio
from aiokafka                               import AIOKafkaProducer
import logging
import json
from ..network_serializer.NetworkSerializer import NetworkSerializer
from typing                                 import Union

class KafkaLogger (object):

    def __init__ (self, pBrokerName:str, pBrokerPort:str , pTopicName:str, pPartition:int ) -> object:
        """
        Costruttore\n

        Args:\n
            pBrokerName    (str)                    : Nome dell'host che esegue Kafka
            pBrokerPort    (str)                    : Porta dell'host su cui sta girando Kafka
            pTopicName     (str)                    : Nome del Topic Kafka su cui Scrivere
            pPartition     (int)                    : Partizione kafka su cui andare a scrivere i record
        """

        self._connectionToken:str                               = pBrokerName + ":"+ pBrokerPort
        self._topic:str                                         = pTopicName
        self._partition:int                                     = pPartition
        
        self._producer:AIOKafkaProducer                         = None
        self._serializer:NetworkSerializer                      = NetworkSerializer()


    async def start (self) -> Union [ None , Exception ]:
        """
        Metodo che connette il componente KafkaLogger con il broker Kafka, una volta fatta tale connessione sarà possibile incominciare ad inviare record al broker

        Returns:\n
            Union[ None , Exception ]                              

        Raises:\n
            Excpetion           : eccezione generica
        """
        
        loop:asyncio                                    = asyncio.get_event_loop()
        self._producer:AIOKafkaProducer                 = AIOKafkaProducer( bootstrap_servers=self._connectionToken )

        try:
            await self._producer.start()
        except Exception as msg:
            return msg


    async def stop (self)  -> Union [ None , Exception ]:
        """
        Metodo che chiude la connessione fra il KafkaLogger e Apache Kafka

        Returns:\n
            Union[ None , Exception ]                               

        Raises:\n
            Excpetion                           : eccezione generica
        """
        try:
            await self._producer.stop()
        except Exception as msg:
            return msg


    async def log (self, pKey:bytes , pRecord:dict, pTimestamp:int) -> Union[ None , Exception ]:
        """
        Questo metodo permette di inserire un record all'interno del Topic Kafka precedentemente configurato

        Args:\n
            pKey            (bytes)         : chiave del record da inserire
            pRecord         (dict)          : payload del record da inserire
            pTimestamp      (int)           : timestamp del record da inserire

        Returns:\n
            Union[ None , Exception ]                            

        Raises:\n
            Excpetion                       : eccezione generica
        """

        try:
            #Serializzazione Dati
            encoded_ser_data:bytes      = self._serializer.encodeJson(pRecord)

            #Invio dati al Broker
            await self._producer.send_and_wait(topic=self._topic, key=pKey, value=encoded_ser_data, timestamp_ms=pTimestamp, partition=self._partition)

        except Exception as msg:
            return msg