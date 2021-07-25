"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questo componente serve per testare il framework di Event-Sourcing del progetto AutoLearn.
"""

from ..lib.abstract_event_sourcing.DomainEvent        import DomainEvent
from ..lib.concrete_event_sourcing.AutoLearnLogEntity import AutoLearnLogEntity
from ..lib.concrete_event_sourcing.KafkaEventStore    import KafkaEventStore

import time
import random
from typing                                            import Union
import pytest
import asyncio


ENTITY_ID:str               = "testeventsourcing"
EVENT_STORE_PARAMS:dict     = { "host_name":"kafka" , "port":"9092" , "topic":ENTITY_ID , "partition":0 }
EVENT_TO_PRODUCE:int        = 10
DATA_TO_WRITE:dict          = {"key":b"test", "value":{ "payload":"train_dat_req", "field":0 } ,  "timestamp":0}


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