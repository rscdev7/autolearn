"""
@author           	    :  rscalia                              \n
@build-date             :  Fri 13/08/2021                       \n
@last-update            :  Fri 13/08/2021                       \n

Questo modulo rappresente lo starter dell'applicativo AutoLearn
"""

import asyncio
from asyncio                                                import AbstractEventLoop , Queue
import signal
from signal                                                 import Signals
from typing                                                 import List, Union
import pickle

from lib.async_input.utils                                  import int_input
from lib.train_request_wizard.training_wizard               import training_wizard
from lib.client_config.ClientConfigurator                   import ClientConfigurator
from lib.exception_manager.ExceptionManager                 import ExceptionManager
from lib.local_ml_engine.LocalMLEngine                      import LocalMLEngine
from lib.time_stamp_manager.TimeStampManager                import TimeStampManager
import aiofiles
from pprint                                                 import pprint
from aiohttp.client_exceptions                              import ClientConnectorError


UNABLE_TO_READ_CFG:int      = 1


async def shut_down_system( pQueue:Queue ) -> None:
    """
    # **shut_down_system**

    Questa funzione inserisce un messaggio nella coda che intima le altre corutine di arrestare le loro computazioni

    Args:\n
        pQueue                      ( Queue )       : coda asincrona
    """
    await pQueue.put("exit")


async def download_catalog(pLocalMLEngine:LocalMLEngine , pRetentationTimeInDays:int ) -> Union [ dict , Exception ]:
    """
    # **download_catalog**

    Questa funzione permette di scaricare il catalogo dei Modelli di ML dalla rete, nel caso di problemi nel download verrà usato un catalogo precedentemente salvato su disco a patto che quest'ultimo non sia obsoleto.

    Args:\n
        pLocalMLEngine              (LocalMLEngine)     : ML Engine
        pRetentationTimeInDays      (int)               : numero di giorni superati i quali il catalogo diventa obsoleto

    Returns:\n
        Union [ dict , Exception ]

    Raises:\n
        FileNotFoundError                               : checkpoint del catalogo assente su disco
        ValueError                                      : catalogo obsoleto
        Exception                                       : impossibile salvare catalogo su disco
    """    
    outcome:Union[ dict , Exception]                        = await pLocalMLEngine.getCatalog()

    # Gestione Caso Catalogo non disponibile lato Remoto
    if ExceptionManager.lookForExceptions(outcome) or set( outcome.keys() ).difference( set( ['data_lake','models','metrics','learning'] ) ) != set( [] ):
        
        print("\n\n________________________________________WARNING_________________________________________")
        print ("\n[O] Impossibile recuperare catalogo dalla rete, tentativo di caching da disco... ")

        try:
            with open("data/cached_catalog.pkl", "rb") as f:
                saved_catalog:dict  = pickle.load(f)

            catalog_age:int         = saved_catalog['save_time']
            current_time:int        = TimeStampManager.currentTimeStampInSec()


            #86400 è il numero di secondi in un giorno
            if (current_time - catalog_age) > (86400*pRetentationTimeInDays):
                raise ValueError("\n[!] ERRORE, il catalogo dell'applicativo è obsoleto, chiusura applicativo in corso...\n ")


            print ("\n[!] Catalogo caricato correttamente da Disco !")

            print("______________________________________________________________________________________\n")
            catalog:dict            = saved_catalog['catalog']
            return catalog

        except ValueError as exp:
            return exp

        except FileNotFoundError as exp:
            return FileNotFoundError("\n[!] ERRORE, impossibile caricare catalogo da disco, chiusura applicativo \n-> Causa: {}".format( str(exp) ) )

        except Exception as exp:
            return Exception("\n[!] ERRORE, impossibile caricare catalogo da disco, chiusura applicativo \n-> Causa: {}".format( str(exp) ) )


    # [2] Salvataggio Catalogo Scaricato su Disco
    try:
        with open("data/cached_catalog.pkl", "wb") as f:
            pickle.dump( { 'catalog' : outcome , 'save_time' : TimeStampManager.currentTimeStampInSec() } , f)

    except Exception as exp:
        print("\n[!] ERRORE, impossibile salvare catalogo su disco \n")


    return outcome



