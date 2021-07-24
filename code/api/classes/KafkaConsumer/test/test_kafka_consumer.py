"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 15/07/2021

Questo componente serve per testare KafkaConsumer
"""

from ..lib.kafka_consumer.KafkaConsumer import KafkaConsumer
from typing                             import List, Union

SERVER:str          = "kafka:9092"
GROUP_ID:str        = "zas"
OFF_SET_SETUP:str   = 'smallest'
TOPIC:str           = "test"
EXIT_TIMES:int      = 2
INFINITE_FETCH:bool = True
VERBOSE:bool        = True


def test_kafka_consumer():
    """
    Test del Consumatore Kafka, si assume che siano presenti record nel Topic prima di eseguire il test
    """

    cs:KafkaConsumer                                = KafkaConsumer ()

    outcome:Union [None , Exception]                = cs.start(SERVER,GROUP_ID,OFF_SET_SETUP,TOPIC,EXIT_TIMES, INFINITE_FETCH)
    assert issubclass (type(outcome) , Exception)   == False

    outcome:List[dict]                              = cs.consume(VERBOSE)
    assert issubclass (type(outcome) , Exception)   == False
    print ("\n\n\n[!] Messaggi Recuperati:\n\n\n {}".format(outcome))


    outcome:Union [None , Exception]                = cs.stop()
    assert issubclass (type(outcome) , Exception)   == False
    
