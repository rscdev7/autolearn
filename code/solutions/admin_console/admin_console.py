"""
@author           	    :  rscalia                              \n
@build-date             :  Fri 13/28/2021                       \n
@last-update            :  Fri 13/08/2021                       \n

Questo componente serve implementa una console di amministrazione per il progetto AutoLearn
"""



from lib.admin_config.AdminConfig                  import AdminConfigurator
from lib.exception_manager.ExceptionManager        import ExceptionManager
from lib.kafka_consumer.KafkaConsumer              import KafkaConsumer
from typing                                         import Union, List


UNABLE_TO_READ_CFG:int              = 1
TOPICS:List[str]                    = [ "catalog" , "training" , "evaluation" , "session" , "sessionRecord" , "sessionUpdate" , "storage" , "storageRecord" ]

CODE_2_TOPICS:dict                  = {     "1" : "catalog",
                                            "2" : "training",
                                            "3" : "evaluation",
                                            "4" : "session",
                                            "5" : "sessionRecord",
                                            "6" : "sessionUpdate",
                                            "7" : "storage",
                                            "8" : "storageRecord"
                                         }



# [1] Lettura configurazione
cfg:AdminConfigurator               = AdminConfigurator()
outcome:Union[ None , Exception ]   = cfg.inspect()

if ExceptionManager.lookForExceptions(outcome):
    print("\n[!] ERRORE, impossibile leggere configurazione applicativo\n")
    exit(UNABLE_TO_READ_CFG)

# [2] Istanzio Oggetto Event-Store
event_store:KafkaConsumer           = KafkaConsumer()


# [3] User Prompt
while True:

    print("\n\n<<<<<<<<<<<<<<<<<<<<<< AUTOLEARN ADMIN CONSOLE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    print ("1) Visualizza Log Comportamentali per Microservizio")
    print("2) Visualizza Log comportamentali del Sistema")
    print ("3) Chiudi Applicazione")

    choice:str      = input("\n>> ")

    try:
        casted_choice:int   = int(choice)
    except Exception as exp:
        print("\n[!] ERRORE, per scegliere un'opzione è necessario inserire un numero intero\n")
        continue

    if casted_choice <1 or casted_choice > 3:
        print("\n[!] ERRORE, per scegliere un'opzione è necessario inserire un numero intero compreso fra 1 e 3\n")
        continue



    if casted_choice == 1:

        print ("\t[1] catalog")
        print ("\t[2] training")
        print ("\t[3] evaluation")
        print ("\t[4] session")
        print ("\t[5] sessionRecord")
        print ("\t[6] sessionUpdate")
        print ("\t[7] storage")
        print ("\t[8] storageRecord")

        choice:str          = input("\n>> ")

        try:
            c_choice:int   = int(choice)
        except Exception as exp:
            print("\n[!] ERRORE, per scegliere un'opzione è necessario inserire un numero intero\n")
            continue

        if c_choice <1 or c_choice > 8:
            print("\n[!] ERRORE, per scegliere un'opzione è necessario inserire un numero intero compreso fra 1 e 8\n")
            continue

        topic:str               = [ CODE_2_TOPICS[ choice ] ]

        outcome:Union [None , Exception]                = event_store.start(cfg.EVENT_STORE_LOGIN_TOKEN, cfg.OFF_SET_SETUP, topic , cfg.WAIT_TIME, cfg.INFINITE_FETCH)
        
        if ExceptionManager.lookForExceptions(outcome):
            print ("\n[!] ERRORE nella connessione con l'event-store \n-> Causa: {}".format( str( outcome ) ))
            continue

        event_store.consume(True)
        


    if casted_choice == 2:

        outcome:Union [None , Exception]                = event_store.start(cfg.EVENT_STORE_LOGIN_TOKEN, cfg.OFF_SET_SETUP, TOPICS , cfg.WAIT_TIME, cfg.INFINITE_FETCH)
        
        if ExceptionManager.lookForExceptions(outcome):
            print ("\n[!] ERRORE nella connessione con l'event-store \n-> Causa: {}".format( str( outcome ) ))
            continue

        event_store.consume(True)


    if casted_choice == 3:
        print("\n")
        break