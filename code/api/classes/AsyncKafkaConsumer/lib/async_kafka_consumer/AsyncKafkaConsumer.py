"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 24/07/2021                       \n
@last-update            :  Sun 24/07/2021                       \n

Questo componente implementa un consumatore Asincrono kafka

"""

from aiokafka                                       import AIOKafkaConsumer, TopicPartition, AIOKafkaProducer
import asyncio
import json 
import os
from typing                                         import Union, List
from ..network_serializer.NetworkSerializer         import NetworkSerializer


class AsyncKafkaConsumer (object):

    def __init__(self, pBrokerName:str, pBrokerPort:str , pTopic:str, pPartition:int , pGroupId:str="def_group") -> object:
        """
        Costruttore

        Args:\n
            pBrokerName         (str)       : host name del broker Kafka
            pBrokerPort         (str)       : port number del broker Kafka
            pTopic              (str)       : topic di interesse
            pPartition          (int)       : partizione di interesse nel Topic
            pGroupId            (str)       :
        """
        self._topic:str                         = pTopic
        self._partition:int                     = pPartition
        self._groupId:str                       = pGroupId
        self._connectionToken:str               = pBrokerName + ":" + pBrokerPort 

        self._topicObj:TopicPartition           = None
        self._nRecordInTopicPart:int            = None
        self._consumer:AIOKafkaConsumer         = None

        self._serializer:NetworkSerializer      = NetworkSerializer()
        self._retrievedRecords:List[dict]       = []

    
    async def start (self) -> Union [None , Exception]:
        """
        Questo metodo avvia un consumatore Kafka Asincrono

        Returns:\n
            Union [ None , Exception ]
        
        Raises: \n
            Exception   : eccezione scaturità da un errore durante la creazione del Kafka Consumer
        """
        self._consumer                      = AIOKafkaConsumer(self._topic,  bootstrap_servers=self._connectionToken, group_id=self._groupId)

        try:
            await self._consumer.start()
            
            outcome:Union [ None , Exception ] = await self._rewindTape()
            if issubclass ( type(outcome) , Exception ):
                raise Exception( str(outcome) )

        except Exception as msg:
            return msg


    async def _rewindTape(self) -> Union [ None , Exception ]:
        """
        Questo metodo permette di impostare l'inizio della consumazione dei record al record iniziale della partizione del Topic.

        Returns:\n
            Union [ None , Exception ]
        
        Raises: \n
            Exception   : eccezione scaturità da un errore durante il seek
        """
        self._topicObj:TopicPartition                = TopicPartition(self._topic , self._partition)
        result:None                                  = self._consumer.seek(self._topicObj , 0)


        
    async def stop (self) -> Union [None , Exception]:
        """
        Questo metodo stoppare un consumatore Kafka Asincrono

        Returns:\n
            Union [ None , Exception ]
        
        Raises: \n
            Exception   : eccezione scaturità da un errore durante la chiusura della connessione con Apache Kafka
        """
        try:
            await self._consumer.stop()
        except Exception as msg:
            return msg

    
    async def consume (self) -> Union [ List[dict] , Exception]:
        """
        Questo metodo consuma tutti i messaggi disponibili nella partizione del Topic scelto.

        Returns:\n
            Union [ List[dict] , Exception ]

        Raises:\n
            Exception   : eccezione durante la lettura dei record
        """
        self._retrievedRecords = []

        try:
            
            #Calcolo Numero Record presenti nella Partizione del Topic
            wrapped_n_record_of_topic:dict      = await self._consumer.end_offsets( [ self._topicObj ] )
            self._nRecordInTopicPart:int        = wrapped_n_record_of_topic[ self._topicObj ]

            #Caso in cui non sono presenti record nel topic
            if self._nRecordInTopicPart == 0: return []

            #Avvio Consumazione
            async for data in self._consumer:
                
                
                #Unwrap Dati Record i-esimo
                record:dict             = {}
                record["topic"]         = data.topic
                record["partition"]     = data.partition
                record["offset"]        = data.offset
                record["key"]           = data.key
                record["timestamp_ms"]  = data.timestamp
                record["payload"]       = self._serializer.decodeJson(data.value)

                #Archiviazione Dati prelevati
                self._retrievedRecords.append ( record )
            

                #Se il record era l'ultimo messaggio della partizione, esci
                if (data.offset+1 == self._nRecordInTopicPart):
                    break

        except Exception as exp:
            return exp


        #Restituisco dati al chiamanete
        return self._retrievedRecords
