"""
@author           	:  rscalia
@version  		    :  1.0.1
@build-date         :  Sun 09/05/2021
@last_update        :  Thu 15/07/2021

Questo componente serve per scrivere record di log all'interno di uno Specifico Topic di Apache Kafka

"""

import os
import asyncio
from aiokafka import AIOKafkaProducer
import logging
import json
from ..network_serializer.NetworkSerializer import NetworkSerializer


class KafkaLogger (object):

    def __init__ (self, pBrokerName:str, pTopicName:str, pPartition:int , pLoggerName:str="logger") -> object:
        """
        Costruttore\n

        Args:\n
            pBrokerName    (str)                    : Nome dell'host che esegue Kafka
            pTopicName     (str)                    : Nome del Topic Kafka su cui Scrivere
            pPartition     (int)                    : Partizione kafka su cui andare a scrivere i record
            pLoggerName    (str, optional)          : Nome del logger interno al Software

        """

        self._connectionToken:str                               = pBrokerName + ":"+ os.environ['KAFKA_BROKER_PORT'] 
        self._topic:str                                         = pTopicName
        self._partition:int                                     = pPartition

        self._logger:Logger                                     = logging.getLogger(pLoggerName)
        
        self._producer:AIOKafkaProducer                         = None
        self._serializer:NetworkSerializer                      = NetworkSerializer()


    async def setUp (self) -> bool:
        """
        Metodo che connette il componente KafkaLogger con il broker Kafka, una volta fatta tale connessione sarà possibile incominciare ad inviare record al broker

        Returns:
            bool                                : restituisce VERO se il setup è andato a buon fine, altrimenti FALSO

        Raises:
            Excpetion           : eccezzione generica
        """

        loop:asyncio                                    = asyncio.get_event_loop()
        self._producer:AIOKafkaProducer                 = AIOKafkaProducer( bootstrap_servers=self._connectionToken )

        try:
            await self._producer.start()

            self._logger.info("Produttore Kafka Avviato Correttamente")

            return True

        except Exception as msg:
            self._logger.error ("Errore nell'avvio del KafkaLogger: {}".format(msg))

            return False


    async def shutDown (self)  -> bool:
        """
        Metodo che chiude la connessione fra il KafkaLogger e Apache Kafka

        Returns:
            bool                                : restituisce VERO se lo shutdown è andato a buon fine, altrimenti FALSO

        Raises:
            Excpetion           : eccezzione generica
        """

        try:
            await self._producer.stop()

            self._logger.info("Produttore Kafka Arrestato Correttamente")

            return True

        except Exception as msg:
            self._logger.error ("Errore nella chiusura del KafkaLogger: {}".format(msg))

            return False


    async def log (self, pKey:bytes , pRecord:dict, pTimestamp:int) -> bool:
        """
        Questo metodo permette di inserire un record all'interno del Topic Kafka precedentemente configurato

        Args:
            pKey            (bytes)         : chiave del record da inserire
            pRecord         (dict)          : payload del record da inserire
            pTimestamp      (int)           : timestamp del record da inserire

        Returns:
            bool                            : restituisce VERO se il messaggio è stato inoltrato correttamente al broker, altrimenti FALSO

        Raises:
            Excpetion           : eccezione generica
        """

        try:
            #Serializzazione Dati
            encoded_ser_data:bytes      = self._serializer.encodeJson(pRecord)


            #Invio dati al Broker
            await self._producer.send_and_wait(topic=self._topic, key=pKey, value=encoded_ser_data, timestamp_ms=pTimestamp, partition=self._partition)


            self._logger.info("Record archiviato correttamente sull'Event Store")

            return True
            
        except Exception as msg:
            self._logger.error ("Errore nell'invio del Record al Broker Kafka: {}".format(msg))

            return False