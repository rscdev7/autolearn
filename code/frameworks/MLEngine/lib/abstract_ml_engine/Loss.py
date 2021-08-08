"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sun 08/08/2021                       \n

Questo componente implementa un wrapper ad un'implementazione di una Loss per un algoritmo di ML
"""
from typing             import List, Union
from abc                import ABC, ABCMeta, abstractmethod

class Loss (ABC, metaclass=ABCMeta):

    __slots__ = ("_lossImpl" , "_computeDevice")
    @abstractmethod
    def setUp(self, pHyperParams:dict = {} , pComputeDevice:str="cpu") -> Union [ None , Exception ]:
        """
        Questo metodo permette di effettuare il setup di un'opportuna Loss Function utilizzando degli appositi Iperparametri.

        Args:\n
            pHyperParams                (dict | DEF = {})              : lista di coppia chiave-valore rappresentanti gli iperparametri della Loss

            pComputeDevice              (str)                          : device di calcolo su cui valutare la loss.
                                                                         Opzioni:\n
                                                                            - **CPU**
                                                                            - **GPU**
                                                                            - **TPU**
                                                                            - **FPGA**
                                                                            - **ASIC**
        
        Returns:\n
            Union [ None , Exception ]

        Raises:\n
            Exception                               : eccezzione derivata da un errore di istanziazione dell'oggetto rappresentante la Loss oppure scelta erronea degli Iperparametri
        """
        pass
        

    @abstractmethod
    def changeComputeDevice(self, pDevice:str) -> Union[ None , Exception ]:
        """
        Questo metodo cambia il device di calcolo su cui viene valutata la Loss

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
    def eval (self, pInput:object) -> Union [ float , Exception ]:
        """
        Questo metodo permette di valutare la Loss su di un input.

        Args:\n
            pInput              (object)        : input della Loss Function

        Returns:\n
            Union [ float , Exception ]

        Raises:\n
            Exception                           : eccezione nella valutazione della Loss sull'Input
        """
        pass