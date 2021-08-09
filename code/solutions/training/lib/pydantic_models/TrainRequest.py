"""
@author           	:  rscalia              \n
@build-date         :  Thu 03/08/2021       \n
@last-update        :  Sun 08/08/2021       \n

Definizione PyDantic model che codifica una richiesta di Training
"""

from pydantic               import BaseModel, Field
from typing                 import List, Optional, Dict, Union



class HyperParam (BaseModel):
    hyper_param_name:str                                                                            = Field(..., title="Nome Iperparametro",description="Nome dell' Iperparametro") 
    hyper_param_value:Union[ int , float , bool , str , List[float] , List[int] , List[str] ]       = Field(..., title="Valore Iperparametro",description="Valore Iperparametro") 


class Dataset (BaseModel):
    dataset_name:str                                = Field(..., title="Nome Dataset",description="Nome di un dataset presente nel catalogo")
    dataset_task:str                                = Field(..., title="Task",description="Task a cui è correlato il dataset")
    split_test:float                                = Field(..., title="Percentuale di Split Test-Set",description="Numero in virgola Mobile compreso fra 0 e 1")
    split_seed:int                                  = Field(..., title="Seed Esperimememti",description="Intero utilizzato come seme per gli algoritmi randomici presenti negli esperimenti, utile fissarlo per avere una ripetibilità degli esperimenti")

class Model (BaseModel):
    model_name:str                                  = Field(..., title="Nome Modello",description="Nome di un modello presente nel catalogo")
    model_task:str                                  = Field(..., title="Task Modello",description="Problema affrontato dal Modello")
    model_hyperparams:List[HyperParam]              = Field(None, title="Iperparametri Modello",description="Iperparametri Scelti per il Modello")

class Learning (BaseModel):
    loss:str                                        = Field(None, title="Loss",description="Funzione Errore da minimizzare")
    learning_algorithm:str                          = Field(None, title="Algoritmo di Ottimizzazione",description="Algoritmo di Ottimizzazione scelto")
    learning_hyperparams:List[HyperParam]           = Field(..., title="Iperparametri Algoritmo di Learning",description="Iperparametri Algoritmo di Learning")


class Training(BaseModel):
    dataset:Dataset                                 = Field(...,title="Dataset",description="Dataset utilizzato per addestrare il Modello Neurale")
    model:Model                                     = Field(...,title="Model",description="Modello ML Scelto per l'Addestramento")
    learning:Learning                               = Field(None,title="Learning",description="Parametri dell'Algoritmo di learning impiegato nell'esperimento")

class TrainRequest (BaseModel):
    train_data:Training                             = Field(..., title="Parametri del Training",description="Parametri del Training")