async def application_logic (pMLEngine:LocalMLEngine , pInputQueue:Queue , pNotifyQueue:Queue , pContentQueue:Queue) -> None:
    """
    # **application_logic**

    Questa funzione permette di eseguire la logica dell'applicativo

    Args:\n
        
        pMLEngine           (LocalMLEngine)                 : engine di Machine Learning

        pInputQueue         (asincio.Queue)                 : coda che permette di ricevere le richieste di computazione

        pNotifyQueue        (asincio.Queue)                 : coda che permette di inoltrare gli esiti delle richieste fatte

        pContentQueue       (asincio.Queue)                 : coda che permette di inoltrare i dati associati alle richieste fatte
 
    Raises:\n
        Exception                                           : eccezione a runtime dell'applicativo
    """
    while True:
       
        # [1] Prelievo Richiesta
        request:dict                                        = await pInputQueue.get()
        if type(request) == str:
            break

        response:dict                                       = request.copy()


        # [2] Eseguo Richiesta
        if request['req_type'] == "trainMLModel":
            outcome:Union[ str , Exception , dict ]         = await pMLEngine.trainMLModel( request['data'] )

        elif request['req_type'] == "evaluateMLModel":
            outcome:Union[ str , Exception , dict ]         = await pMLEngine.evaluateMLModel( request['data'] )

        elif request['req_type'] == "viewSessionData":
            outcome:Union[  dict, Exception  ]              = await pMLEngine.viewSessionData()

        elif request['req_type'] == "saveSession":
            outcome:Union[ str , Exception , dict  ]        = await pMLEngine.saveSession( request['data'] )

        elif request['req_type'] == "viewExperiments":
            outcome:Union[  dict, Exception  ]              = await pMLEngine.viewExperiments()


        # [3] Controllo Output Richiesta
        if request['req_type'] in [ "trainMLModel" , "evaluateMLModel" , "saveSession" ]:

            if type(outcome) == dict:
                response['data']                            = "Unable to decode Response Format"

            else:
                response['data']                            = outcome

            # [4] Return Outcome Richiesta
            await pNotifyQueue.put( response )

        else:
            
            if ExceptionManager.lookForExceptions(outcome) == False:
                for exp in outcome['experiments']:
                    del exp['train_data']['model']['model_checkpoint']

            response['data']                                = outcome

            # [4] Return Outcome Richiesta
            await pContentQueue.put( response )
        

