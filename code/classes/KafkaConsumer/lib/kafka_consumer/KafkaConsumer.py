"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 15/07/2021

Questo componente serve per consumare i record scritti su Kafka
"""

from confluent_kafka    import Consumer, KafkaException, TopicPartition
from kafka.structs      import TopicPartition
from typing             import List,Callable
import signal

class KafkaConsumer (object):


    def __init__ (self) -> object:
        """
        Costruttore
        """
        pass


    def setUp (self,pServer:str, pGroupId:str, pOffsetReset:str, pTopic:str, pExitTimes:int=2, pInfineFetch:bool=False) -> object:
        """
        Questo metodo configura il Consumatore Kafka

        Args:\n
            pServer             (str)       : host e porta nel formato "host:port"
            pGroupId            (str)       : nome del Consumer Group
            pOffsetReset        (str)       : impostazione offset del Topic
            pTopic              (str)       : topic del consumatore Kafka
            pExitTimes          (int)       : numero di tentativi prima di chiudere il polling in ricerca di nuovi messaggi
            pInfineFetch        (bool)      : se impostato a True accadrà che il componente cerca messaggi infinitcamente, sovrascrive il parametro pExitTimes
        """
        self._server:str                    = pServer
        self._groudId:str                   = pGroupId
        self._offsetSetup:str               = pOffsetReset
        self._topic:str                     = pTopic
        self._exitTimes:int                 = pExitTimes
        self._infiniteFetch:bool            = pInfineFetch
        self._retrievedMsg:List[dict]       = {}
        self._conf:dict                     = { 'bootstrap.servers':    self._server,
                                                'group.id':             self._groudId,
                                                'auto.offset.reset':    self._offsetSetup,
                                              }

        self._consumer:Consumer             = Consumer(self._conf)
        self._consumer.subscribe([self._topic] , on_assign=self._on_assign)


    def stop (self) -> None:
        """
        Questa funzione permette di stoppare la connessione con Apache Kafka
        """
        self._consumer.close()
    

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


    def consume (self, pVerbose:str=False) -> List[dict]:
        """
        Questo metodo permette di consumare i record del Topic scelto\n

        Args:
            pVerbose        (bool)          : se vero vengono stampati a schermo i messaggi

        Returns:\n
                            (List[dict])    : lista di record restituiti\n
                            Formato Record:
                                - **topic**: nome del topic\n
                                - **partition**, partizione \n
                                - **msg_offset**, partizione messaggio\n
                                - **msg_key**, chiave messaggio \n
                                - **msg_payload**, contenuto del messaggio

        Raises:\n
            KeyboardInterrupt   : interruzione dell'Utente
            KafkaException      : eccezzione di kafka
            Exception           : eccezzione generica
        """

        signal.signal(signal.SIGINT, self._signal_handler)

        fail_counter:int                = 0
        self._retrievedMsg:List[dict]   = []

        try:

            while fail_counter < self._exitTimes or self._infiniteFetch == True:

                #Consumo un messaggio ogni 1 secondo
                msg:object         = self._consumer.poll(timeout=1.0)

                #Se non trovo nulla incremento il contatore dei fallimenti
                if msg is None:
                    fail_counter +=1
                    continue

                if msg.error():
                    raise KafkaException(msg.error())

                else:
                    #Processo il Messaggio
                    record:dict = {
                                        "topic":        msg.topic(),
                                        "partition":    msg.partition(),
                                        "msg_offset":   msg.offset()        ,
                                        "msg_key":      str( msg.key() ),
                                        "msg_payload":  msg.value()
                                         }


                    #Eventuale Stampa del messaggio Ricevuto
                    if (pVerbose == True):
                        print ("\n\n[Message]: \n-> Topic: {}\n-> Partition: {}\n-> Offset: {}\n-> Key: {}\n-> Payload:\n\n {} ".format(             record['topic'] , 
                                                              record['partition'],
                                                              record["msg_offset"],
                                                              record["msg_key"],
                                                              record["msg_payload"]))


                    self._retrievedMsg.append( record )

        except KeyboardInterrupt:
            self.stop()
            return self._retrievedMsg

        except KafkaException as kmsg:
            self.stop()
            return kmsg

        except Exception as msg:
            self.stop()
            return msg


        #Chiudo la connessione in modo da fare commit sui record letti
        self.stop()

        #Restituisco al chiamante i messaggi scaricati
        return self._retrievedMsg