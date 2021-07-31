"""
@author           	    :  rscalia                              \n
@build-date             :  Sat 31/07/2021                       \n
@last-update            :  Sat 31/07/2021                       \n

Questo modulo racchiude una serie di funzioni di utilità per i microservizi.
"""
import pickle
from ..network_serializer.NetworkSerializer                 import NetworkSerializer
from bson.binary                                            import Binary
from typing                                                 import Union


def ser_model__db_2_net( pRecord:dict ) -> Union[ dict , Exception ]:
    """
    # **ser_model__db_2_net**

    Questa funzione permette di convertire il Modello di ML presente nei record del DB in un formato adatto per viaggiare in rete

    Args:\n
        pRecord             (dict)                  : record del DB contente il modello di ML

    Returns:\n
        Union[ dict , Exception ]

    Raises:\n
        Exception                                   : eccezione derivata dall'assenza del modello sul record passato dal chiamante
    """
    serializer:NetworkSerializer                             = NetworkSerializer()

    try:
        model_ck:bytes                                       = pRecord['train_data']['model']['model_checkpoint']
    except Exception as exp:
        return exp

    model_obj:object                                         = pickle.loads( model_ck )
    model_obj_ready_for_net_transfer:str                     = serializer.encodeBinaryObj ( model_obj )
    pRecord['train_data']['model']['model_checkpoint']       = model_obj_ready_for_net_transfer

    return pRecord


def ser_model__net_2_db( pRecord:dict  ) -> Union[ dict , Exception ]:
    """
    # **ser_model__net_2_db**

    Questa funzione permette di convertire il Modello di ML presente in un messaggio di rete in un formato adatto ad essere scritto su MongoDB.

    Args:\n
        pRecord             (dict)                  : record "di rete" contente il modello di ML

    Returns:\n
        Union[ dict , Exception ]

    Raises:\n
        Exception                                   : eccezione derivata dall'assenza del modello sul record passato dal chiamante
    """
    serializer:NetworkSerializer                             = NetworkSerializer()
    
    try:
        model_ck:str                                         = pRecord['train_data']['model']['model_checkpoint']
    except Exception as exp:
        return exp

    model_obj:object                                         = serializer.decodeBinaryObj ( model_ck )
    slob:bytes                                               = pickle.dumps(obj= model_obj)
    db_ready_object:Binary                                   = Binary(slob) 
    pRecord['train_data']['model']['model_checkpoint']       = db_ready_object

    return pRecord

        