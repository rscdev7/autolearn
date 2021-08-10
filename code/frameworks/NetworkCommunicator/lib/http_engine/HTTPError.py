"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 15/07/2021

Questa classe permette di lanciare un'eccezzione quando il server restituisce un codice d'errore.
"""

class HTTPError (Exception):
    pass