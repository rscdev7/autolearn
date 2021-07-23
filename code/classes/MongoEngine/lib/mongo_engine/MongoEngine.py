"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 23/07/2021

Questo componente serve per leggere, scrivere su un DB Mongo
"""

import motor.motor_asyncio
import asyncio
import os
import pprint
from motor.motor_asyncio    import AsyncIOMotorDatabase
from pymongo.results        import InsertManyResult,UpdateResult

from typing                 import List,Union
import pickle
from bson.binary            import Binary
from bson.objectid          import ObjectId


class MongoEngine (object):


    def __init__ (self, pHostName:str , pPort:int , pUsername:str, pPassword:str, pDBName:str , pCollectionName:str) -> object:
        """
        Costruttore\n

        Args:\n
            pHostName               (str)       : nome dell'host su cui risiede il DB
            pPort                   (int)       : porta su cui gira il processo del DB
            pUsername               (str)       : Nome Utente
            pPassword               (str)       : Password Utente     
            pDBName                 (str)       : nome del DB a cui si vuole accedere
            pCollectionName         (str)       : nome della collezione del DB a cui si vuole accedere       
        """

        self._host:str                  = pHostName
        self._port:int                  = pPort
        self._username:str              = pUsername
        self._password:str              = pPassword
        self._dbName:str                = pDBName
        self._collectionName:str        = pCollectionName

        self._db:AsyncIOMotorDatabase   = None
        self._connection                = None


    def start (self) -> Union [None , Exception]:
        """
        Questo metodo avvia la connessione col DB

        Returns:\n
            Union [None , Exception]

        Raises:\n
            Exception   : eccezione generica
        """
        try:
            self._connection:AsyncIOMotorClient                 = motor.motor_asyncio.AsyncIOMotorClient(host=self._host, port=self._port , username=self._username, password=self._password)

            self._db:AsyncIOMotorDatabase                       = self._connection[self._dbName]
        except Exception as msg:
            return msg


    def stop (self) -> Union [None , Exception]:
        """
        Questo metodo stoppa la connessione col DB

        Returns:\n
            Union [None , Exception]

        Raises:\n
            Exception   : eccezione _collectionNamegenerica
        """
        try:
            self._connection.close()
            self._db:AsyncIOMotorDatabase           = None
        except Exception as msg:
            return msg  


    async def push (self, pDocs:List[dict]) -> Union [ List[ObjectId] , Exception ]:
        """
        Inserisce una lista di documenti nella collezione del DB selezionata

        Args:\n
            pDocs           (List[dict])                : lista di record da inserire

        Returns:\n       
            Union [ List[ObjectId] , Exception ]        : token inserimento o eccezione

        Raises:\n
                Exception                               : eccezione generica
        """

        try:
            result:InsertManyResult          = await self._db[self._collectionName].insert_many( pDocs )
        except Exception as msg:
            return msg
        
        return result.inserted_ids


    async def pushBinary (self, pDocs:List[dict], pFieldsToBinary:List[list]) -> Union [ List[ObjectId] , Exception ]:
        """
        Inserisce una lista di documenti nella collezione del DB selezionata.\n

        Inoltre, converto in binario i campi dei record inseriti in pFieldsToBinary.

        Args:\n
            pDocs           (List[dict])                : lista di record da inserire
            pFieldsToBinary (List[list])                : per ogni record, indica i campi da trasformare in bianrio

        Returns:\n        
            Union [ List[ObjectId] , Exception ]        : token inserimento o eccezione

        Raises:\n
                Exception                               : eccezione generica
        """

        #Binarize some data in the records 
        computed_data:dict                  = pDocs.copy()
        for doc, to_binary  in zip( computed_data , pFieldsToBinary ):
            for field in to_binary:
                binary_data:bytes           = pickle.dumps(obj= doc[field]) 
                doc[field]                  = Binary(binary_data)


        #Insert computed records on the DB
        try:
            result:InsertManyResult         = await self._db[self._collectionName].insert_many( computed_data )
        except Exception as msg:
            return msg
        
        return result.inserted_ids


    async def queryOnesBinary (self, pBinaryFields:List[list], pQuery:dict , pProjection:dict=None) -> Union [ dict , Exception ]:
        """
        Questo metodo restituisce il primo documento che fa match con la query.

        Args:\n
            pFieldsToBinary (List[list])                : indica i campi da trasformare da binario al tipo originario del dato
            pQuery          (dict)                      : query
            pProjection     (dict | DEF = None)         : proiezione sulla query

        Returns:\n
            Union [ dict , Exception  ]                 : dizionario con i dati recuperati o Eccezione

        Raises:\n
            Exception                                   : eccezione generica

        """
        try:
            document:dict           = await self._db[self._collectionName].find_one( pQuery , pProjection )

            #Trasformo i campi binari nel loro formato originario
            for ls_fields in pBinaryFields:
                for field in ls_fields:
                    document[field] = pickle.loads( document[field] )

            return document
        except Exception as msg:
            return msg


    async def queryOnes (self, pQuery:dict , pProjection:dict=None) -> Union [ dict , Exception, None ]:
        """
        Questo metodo restituisce il primo documento che fa match con la query.

        Args:\n
            pQuery          (dict)                          : query
            pProjection     (dict | DEF = None)             : proiezione sulla query

        Returns:\n
            Union [ dict , Exception, None  ]               : dizionario con i dati recuperati o Eccezione

        Raises:\n
            Exception                                       : eccezione generica

        """
        try:
            document:dict          = await self._db[self._collectionName].find_one( pQuery , pProjection )
            return document
        except Exception as msg:
            return msg


    async def query (self, pQuery:dict, pProjection:dict=None) -> Union [ List[dict] , Exception ]:
        """
        Questo metodo restituisce il primo documento che fa match con la query.

        Args:\n
            pQuery          (dict)                  : query
            pProjection     (dict | DEF = None)     : proiezione sulla query

        Returns:\n
            Union [ List[dict] , Exception ]        : Lista di dizionari con i dati recuperati o eccezione. \n
                                                      Restituisce "[]" quand la query non ha trovat risultati

        Raises:\n
            Exception                               : eccezione generica

        """
        try:
            cursor:AsyncIOMotorCursor                   = self._db[self._collectionName].find(pQuery , pProjection)
            retrieved_data:List[dict]                   = []

            async for document in cursor:
                retrieved_data.append ( document )
        except Exception as msg:
            return msg

        return retrieved_data


    async def count (self, pQuery:dict={}) -> Union [ int, Exception ]:
        """
        Conta il numero di occorrenze che soddisfano una Query

        Args:\n
            pQuery          (dict | DEF = {})       : query  

        Returns:\n
            Union [ int, Exception ]                : Numero record che fanno match con la query passata come parametro

        Raises:\n
            Exception                               : eccezione generica
        """
        try:
            n:int           = await self._db[self._collectionName].count_documents(pQuery)
        except Exception as msg:
            return msg

        return n


    async def update (self, pQuery:dict , pUpdate:dict) -> Union [ UpdateResult , Exception ]:
        """
        Questo metodo aggiorna tutti i record del DB che fanno match con la query.

        Args:\n
            pQuery          (dict)              : query di ricerca
            pUpdate         (dict)              : aggiornamenti dizionario

        Returns:\n
            Union [ UpdateResult , Exception ]  : sommario aggiornamento record

        Raises:\n
            Exception                           : eccezione generica
        """
        try:
            res:UpdateResult        = await self._db[self._collectionName].update_many( pQuery , pUpdate)
            return res
        except Exception as msg:
            return msg