async def command_line_interface(pInputQueue:Queue , pNotifyQueue:Queue , pContentQueue , pExitQueue:Queue , pCatalog:dict) -> None:
    """
    # **command_line_interface**

    Questa funzione rappresenta l'interfaccia utente

    Args:\n
        
        pInputQueue         (asincio.Queue)                 : coda che permette di inoltrare le richieste di computazione all'apposita corutine

        pNotifyQueue        (asincio.Queue)                 : coda che permette di recuperare gli esiti delle richieste fatte

        pContentQueue       (asincio.Queue)                 : coda che permette di recuperare i dati delle richieste fatte

        pExitQueue          (asincio.Queue)                 : coda che permette di chiudere l'applicativo in maniera consona     

        pCatalog            (dict)                          : catalogo applicativo

    Raises:\n
        Exception                                           : eccezione a runtime dell'applicativo
    """
    while True:

        # [0] Se ricevo un messaggio di "exit" nella coda, arresto la cortutine
        try:
            pExitQueue.get_nowait()

            print("\n[!] Chiusura applicativo in corso...\n")
            await asyncio.sleep(1)
            await pInputQueue.put("exit")
            break
        except Exception as exp:
            pass
        
        # [1] Prompt
        print("\n\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< AUTOLEARN >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        print("1) Visualizza il Catalogo")
        print("2) Addestra un Modello di Machine Learning")
        print("3) Valuta un Modello di Machine Learning")
        print("4) Visualizza Esperimenti di Sessione")
        print("5) Salva Sessione")
        print("6) Visualizza Esperimenti presenti nello Storage Permanente")
        print("7) Visualizza Notifiche")
        print("8) Chiudi Applicazione ( CTRL + C + INVIO )")

        choice:Union[ int , Exception ]      = await int_input("")


        # [1] Check Chiusura Applicativo
        try:
            pExitQueue.get_nowait()

            print("\n[!] Chiusura applicativo in corso...\n")
            await asyncio.sleep(1)
            await pInputQueue.put("exit")
            break
        except Exception as exp:
            pass


        # [1.1] Check Errori Input
        if ExceptionManager.lookForExceptions(choice):
            print("\n[!] ERRORE, per scegliere un'opzione bisogna inserire un numero intero\n")
            continue
        

        # [2] Elaborazione Scelte Utente
        if choice < 1 or choice > 8:
            print("\n[!] ERRORE, per scegliere un'opzione bisogna inserire un numero compreso fra 1 e 8\n")
            continue

        if choice == 1:
            print("\n")
            pprint(pCatalog , indent=3)
            continue


        elif choice == 2:
            train_request:Union[dict, Exception]      = await training_wizard(pCatalog)

            if ExceptionManager.lookForExceptions(train_request):
                print("\n[!] ERRORE, eccezione durante la compilazione della richiesta di training \nCausa: {}".format(str(train_request)))
            else:
                request:dict        = { 
                                        'req_type'  : 'trainMLModel' ,   
                                        'time'      : TimeStampManager.currentTimeStampInSec() , 
                                        'data'      : train_request 
                                       }

                print ("\n\n___________________________PANORAMICA RICHIESTA TRAINING______________________\n\n")
                pprint(request['data']['train_data'] , indent=3 )
                print ("\n______________________________________________________________________________\n\n")


                await pInputQueue.put( request )


        elif choice == 3:
            sess_id:Union[ int , Exception ] =  await int_input("\n\n[Q] Inserisci l'ID di Sessione associato all'Esperimento contente il Modello di ML da valutare\n")

            if ExceptionManager.lookForExceptions(sess_id):
                print("\n[!] ERRORE, l'id di Sessione da inserire deve essere un numero intero\n")
                continue
            else:
                request:dict        = { 
                                        'req_type'  : 'evaluateMLModel' ,   
                                        'time'      : TimeStampManager.currentTimeStampInSec() , 
                                        'data'      : sess_id 
                                       }

                await pInputQueue.put( request )

        
        elif choice == 4:
            request:dict        = { 
                                        'req_type' : 'viewSessionData' 
                                  }
            await pInputQueue.put( request )
            
            session_data:Union [ dict , Exception ] = await pContentQueue.get()

            if ExceptionManager.lookForExceptions(session_data) or type(session_data['data']) == ClientConnectorError:
                print("\n[!] ERRORE, errore durante la query in merito ai dati di sessione \n-> Causa: {}\n".format(session_data))
                continue

            else:

                if type(session_data['data']) == dict:
                    for idx,experiment in enumerate(session_data['data']['experiments']):
                        print("\n[!] Esperimento {} \n\n".format(idx+1))
                        pprint(experiment , indent=3)
                else:
                    print("\n[!] ERRORE durante la query in merito ai dati di sessione \n")
                    continue


        elif choice == 5:
            sess_id:Union[ int , Exception ] =  await int_input("\n\n[Q] Inserisci l'ID di Sessione associato all'Esperimento da salvare\n")

            if ExceptionManager.lookForExceptions(sess_id):
                print("\n[!] ERRORE, l'id di Sessione da inserire deve essere un numero intero\n")
                continue
            else:
                request:dict        = { 
                                        'req_type'      : 'saveSession' ,   
                                        'time'          : TimeStampManager.currentTimeStampInSec() , 
                                        'data'          : sess_id 
                                       }

                await pInputQueue.put( request )


        elif choice == 6:
            request:dict        = { 
                                    'req_type' : 'viewExperiments' ,   
                                  }

            await pInputQueue.put( request )

            exp_data:Union [ dict , Exception ] = await pContentQueue.get()
            if ExceptionManager.lookForExceptions(exp_data) or type(exp_data['data']) == ClientConnectorError:
                print("\n[!] ERRORE, errore durante la query in merito ai dati degli Esperimenti \n-> Causa: {}\n".format(exp_data))
                continue

            else:
                if type(exp_data['data']) == dict:
                    for idx,experiment in enumerate(exp_data['data']['experiments']):
                        print("\n[!] Esperimento {} \n\n".format(idx+1))
                        pprint(experiment , indent=3)
                else:
                    print("\n[!] ERRORE durante la query in merito ai dati degli Esperimenti \n")
                    continue
        

        elif choice == 7:

            is_empty:bool          = True

            while True:
                try:
                    response:dict  = pNotifyQueue.get_nowait()
                    req_type:str   = response['req_type']
                    time:int       = response['time']
                    msg:str        = response['data']

                    print ("\n[RESPONSE] \n\t-> Tipo Richiesta: {} \n\t-> Data & Ora Richiesta: {} \n\t-> Contenuto Risposta: {} \n".format( req_type  ,TimeStampManager.timestamp2Date(time) , msg ))

                    is_empty       = False

                except Exception as exp:
                    if is_empty: print("\n[!] Non sono presenti notifiche ! \n")
                    break


        elif choice == 8:
            print("\n[!] Chiusura applicativo in corso...\n")
            await asyncio.sleep(1)
            await pInputQueue.put("exit")
            break


