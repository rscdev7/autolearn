"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sat 07/08/2021                       \n

Questo componente implementa un wrapper ad un'implementazione di un algoritmo di Ottimizzazione necessario per addestrare i Modelli di ML.
"""
from typing             import List, Union
from abc                import ABC, ABCMeta, abstractmethod

class Optimizer (ABC, metaclass=ABCMeta):

    __slots__ = ("_optImpl" , "_computeDevice")
    @abstractmethod
    def setUp(self, pHyperParams:List[dict] , pComputeDevice:str="cpu") -> Union [ None , Exception ]:
        """
        Questo metodo permette di effettuare il setup di un'opportuno Optimizer utilizzando degli appositi Iperparametri.

        Args:\n
            pHyperParams                (List[dict])        : lista di coppia chiave-valore rappresentanti gli iperparametri dell'Optimizer

            pComputeDevice              (str)               : device di calcolo su cui viene eseguito l'algoritmo di ottimizzazione.
                                                              Opzioni:\n
                                                                - **CPU**
                                                                - **GPU**
                                                                - **TPU**
                                                                - **FPGA**
                                                                - **ASIC**
        
        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                               : eccezzione derivata da un errore di istanziazione dell'oggetto rappresentante l'Optimizer oppure scelta erronea degli Iperparametri
        """
        pass
        

    @abstractmethod
    def changeComputeDevice(self, pDevice:str) -> Union[ None , Exception ]:
        """
        Questo metodo cambia il device di calcolo su cui viene eseguito l'algoritmo di ottimizzazione.

        Args:\n
            pDevice                 (str)           : device di calcolo da utilizzare \n
                                                      Opzioni:\n
                                                        - **CPU**
                                                        - **GPU**
                                                        - **TPU**
                                                        - **FPGA**
                                                        - **ASIC**

        Returns:\n
            Union[ None , Exception ]

        Raises:\n
            Exception                               : eccezione nella scelta del device di calcolo
        """
        pass


    @abstractmethod
    def step (self, pModelImpl:object , pLossImpl:object , pDataset:object ) -> Union [ None , Exception ]:
        """
        Questo metodo permette di eseguire un'iterazione (step) dell'algoritmo di Ottimizzazione in modo tale da ottimizzare i parametri del Modello rispetto ad una Loss e con l'ausilio di un dataset.

        Args:\n
            pModelImpl              (object)        : oggetto che permette di valutare il modello e di accedere ai suoi parametri
            pLossImpl               (object)        : oggetto che permette di valutare la Loss
            pDataset                (object)        : oggetto che permette di accedere al set di dati da utilizzare come training-set

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                               : eccezione nell'aggiornamento dei parametri del Modello di ML
        """
        pass