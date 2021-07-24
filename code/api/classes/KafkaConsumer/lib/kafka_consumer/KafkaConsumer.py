"""
@author           	:  rscalia                  \n
@build-date         :  Thu 15/07/2021           \n
@last-update        :  Sat 24/07/2021           \n

Questo componente serve per consumare i record scritti su Kafka
"""

from confluent_kafka                        import Consumer, KafkaException, TopicPartition
from kafka.structs                          import TopicPartition
from typing                                 import List,Callable, Union
from ..time_stamp_manager.TimeStampManager  import TimeStampManager
from ..network_serializer.NetworkSerializer import NetworkSerializer
import signal
import json

class KafkaConsumer (object):


    def start (self, pServer:str, pGroupId:str, pOffsetReset:str, pTopics:List[str], pExitTimes:int=2, pInfineFetch:bool=False) -> Union[ None , Exception ]:
        """
        Questo metodo configura il Consumatore Kafka

        Args:\n
            pServer             (str)                   : host e porta nel formato "host:port"
            pGroupId            (str)                   : nome del Consumer Group
            pOffsetReset        (str)                   : impostazione offset del Topic
            pTopics             (List[str])             : lista di topic da consumare 
            pExitTimes          (int | DEF = 2)         : numero di tentativi prima di chiudere il polling in ricerca di nuovi messaggi
            pInfineFetch        (bool | DEF = False)    : se impostato a True accadrà che il componente cerca messaggi infinitcamente, sovrascrive il parametro pExitTimes

        Returns: \n
                                ( Union [ None , Exception ]  ) 

        Raises: \n
            Exception                       : Eccezione generica 
        """
        if ( hasattr(self, "_consumer") == True):
            self.stop()

        self._server:str                    = pServer
        self._groudId:str                   = pGroupId
        self._offsetSetup:str               = pOffsetReset
        self._topics:List[str]              = pTopics
        self._exitTimes:int                 = pExitTimes
        self._infiniteFetch:bool            = pInfineFetch
        self._retrievedMsg:List[dict]       = []
        self._conf:dict                     = { 'bootstrap.servers':    self._server,
                                                'group.id':             self._groudId,
                                                'auto.offset.reset':    self._offsetSetup,
                                              }
        self._serializer:NetworkSerializer  = NetworkSerializer()

        try:
            self._consumer:Consumer         = Consumer(self._conf)
            self._consumer.subscribe(self._topics , on_assign=self._on_assign)
        except Exception as exp:
            return exp


    def stop (self) -> Union[ None , Exception ]:
        """
        Questa funzione permette di stoppare la connessione con Apache Kafka

        Returns: \n
            ( Union[ None , Exception ])  

        Raises: \n
            Exception       : eccezione generica, molto probabilmente scaturita da un doppio tentativo di chiusura di connessione
        """
        try:
            self._consumer.close()
        except Exception as exp:
            return exp
    

    def _on_assign (self, pClient:Consumer, pPartitions:List[TopicPartition]) -> None:
        """
        Imposta l'offset della Partizione a 0
        
        Args:
            pClient         (Consumer)          : consunmatore
            pPartition      (TopicPartition)    : partizione a cui è iscritto il consumatore
        """
        for partition in pPartitions:
            partition.offset = 0

        pClient.assign(pPartitions)


    def _signal_handler(self, pSignal:signal, pMethod:Callable) -> None:
        """
        Cattura il CTRL+C da Tastiera

        Args:
            pSignal         (signal)        : segnale catturato
            pMethod         (Callable)      : metodo che gestisce l'evento
        """
        raise KeyboardInterrupt


    def consume (self,  pVerbose:str=False , pLowDateInTimeStampSec:int=None, pHighDateInTimeStampSec:int=None) -> Union [ List[dict], KafkaException , Exception ]:
        """
        Questo metodo permette di consumare i record del Topic scelto\n

        Args:\n
            pVerbose                (bool | DEF = False)         : se vero vengono stampati a schermo i messaggi
            
            pLowDateInTimeStampSec  (int  | DEF = None)          : timestamp (in secondi) della data di inizio dei messaggi che si vogliono prelevare

            pHighDateInTimeStampSec (int  | DEF = None)          : timestamp (in secondi) della data di fine dei messaggi che si vogliono prelevare

        Returns:\n
                            Union [ List[dict], KafkaException , Exception ]            : lista di record restituiti\n

                            Formato Record:
                                - **topic**: nome del topic\n
                                - **partition**, partizione \n
                                - **msg_offset**, partizione messaggio\n
                                - **msg_key**, chiave messaggio \n
                                - **msg_payload**, contenuto del messaggio

        Raises:\n
            KeyboardInterrupt   : interruzione dell'Utente
            KafkaException      : eccezione di kafka
            Exception           : eccezione generica
        """

        #Impostazione della cattura dei tasti CTRL+C
        signal.signal(signal.SIGINT, self._signal_handler)

        #Variabili che gestiscono la Logica del Ciclo
        fail_counter:int                = 0
        to_fetch:bool                   = True
        self._retrievedMsg:List[dict]   = []

        try:
            while ( fail_counter < self._exitTimes or self._infiniteFetch == True ) and to_fetch == True:

                #Consumo un messaggio ogni 1 secondo
                msg:object         = self._consumer.poll(timeout=1.0)

                #Se non trovo nulla, incremento il contatore dei fallimenti
                if msg is None:
                    fail_counter +=1
                    continue

                if msg.error():
                    raise KafkaException(msg.error())

                else:
                    
                    timestamp_in_sec:int   = TimeStampManager.timestampMs2Sec( msg.timestamp()[1] )


                    #Check Validità Timestamp dal Basso
                    if ( pLowDateInTimeStampSec != None and timestamp_in_sec < pLowDateInTimeStampSec):
                        continue

                    #Check Validità Timestamp dall'Alto
                    if ( pHighDateInTimeStampSec != None and timestamp_in_sec > pHighDateInTimeStampSec):
                        continue


                    formatted_data:str     = TimeStampManager.timestamp2Date (timestamp_in_sec)

                    #Processo il Messaggio
                    record:dict = {
                                        "topic"             :   msg.topic()                 ,
                                        "partition"         :   msg.partition()             ,
                                        "offset"            :   msg.offset()                ,
                                        "timestamp_sec"     :   timestamp_in_sec            ,
                                        "date"              :   formatted_data              ,
                                        "key"               :   str( msg.key() )            ,
                                        "payload"           :   msg.value()
                                         }


                    #Eventuale Stampa del messaggio Ricevuto
                    if (pVerbose == True):
                        self.prettyPrint(record)


                    self._retrievedMsg.append( record )
                    
        except KeyboardInterrupt:
            self.stop()
            to_fetch = False

        except KafkaException as kmsg:
            self.stop()
            return kmsg

        except Exception as msg:
            self.stop()
            return msg


        #Riordino Lista Record Recuperati in Ordine Cronologico
        sorted(self._retrievedMsg, key= lambda record:record["timestamp_sec"] )  

        #Restituisco al chiamante i messaggi scaricati
        return self._retrievedMsg


    def prettyPrint (self, pRecord:dict ) -> None:
        """
        Questa funzione stampa in maniera gradevole un record Kafka

        Args:\n
            pRecord             (dict)      : record da stampare
        """

        payload_deser:dict      = self._serializer.decodeJson(pRecord['payload'])
        print ("\n\n[RECORD]: \n-> Topic: {}\n-> Partition: {}\n-> Offset: {}\n-> Date: {}\n-> Key: {}\n-> Payload:\n\t ".format(                                               pRecord['topic'] , 
                                                                pRecord['partition'],
                                                                pRecord["offset"],
                                                                pRecord["date"],
                                                                pRecord["key"]
                                                                ))  
        self.dictPrettyPrint(payload_deser)


    def dictPrettyPrint(self, pDict:dict , pIndent:int=1) -> None:
        """
        Questo metodo permette di stampare in maniera gradevole i dizionari

        Args:\n
            pDict           (dict)                  : dizionario da stampare
            pIndent         (int | DEF = 1)         : indentazione
        """
        for key, value in pDict.items():

            print('\t' * pIndent + str(key))
            if isinstance(value, dict):
                self.dictPrettyPrint(value, pIndent+1)
            else:
                print('\t' * (pIndent+1) + "-> "+ str(value) + "\n")