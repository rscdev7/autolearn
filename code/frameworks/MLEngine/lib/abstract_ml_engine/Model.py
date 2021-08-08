"""
@author           	    :  rscalia                              \n
@build-date             :  Fri 06/08/2021                       \n
@last-update            :  Sun 08/08/2021                       \n

Questa classe rappresenta un'interfaccia ad un Modello di Machine Learning
"""
from typing             import List, Union
from abc                import ABC, ABCMeta, abstractmethod
from .Loss              import Loss
from .Optimizer         import Optimizer
from .Dataset           import Dataset

class Model (ABC, metaclass=ABCMeta):

    __slots__ = ("_modelImpl" , "_computeDevice")
    @abstractmethod
    def setUp (self, pHyperParams:List[dict] , pComputeDevice:str="cpu") -> Union[ None , Exception ]:
        """
        Questo metodo inizializza opportunamente un Modello di Machine Learning

        Args:\n
            pHyperParams            (List[dict])    : iperparametri da applicare al Modello
            pComputeDevice          (str)           : device di calcolo su cui eseguire il Modello \n
                                                      Opzioni:\n
                                                        - **CPU**
                                                        - **GPU**
                                                        - **TPU**
                                                        - **FPGA**
                                                        - **ASIC**
        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                               : eccezzione derivata da un errore di istanziazione dell'oggetto rappresentante il Modello di ML oppure scelta erronea degli Iperparametri
        """
        pass


    @abstractmethod
    def changeComputeDevice(self, pDevice:str) -> Union[ None , Exception ]:
        """
        Questo metodo cambia il device di calcolo su cui viene eseguito il Modello

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
    def fit (self, pDataset:Dataset , pTrainingHyperParams:List[dict] = None , pLoss:Loss = None , pOptimizer:Optimizer = None , pLogger:object = None ) -> Union [ None , Exception ]:
        """
        Questo metodo addestra il Modello di Machine Learning su un apposito dataset utilizzando eventualmente un'implementazione custom di Loss e Optimizer.

        Args:\n
            pDataset                (Dataset)                  : dataset su cui addestrare il Modello di Machine Learning
            pTrainingHyperParams    (List[dict] | DEF = None)  : iperparametri di training
            pLoss                   (Loss       | DEF = None)  : eventuale funzione Custom da ottimizzare
            pOptimizer              (Optimizer  | DEF = None)  : eventuale Optimizer Custom che permette di ottimizzare la Loss

            pLogger                 (object     | DEF = None)  : oggetto che permette di fare logging dell'andamento del training               

        Returns:\n
            Union [ None , Exception ]      

        Raises:\n
            Exception                                           : eccezione durante il training, molto probabilmente proveniente dall'esecuzione del Modello o nella computazione attuata dall'Optimizer
        """
        pass


    @abstractmethod
    def evaluate(self , pDataset:Dataset) -> Union [ List[dict] , Exception ]:
        """
        Questo metodo permette di valutare il Modello di ML sul Test-Set usando un opportuno set di metriche.

        Args:\n
            pDataset                (Dataset)       : dataset su cui valutare il Modello

        Returns:\n
            Union [ List[dict] , Exception ]

        Raises:\n
            Exception                               : eccezione durante la valutazione del Modello
        """
        pass


    @abstractmethod
    def inference(self, pSample:object) -> Union [ object , Exception ]:
        """
        Questo metodo permette di fare inferenza su un apposito sample.

        Args:\n
            pSample             (object)        : input del Modello di ML

        Returns:\n
            Union [ object , Exception ]

        Raises:\n
            Exception                           : eccezione durante l'inferenza del Modello
        """
        pass


    @abstractmethod
    def loadCheckPoint(self, pParams:dict=None ) -> Union [ None , Exception ]:
        """
        Questo metodo permette di caricare un checkpoint di un Modello di ML

        Args:\n
            pParams             (dict | DEF = None)     : eventuali parametri di caricamento del Modello

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                                   : eccezione durante il caricamento del Modello, magari per l'assenza del salvataggio su Disco
        """
        pass


    @abstractmethod
    def saveCheckPoint(self, pParams:dict=None ) -> Union [ None , Exception ]:
        """
        Questo metodo permette di salvare un checkpoint di un Modello di ML

        Args:\n
            pParams             (dict | DEF = None)     : eventuali parametri di salvataggio del checkpoint

        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                                   : eccezione durante il salvataggio del Modello
        """
        pass
        