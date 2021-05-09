# Module `KafkaLogger` {#KafkaLogger}

@author                 :  rscalia
@version                    :  1.0.0
@build-date         :  Sun 09/05/2021
@last_update        :  Sun 09/05/2021

Questo componente serve per scrivere record di log all'interno di uno Specifico Topic di Apache Kafka





    
## Classes


    
### Class `KafkaLogger` {#KafkaLogger.KafkaLogger}




>     class KafkaLogger(
>         pBrokerName: str,
>         pTopicName: str,
>         pPartition: int,
>         pLoggerName: str
>     )


Costruttore


Args
-----=
pBrokerName    (str)          : Nome dell'host che esegue Kafka
pTopicName     (str)          : Nome del Topic Kafka su cui Scrivere
pPartition     (int)          : Partizione kafka su cui andare a scrivere i record
pLoggerName    (str)          : Nome del logger interno al Software







    
#### Methods


    
##### Method `log` {#KafkaLogger.KafkaLogger.log}




>     async def log(
>         self,
>         pKey: str,
>         pRecord: dict,
>         pTimestamp: int
>     ) ‑> bool


Questo metodo permette di inserire un record all'interno del Topic Kafka precedentemente configurato


Args
-----=
pKey            (str)           : chiave del record da inserire
pRecord         (dict)          : payload del record da inserire
pTimestamp      (int)           : timestamp del record da inserire

Returns
-----=
<code>bool                            </code>
:   restituisce VERO se il messaggio è stato inoltrato correttamente al broker, altrimenti FALSO



    
##### Method `setUp` {#KafkaLogger.KafkaLogger.setUp}




>     async def setUp(
>         self
>     ) ‑> bool


Metodo che connette il componente KafkaLogger con il broker Kafka, una volta fatta tale connessione sarà possibile incominciare ad inviare record al broker


Returns
-----=
<code>bool                                </code>
:   restituisce VERO se il setup è andato a buon fine, altrimenti FALSO



    
##### Method `shutDown` {#KafkaLogger.KafkaLogger.shutDown}




>     async def shutDown(
>         self
>     ) ‑> bool


Metodo che chiude la connessione fra il KafkaLogger e Apache Kafka


Returns
-----=
<code>bool                                </code>
:   restituisce VERO se lo shutdown è andato a buon fine, altrimenti FALSO




--