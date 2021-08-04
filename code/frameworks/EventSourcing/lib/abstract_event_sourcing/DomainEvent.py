"""
@author           	    :  rscalia                              \n
@build-date             :  Sun 25/07/2021                       \n
@last-update            :  Sun 25/07/2021                       \n

Questa classe mantiene le informazioni correlate al verificarsi di un evento nel sistema.
"""


class DomainEvent (object):

    def __init__(self, pEntityId:str , pEventTimeStamp:int , pEventPayload:dict) -> object:
        """
        Costruttore, permette di raccogliere le informazioni necessarie all'identificazione univoca dell'Evento.

        Args:\n
            pEntityId           (str)   : entità di dominio che ha subito l'evento
            pEventTimeStamp     (int)   : timestamp dell'evento
            pEventPayload       (dict)  : informazioni necessarie a identificare il cambiamento scaturito dall'evento \n
                                          Formato Dizionario: \n
                                            - "key": bytes
                                            - "value": 
                                                - dict { ...  "payload": _  ... }
                                            - "timestamp": int

        """
        self._entityId:str          = pEntityId
        self._eventTimeStamp:int    = pEventTimeStamp
        self._eventPayload:dict     = pEventPayload
        