"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Tue 27/07/2021                       \n

Questo componente serve per testare il framework di Event-Sourcing del progetto AutoLearn.
"""

from ..lib.abstract_event_sourcing.DomainEvent              import DomainEvent
from ..lib.concrete_event_sourcing.AutoLearnLogEntity       import AutoLearnLogEntity
from ..lib.concrete_event_sourcing.KafkaEventStore          import KafkaEventStore
from ..lib.event_sourcing_utility.event_sourcing_utility    import getLocalLogger , make_behavioral_event , setUpEventSourcing , final_communication_log

import time
import random
from typing                                                 import Union
import pytest
import asyncio
from logging                                                import Logger
import os


ENTITY_ID:str                               = "testeventsourcing"
EVENT_STORE_PARAMS:dict                     = { "host_name":"kafka" , "port":"9092" , "topic":ENTITY_ID , "partition":0 }
EVENT_TO_PRODUCE:int                        = 10
DATA_TO_WRITE:dict                          = {"key":b"test", "value":{ "payload":"train_dat_req", "field":0 } ,  "timestamp":0}


@pytest.mark.asyncio
async def test_es ():

    #Inizializzazione EventStore
    event_store:KafkaEventStore             = KafkaEventStore()
    outcome:Union[None, Exception]          = await event_store.start(EVENT_STORE_PARAMS)
    assert issubclass( type( outcome ) , Exception ) == False


    #Inizializzazione Oggetto Entità
    app_entity:AutoLearnLogEntity           = AutoLearnLogEntity()
    app_entity.init(ENTITY_ID, event_store)


    #Test Rewind
    outcome:Union[None, Exception]          = await app_entity.rewind()
    assert issubclass( type( outcome ) , Exception ) == False
    print ("[!] Number of Recovered Records: {}".format( len(app_entity._eventList) ))


    #Test Singleton
    entity:AutoLearnLogEntity               = AutoLearnLogEntity()


    #Test creazione Eventi
    for i in  range(EVENT_TO_PRODUCE):
        current_time:int                    = int( time.time() * 1000 )
        DATA_TO_WRITE["value"]["field"]     = random.randint(0,50)
        DATA_TO_WRITE["timestamp"]          = current_time

        fake_event:DomainEvent              = DomainEvent(ENTITY_ID , current_time , DATA_TO_WRITE  )
        outcome:Union[None, Exception]      = await entity.emit(fake_event)
        assert issubclass( type( outcome ) , Exception ) == False


    #Test Rewind dopo Scrittura
    old_list:List[DomainEvent]              = entity._eventList.copy()
    print ("\n[BEFORE] Length Event List: {}".format(len( old_list ) ))

    outcome:Union[None, Exception]          = await entity.rewind()
    assert issubclass( type( outcome ) , Exception ) == False    
    assert len(old_list) == len(entity._eventList)
    print ("\n[AFTER] Length Event List: {}".format( len( entity._eventList ) ))


    #Stop EventStore
    outcome:Union[None, Exception]          = await event_store.stop()
    assert issubclass( type( outcome ) , Exception ) == False

    print ("\n\n<<<<<<<<<< TEST GENERALE ANDATO A BUON FINE >>>>>>>>>>>>>>>>")


@pytest.mark.asyncio
async def test_utility ():

    #Test GetLogger
    logger:Logger                               = getLocalLogger("TestService")
    assert logger.name == "TestService__"+ str(os.getpid())

    #Test SetUp Event-Store
    event_store:KafkaEventStore                 = KafkaEventStore()
    net_logger:AutoLearnLogEntity               = AutoLearnLogEntity()
    outcome:bool                                = await setUpEventSourcing("TestService" , event_store , net_logger, EVENT_STORE_PARAMS)
    assert outcome == True

    #Test Costruzione evento
    timestamp:int                               = int(time.time()*1000)
    event:DomainEvent                           = make_behavioral_event (b"Test",timestamp ,"Test" , "Test_Dest" , "send" ,"async", "test_tk" )
    
    #Test Record build
    record:dict                                 = {}
    record["key"]                               = b"Test"
    record["value"]                             = {}
    record["value"]["source_service"]           = "Test"
    record["value"]["destination_service"]      = "Test_Dest"
    record["value"]["message_type"]             = "send"
    record["value"]["com_type"]                 = "async"
    record["value"]["payload"]                  = "test_tk"
    record["timestamp"]                         = timestamp

    assert event._entityId == "Test" and event._eventTimeStamp == timestamp and event._eventPayload == record

    
    #Test final comunication log
    await final_communication_log("Test","Test_Dest","async","test_tk",net_logger)

    #Riavvio Event-Store e effettuo una lettura da quest'ultimo
    outcome:Union[None , Exception]             = await event_store.start(EVENT_STORE_PARAMS)
    assert issubclass (type(outcome) , Exception) == False

    data:Union[ List[dict] , Exception]         = await event_store.read()
    assert issubclass (type(data) , Exception) == False

    #Verifico che il contenuto letto sia uguale a quello scritto
    last_record:dict                            = data[-1]
    assert last_record["payload"]               == record["value"]

    #Stop Event Store
    await event_store.stop()

    print ("\n\n<<<<<<<<<< TEST UTILITY ANDATO A BUON FINE >>>>>>>>>>>>>>>>")