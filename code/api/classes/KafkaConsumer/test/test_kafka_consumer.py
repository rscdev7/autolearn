"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last-update        :  Mon 08/08/2021

Questo componente serve per testare KafkaConsumer
"""

from ..lib.kafka_consumer.KafkaConsumer import KafkaConsumer
from typing                             import List, Union


SERVER:str          = "kafka:9092"

OFF_SET_SETUP:str   = 'smallest'
TOPICS:str          = [ "storage" ]
MULTI_TOPICS:str    = [ "storage" , "session" ]

WAIT_TIME:int       = 2
INFINITE_FETCH:bool = False
VERBOSE:bool        = True


def test_kafka_consumer():
    """
    Test del Consumatore Kafka, si assume che siano presenti record nel Topic prima di eseguire il test
    """

    cs:KafkaConsumer                                = KafkaConsumer ()

    #General Test
    outcome:Union [None , Exception]                = cs.start(SERVER, OFF_SET_SETUP, TOPICS, WAIT_TIME, INFINITE_FETCH)
    assert issubclass (type(outcome) , Exception)   == False


    outcome:List[dict]                              = cs.consume(VERBOSE)
    assert issubclass (type(outcome) , Exception)   == False
    print ("\n\n\n[!] Messaggi Recuperati:\n\n\n {}".format(outcome))


def test_kafka_bounds():

    cs:KafkaConsumer                                = KafkaConsumer ()

    #Test TimeStamp Messaggi Low
    outcome:Union [None , Exception]                = cs.start(SERVER, OFF_SET_SETUP, TOPICS, WAIT_TIME, INFINITE_FETCH)
    assert issubclass (type(outcome) , Exception)   == False

    outcome:List[dict]                              = cs.consume(VERBOSE , pLowDateInTimeStampSec=318294000)
    assert issubclass (type(outcome) , Exception)   == False
    print ("\n\n\n[!] Messaggi Recuperati con TimeStamp Low:\n\n\n {}".format(outcome))


    #Test TimeStamp Messaggi High
    outcome:Union [None , Exception]                = cs.start(SERVER, OFF_SET_SETUP, TOPICS, WAIT_TIME, INFINITE_FETCH)
    assert issubclass (type(outcome) , Exception)   == False

    outcome:List[dict]                              = cs.consume(VERBOSE , pHighDateInTimeStampSec=318294000)
    assert issubclass (type(outcome) , Exception)   == False
    print ("\n\n\n[!] Messaggi Recuperati con TimeStamp High:\n\n\n {}".format(outcome))


def test_kafka_multi_topic():

    cs:KafkaConsumer                                = KafkaConsumer ()

    #Test MultiTopic
    outcome:Union [None , Exception]                = cs.start(SERVER, OFF_SET_SETUP, TOPICS, WAIT_TIME, INFINITE_FETCH)
    assert issubclass (type(outcome) , Exception)   == False

    outcome:List[dict]                              = cs.consume(VERBOSE)
    assert issubclass (type(outcome) , Exception)   == False
    print ("\n\n\n[!] Messaggi Recuperati Multi-Topic:\n\n\n {}".format(outcome))