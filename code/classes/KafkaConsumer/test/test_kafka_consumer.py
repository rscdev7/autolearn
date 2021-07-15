"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 15/07/2021

Questo componente serve per testare KafkaConsumer
"""

from ..lib.kafka_consumer.KafkaConsumer import KafkaConsumer
from typing                             import List

SERVER:str          = "kafka:9092"
GROUP_ID:str        = "zas"
OFF_SET_SETUP:str   = 'smallest'
TOPIC:str           = "Test"
EXIT_TIMES:int      = 2
INFINITE_FETCH:bool = True
VERBOSE:bool        = True

def test_kafka_consumer():

    cs:KafkaConsumer                = KafkaConsumer ()
    cs.setUp(SERVER,GROUP_ID,OFF_SET_SETUP,TOPIC,EXIT_TIMES, INFINITE_FETCH)
    res:List[dict]                  = cs.consume(VERBOSE)
    print ("\n\n\n[!] Messaggi Recuperati:\n\n\n {}".format(res))
    
