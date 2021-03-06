# AutoLearn
![Alt -> Software Architecture](./img/logo.png)

AutoLearn è un Applicativo Distribuito che permette la gestione del ciclo di vita di un Modello di
Machine Learning.


## BUSINESS-LOGIC

### *[ML-PIPELINE]*
>- Visualizza Modelli e Dataset presenti nel Catalogo                                   
>- Training impostando una serie di parametri:                                   
>    - Dataset
>    - Modello
>               
>
>- Calcolo Misure Valutazione Modello sul Test-Set dato il NUMERO_SESSIONE       
>            
>
>- Salvataggio Dati Sessione (Training e/o Evaluation) nello Storage Permanente dato il NUMERO_SESSIONE 

### *[DASHBOARD-PIPELINE]*
>- Visualizza Log Esperimenti di Sessione 
>- Visualizzazione Log Esperimenti Storage Permanente 

### *[ADMIN-PIPELINE]*
>- Visualizza Log Comportamentale di un Singolo Microservizio in ordine cronologico
>- Visualizza Log Comportamentale di tutto il Sistema in ordine cronologico


## PERSISTENZA
- Tutti i dati degli Esperimenti Passati saranno archiviati in una base di dati opportuna
- **Formato**

     - *TIMESTAMP_EXPERIMENT_BUILD*
     - *DATI_ESPERIMENTI*
          - *Train*
          - *Eval*

- Tutti i dati di Sessione saranno archiviati in una base di dati opportuna
- **Formato**

    - *TIMESTAMP_EXPERIMENT_BUILD*
    - *DATI_ESPERIMENTI*
      - *Train*
      - *Eval*

- Tutti i log del Comportamento del Sistema saranno archiviati in un apposito Event Store:
- **Formato**

    - *ID_SOURCE_SERVICE*
    - *ID_DESTINATION_SERVICE* 
    - *MESSAGE_TYPE*
    - *COMMUNICATION_TYPE* 
    - *TIMESTAMP* 
    - *PAYLOAD*

    
## PRESENTAZIONE
- CLI scritta in Python
- Per eseguire le operazioni, il client invocherà ,spesso in maniera asincrona, le procedure remote messe a disposizione dal server attraverso una serie di API REST.


------------------------------------------------------------------------------------------
## REQUISITI PROGETTUALI


### *[MACHINE LEARNING]*
>- I dataset devono risiedere sul Backend
>- Modelli di ML disponibili a Catalogo:
>    - Regressore Logistico
>    - Decision Tree
>    - Random Forest
>    - SVM
>    - Naive Bayes
>
>- Metriche di Valutazione
>    - Precision
>    - Recall


### *[ASPETTI ARCHITETTURALI]*
>- Il Backend sarà a Microservizi
>- Ogni Microservizio espone un REST End-Point
>- Le comunicazioni avverranno sia attraverso chiamate ai REST End-Point che attraverso la Messaggistica.
>- La Logica associata ad ogni chiamata REST verrà gestita da un'apposita Corutine/Processo, generata al momento della chiamata
>
>- I flussi di lavoro presenti nei microservizi sono riassunti di seguito:
>    - **REST-WORKER**, entità che resta in ascolto per chiamate al REST End-Point
>    - **EVENT-WORKER**, entità che resta in ascolto ,asincronicamente, in merito a nuovi eventi associati ad un task specifico
>    *(ES. Comunicazione asincrona fra Microservizi)*
>    - **TASK-WORKER**, entità che prende in carico il task associato alla chiamata di un’API REST
>
>- I Microservizi possono avere più istanze parallele in esecuzione, dato che il Web Server sfrutta il parallelismo
offerto dalle moderne CPU Multi-Core


### *[GESTIONE DELLA SESSIONE]*
>- Il sistema conserva dei dati di sessione che il Client può decidere di confermare in futuro.
>- La conferma di una Sessione implica la sua scrittura nello Storage permanente e la sua
successiva rimozione.
>- Essenzialmente, un record di sessione contiene i dati di Training e di Evaluation.
>- I dati di sessione verranno mantenuti su un apposito Database (DATABASE SESSION STATE).


### *[REQUISITI DI SICUREZZA]*
>- Client e Server utilizzano uno schema di Crittografia Simmetrico per scambiarsi Informazioni Confidenziali.
>- La chiave crittografica sarà una chiave a 128 bit generata dall'Algoritmo AES.
>- Le informazioni Confidenziali delle comunicazioni sono i Dati di Sessione.


### *[MONITORAGGIO]*
>- Lo stato passato dell’applicazione deve essere ricostruibile
>- Ogni Comunicazione fra Microservizi deve essere segnala ed archiviata
>- Ogni Comunicazione Client ------> Backend deve essere segnala ed archiviata
>- Tipologia Archiviazione:
>    - Memoria
>    - Event Store


### *[REQUISITI DI MODULARITÀ]*
>- La costruzione dell'applicativo rende *semplice* l'aggiunta di nuovi Modelli all'interno del Catalogo
>- La costruzione dell'applicativo rende *semplice* l'aggiunta di nuove Misure di Valutazione all'interno del Catalogo
    

------------------------------------------------------------------------------------------
## ARCHITETTURA DEL SOFTWARE
![Alt -> Software Architecture](./img/arch.png)

## DESIGN PATTERN
- Session State                                     
- Remote Proxy                                     
- Forward-Receiver                               
- Remote Facade
- Data Transfer Object
- Serialized LOB    
- Streaming Pipeline                                 
- Event Sourcing  
- Singleton                                  


