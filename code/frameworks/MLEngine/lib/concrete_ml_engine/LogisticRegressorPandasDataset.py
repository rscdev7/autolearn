"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 07/08/2021                       \n
@last-update            :  Sat 07/08/2021                       \n

Questo componente implementa un wrapper ad un'implementazione dell'algoritmo LogisticRegressor
"""
from ..abstract_ml_engine.Model             import Model
from ..abstract_ml_engine.Loss              import Loss
from ..abstract_ml_engine.Optimizer         import Optimizer
from ..abstract_ml_engine.Dataset           import Dataset
from sklearn.linear_model                   import LogisticRegression
from sklearn.metrics                        import precision_score
from sklearn.metrics                        import recall_score
from typing                                 import List, Union

class LogisticRegressorPandasDataset (Model):

    __slots__ = ("_modelImpl" , "_computeDevice" , "_randomState")
    def setUp (self, pHyperParams:List[dict] , pComputeDevice:str="cpu") -> Union[ None , Exception ]:
        """
        Questo metodo inizializza opportunamente un Modello di Machine Learning

        Args:\n
            pHyperParams            (List[dict])    : iperparametri da applicare al Modello
                                                      Opzioni:\n
                                                        - **random_state**
                                                        
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
        self._randomState:int                           = pHyperParams['random_state']
        self._computeDevice:str                         = pComputeDevice
        self._modelImpl:LogisticRegression              = LogisticRegression( random_state=self._randomState )


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
        try:
            training_set:object         = pDataset._trainingSet
            label:str                   = pDataset._label
            self._modelImpl.fit( training_set.drop( [label] , axis=1) , training_set[label] )
        except Exception as exp:
            return exp


    def evaluate(self , pDataset:Dataset) -> Union [ List[dict] , Exception ]:
        """
        Questo metodo permette di valutare il Modello di ML sul Test-Set usando un opportuno set di metriche.

        Args:\n
            pDataset                (Dataset)       : dataset su cui valutare il Modello

        Returns:\n
            Union [ List[dict] , Exception ]        : Formato Dizionari:\n
                                                        - **metric_name**     : str
                                                        - **metric_value**    : float
        Raises:\n
            Exception                               : eccezione durante la valutazione del Modello
        """
        try:
            test_set:object             = pDataset._testSet
            label:str                   = pDataset._label

            inf_test_set:object         = test_set.drop( [label] , axis=1)
            ground_truth:DataFrame      = test_set[ label ]

            model_inferences:list       = self.inference(inf_test_set)


            recall:float                = recall_score(model_inferences, ground_truth , average='micro' )
            precision:float             = precision_score(model_inferences , ground_truth ,average='micro')

            metrics_outcome:List[dict]  = [ 
                                                { "metric_name": "precision"    , "metric_value": precision } ,
                                                { "metric_name": "recall"       , "metric_value": recall } ]

            return metrics_outcome

        except Exception as exp:
            return exp


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
        try:
            inference:object       = self._modelImpl.predict(pSample)
            return inference
        except Exception as exp:
            return exp


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
        self._modelImpl                     = pParams["model"]


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
        return self._modelImpl
        