async def launcher (pCfg:ClientConfigurator , pInputQueue:Queue , pNotifyQueue:Queue , pContentQueue:Queue  , pExitQueue:Queue) -> None:
    """
    # **launcher**

    Questa funzione permette di lanciare l'applicativo AutoLearn

    Args:\n

        pCfg                (ClientConfigurator)            : componente che mantiene la configurazione dell'applicativo
        
        pInputQueue         (asincio.Queue)                 : coda che permette di inoltrare le richieste di computazione all'apposita corutine

        pNotifyQueue        (asincio.Queue)                 : coda che permette di recuperare gli esiti delle richieste fatte

        pContentQueue       (asincio.Queue)                 : coda che permette di recuperare i dati delle richieste fatte

        pExitQueue          (asincio.Queue)                 : coda che permette di chiudere l'applicativo in maniera consona     

    Raises:\n
        Exception                                           : eccezione a runtime dell'applicativo
    """

    # [1] Init LocalMLEngine
    ml_engine:LocalMLEngine                                 = LocalMLEngine(pCfg)
    outcome:Union[ None , Exception ]                       = await ml_engine.start()

    if ExceptionManager.lookForExceptions(outcome):
        print("\n[!] ERRORE, impossibile avviare componente di Machine Learning dell'applicativo, arresto applicazione")
    else:

        # [2] Download Catalogo dalla Rete
        catalog:Union[dict, Exception]                      = await download_catalog(ml_engine , pCfg.CATALOG_RETENTATION_TIME_IN_DAYS)

        if ExceptionManager.lookForExceptions(catalog):
            print( str(catalog) )

        else:
            task_to_launch:list     = [ command_line_interface(pInputQueue , pNotifyQueue , pContentQueue ,  pExitQueue , catalog) , application_logic(ml_engine , pInputQueue , pNotifyQueue , pContentQueue  ) ]

            await asyncio.gather( *task_to_launch )

  
    # [3] Stop LocalMLEnginw
    outcome:Union[ None , Exception ]                        = await ml_engine.stop()
    

    # [4] Invio segnale cancel() a tutte le corutine ancora in esecuzione
    tasks:set                                                = [ task for task in asyncio.all_tasks() if task is not
             asyncio.current_task() ]

    [ task.cancel() for task in tasks ]


    # [5] Stop Event-Loop
    loop:AbstractEventLoop                                   = asyncio.get_event_loop()
    loop.stop()

    

def main():
    """
    # **MAIN**
    """

    #[0] Init Componenti
    cfg:ClientConfigurator                                  = ClientConfigurator()
    outcome:Union[ None , Exception ]                       = cfg.inspect()

    if ExceptionManager.lookForExceptions(outcome):
        print("\n[!] ERRORE, impossibile leggere file di configurazione\n")
        exit (UNABLE_TO_READ_CFG)

    # [1] Costruzione Strutture dati Comunicazione Corutine
    exit_queue:Queue                                        = asyncio.Queue(1)
    in_queue:Queue                                          = asyncio.Queue(0)
    notify_queue:Queue                                      = asyncio.Queue(0)
    content_queue:Queue                                     = asyncio.Queue(0)

    # [2] Costruzione Strutture dati per gestire segnali chiusura applicativo
    loop:AbstractEventLoop                                  = asyncio.get_event_loop()
    signals:tuple                                           = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sgn in signals:
        loop.add_signal_handler( sgn, lambda sgn = sgn : asyncio.create_task( shut_down_system( exit_queue ) ) )


    # [3] Avvio Applicativo
    try:
        loop.create_task( launcher( cfg , in_queue , notify_queue , content_queue  , exit_queue ) )
        loop.run_forever()

    finally:
        loop.close()
    


main()   