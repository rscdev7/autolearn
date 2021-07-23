"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Fri 23/07/2021

Questa classe serve per gestire le chiamate HTTP Sincrone e Asincrone
"""

import asyncio
import aiohttp
from aiohttp                                import ClientSession, ClientTimeout, ClientError, ClientPayloadError , InvalidURL, ClientResponseError, ClientResponseError

import json

import requests
from requests.adapters                      import HTTPAdapter
from requests.packages.urllib3.util.retry   import Retry
from requests.models                        import Response

from typing                                 import Dict, Union, Tuple

from .HTTPError                             import HTTPError


class HTTPEngine (object):

    def __init__(self, pSecTimeOut:int) -> object:
        """
        Costruttore\n

        Args:\n
            pSecTimeOut         (int)       : timeout per le richieste HTTP in secondi
        """
        self._timeOut:int                           = pSecTimeOut
        self._asyncSession:ClientSession            = None


    def startAsync(self) -> None:
        """
        Questo metodo avvia una sessione HTTP Asincrona
        """
        timeout:ClientTimeout                       = ClientTimeout(total=self._timeOut)
        self._asyncSession:ClientSession            = ClientSession(timeout=timeout)


    async def closeAsync (self) -> Union[ None , Exception]:
        """
        Questo metodo chiude una sessione HTTP Asincrona

        Raises:\n
            "Exception"     : eccezione generica, molto probabilmente causata da una sessione già chiusa.
        """
        try:
            await self._asyncSession.close()
        except Exception as exp:
            return exp


    def get (self, pURL:str , pParams:dict={}) -> Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]:
        """
        Questo metodo effettua una get Sincrona.\n

        Args:\n
                pURL            (str)                                                                       : URL su cui fare la chiamata 
                pParams         (dict | DEF = {} )                                                          : eventuali parametri di query da aggiugere all'URL http
        
        Returns:\n
                                (Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ])              : dizionario contenente status_code e payload restituiti dal server \n
                                
                                Formato Dizionario:\n
                                    - **status_code**, status code della chiamata HTTP \n
                                    - **payload**, dati restituiti dal server\n

        Raises:\n
            "HTTPError"     : errore HTTP con codice da 400 a 499 \n
            "RuntimeError"  : errore generico a Runtime
            "Exception"     : errore generico
        """

        try:
            r:Response      = requests.get(pURL, params=pParams)
            status_code:int = r.status_code
            response:dict   = r.json()

            if (status_code >= 400 and status_code <= 499):
                raise HTTPError("HTTP Error {}".format(status_code))

            return { "status_code": status_code , "payload": response }

        except HTTPError as err:
            return (err, status_code)

        except RuntimeError as rte:
            return rte

        except Exception as ex:
            return ex


    async def getAsync(self, pURL:str, pParams:dict={}) -> Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]:
        """
        Questo metodo effettua una get asincrona.\n

        Args:\n
                pURL            (str)                                                                       : URL su cui fare la chiamata 
                pParams         (dict | DEF = {})                                                           : eventuali parametri di query da aggiugere all'URL http
        
        Returns:\n
                                (Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ])              : dizionario contenente status_code e payload restituiti dal server \n
                                
                                Formato Dizionario:\n
                                    - **status_code**, status code della chiamata HTTP \n
                                    - **payload**, dati restituiti dal server\n

        Raises:\n
            "HTTPError"             : errore HTTP con codice da 400 a 499 \n
            "InvalidURL"            : URL mal formato, ad esempio manca l'host \n
            "ClientPayloadError"    : il client ha inviato al server dei dati mal formati \n
            "ClientError"           : errore generico al livello di API HTTP \n
            "RuntimeError"          : errore generico a runtime
            "Exception"             : errore generico
        """
        try:
            async with self._asyncSession.get(url=pURL , params=pParams) as resp:
                status_code:int     = resp.status
                response:dict       = await resp.json()

                if (status_code >= 400 and status_code <= 499):
                    raise HTTPError("HTTP Error {}".format(status_code))

                return { "status_code": status_code , "payload": response }
                
        except HTTPError as err:
            return (err, status_code)

        except InvalidURL as iurl:
            return iurl

        except ClientPayloadError as cpe:
            return cpe

        except ClientResponseError as cl:
            return cl

        except ClientError as cle:
            return cle

        except RuntimeError as rte:
            return rte

        except Exception as ex:
            return ex


    def post (self, pUrl:str , pPayload:dict) -> Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]:
        """
        Questo metodo effettua una post Sincrona.\n

        Args:\n
                pURL            (str)                                                                   : URL su cui fare la chiamata \n
                pPayload        (dict)                                                                  : payload da inoltrare al server\n
        
        Returns:\n
                                (Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ])          : dizionario contenente status_code e payload restituiti dal server \n
                                
                                Formato Dizionario:\n
                                    - **status_code**, status code della chiamata HTTP \n
                                    - **payload**, dati restituiti dal server\n

        Raises:\n
            "HTTPError"     : errore HTTP con codice da 400 a 499 \n
            "RuntimeError"  : errore generico a runtime
            "Exception"     : errore generico
        """
        try:
            r:Response      = requests.post(pUrl, data= json.dumps(pPayload , default=lambda o: o.__dict__, indent=2) )
            status_code:int = r.status_code
            response:dict   = r.json()

            if (status_code >= 400 and status_code <= 499):
                raise HTTPError("HTTP Error {}".format(status_code))

            return { "status_code": status_code , "payload": response }

        except HTTPError as err:
            return (err, status_code)

        except RuntimeError as rte:
            return rte

        except Exception as ex:
            return ex


    async def postAsync(self, pUrl:str , pPayload:dict) -> Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ]:
        """
        Questo metodo effettua una post asincrona.\n

        Args:\n
                pURL            (str)                                                                   : URL su cui fare la chiamata \n
                pPayload        (dict)                                                                  : payload da inoltrare al server\n
        
        Returns:\n
                                (Union[ Dict[int,dict] , Exception, Tuple [Exception , int] ])          : dizionario contenente status_code e payload restituiti dal server \n
                                
                                Formato Dizionario:\n
                                    - **status_code**, status code della chiamata HTTP \n
                                    - **payload**, dati restituiti dal server\n

        Raises:\n
            "HTTPError"             : errore HTTP con codice da 400 a 499 \n
            "InvalidURL"            : URL mal formato, ad esempio manca l'host \n
            "ClientPayloadError"    : il client ha inviato al server dei dati mal formati \n
            "ClientError"           : errore generico al livello di API HTTP \n
            "RuntimeError"          : errore generico a runtime
            "Exception"             : errore generico
        """
        try:

            resp:_RequestContextManager = await self._asyncSession.post(pUrl, json=pPayload)
            
            status_code:int = resp.status
            response:str    = await resp.json()

            if (status_code >= 400 and status_code <= 499):
                    raise HTTPError("HTTP Error {}".format(status_code))

            return { "status_code": status_code , "payload": response }

        except HTTPError as err:
            return (err, status_code)

        except InvalidURL as iurl:
            return iurl

        except ClientPayloadError as cpe:
            return cpe

        except ClientResponseError as cl:
            return cl

        except ClientError as cle:
            return cle

        except RuntimeError as rte:
            return rte

        except Exception as ex:
            return ex