## STACK SOFTWARE - GENERALE
![Alt -> General Software Stack](./img/general_sw.svg)

## STACK SOFTWARE - MICROSERVIZI
![Alt -> Microservices Software Stack](./img/micro_sw.svg)

------------------------------------------------------------------------------------------
## REQUISITI CLIENT

Requisiti:

1. [Anaconda](https://www.anaconda.com/products/individual)
2. Python 3.7
3. Librerie Python da installare:

        aiofiles
        pytest
        pytest-asyncio
        cryptography
        sphinx
        sphinx_rtd_theme
        rinohtype
        pdoc3
        aiohttp[speedups]
        requests
        typing
        dataclasses

Comandi Installazione Ambiente, Interprete e Librerie:

        conda env create -f $REPO_DIR/client_requirements/conda_client_env.yaml
        
        
## ISTRUZIONI PER ESEGUIRE IL PROGETTO

#### BACKEND - SISTEMI UNIX

1. Installare *Docker* e *docker-compose* sul proprio Sistema
2. Impostare le Variabili d'Ambiente modificando opportunamente il file 
        
        $REPO_DIR/docker/production_env/.env

   In particolar modo, è necessario modificare i *path ai Volumi* dei Container.

   Inoltre, può essere di utilità modificare le seguenti ulteriori variabili d'ambiente:
   
        - Porte Servizi (tutte le variabili che contengono il token "PORT")
        - WEB_SERVER_WORKERS, numero di worker per il Web Server 

-------------------------------------------------------------------------------------------------

**[OSSERVAZIONE]** 
Le carelle dell'Event-Store e del Config-Service devono essere assegnate ad un utente specifico; per fare ciò, eseguire i seguenti comandi:

        sudo chown -R 1001:1001 ($EVENT_STORE_DATA_PATH)
        sudo chown -R 1001:1001 ($CONFIG_SERVICE_DATA_PATH)
-------------------------------------------------------------------------------------------------

3. Avviare l'Event-Store:

        cd $REPO_DIR/docker/production_env

        docker-compose up -d event_store


4. Impostare i parametri dell'Event-Store all'interno del file:
        
        $REPO_DIR/docker/production_env/event_store_set_up.sh


5. Concedere i permessi di esecuzione agli script necessari per inizializzare l'Event-Store:
        
        chmod u+x $REPO_DIR/docker/production_env/event_store_set_up.sh
        chmod u+x $REPO_DIR/docker/production_env/init_event_store.sh


6. Inizializzare l'Event-Store:
        
        ./$REPO_DIR/docker/production_env/init_event_store.sh


7. Stoppare esecuzione Event-Store:
        
        docker-compose down


8. Avviare il Backend:

        cd $REPO_DIR/docker/production_env
    
        ./build_img.sh
    
        docker-compose up -d


#### FRONTEND
1. All'interno della cartella del client dell'applicativo, modificare le porte dei servizi in base a quelle scelte al punto **2** delle istruzioni per inizializzare il *Backend*.

    Per fare ciò, sarà necessario modificare il file:

        $CLIENT_APP_DIR/config/cfg.conf

    in modo tale da inserire le suddette porte.

    Per tanto, sarà necessario modificare tutte le variabili del tipo 
        
        (SERVICE__NAME)_BASE_ADDRESS = http://localhost:$PORT/(SERVICE_NAME)/api

    con le porte scelte al punto **2**.
<br /> 

2. Avviare il Frontend: 

        cd $CLIENT_APP_DIR

        conda activate autolearn_client_env

        python3 autolearn_client.py


## ISTRUZIONI PER AVVIARE LA CONSOLE DI AMMINISTRAZIONE DEL SISTEMA
1. A Sistema Avviato, aprire una shell da un Host *interno* alla Network dei Container
2. Eseguire il seguente comando:

        docker attach admin


## DEMO 

#### APPLICAZIONE
![Alt -> Demo](./demo/demo.gif)

#### ADMIN CONSOLE
![Alt -> Admin Console](./demo/admin_console_demo.gif)

------------------------------------------------------------------------------------------
## STRATEGIA DI BRANCHING
- **MAIN**, codice di produzione.
- **DEVELOP**, codice di sviluppo.

## STRUTTURA DEL REPOSITORY
- **code**, contiene il codice del progetto.
    - **0.legacy**, contiene componenti *Software Deprecati* che restano significativi.
    - **api**, librerie del progetto
        - **classes**, contiene le classi del progetto.
        - **modules**, contiene i moduli (insieme di funzioni) del progetto.
    - **frameworks**, contiene i framework (serie di classi correlate) del progetto.
    - **solutions**, contiene il Software di Produzione del progetto.
- **demo**, contiene immagini demo del Software in esecuzione.
- **docker**, contiene le immagini docker utilizzate come ambiente di sviluppo/produzione.
- **img**, contiene le immagini usate nei vari file markdown del repository.
- **report**, contiene la relazione del progetto.
- **talk**, contiene un blocco di slide che illustra le caratteristiche salienti del progetto.

------------------------------------------------------------------------------------------
## AUTORE
- [@r-scalia](https://github.com/rscdev7) Rosario Scalia

## RINGRAZIAMENTI 
- [@e-tramontana](https://www.dmi.unict.it/tramonta/) Prof Emiliano Alessio Tramontana (UniCT)
- [@a-fornaia](https://www.dmi.unict.it/fornaia/) Prof Andrea Francesco Fornaia (UniCT)    
