"""
@author           	:  rscalia              \n
@build-date         :  Sat 31/05/2021       \n
@last-update        :  Sat 31/05/2021       \n

Questa classe codifica una richiesta che permette di modificare i dati di sessione.
"""

from pydantic   import BaseModel, Field
from typing     import List,Optional,Dict


class SessionRequest (BaseModel):
    id_sess_cf:str                      = Field(...,title="Id Sessione Cifrato",description="Id Sessione Cifrato")