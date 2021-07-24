"""
@author           	:  rscalia
@build-date         :  Fri 16/07/2021
@last-update        :  Fri 23/07/2021

Questo componente serve per testare MongoEngine
"""

import pytest
import asyncio
from typing                         import List, Union
from bson.objectid                  import ObjectId

from ..lib.mongo_engine.MongoEngine import MongoEngine

from sklearn.linear_model           import LogisticRegression
from sklearn.datasets               import load_iris


HOST_NAME:str               = "mongo"
PORT:int                    =  27017
USERNAME:str                = "root"
PASSWORD:str                = "example"
DB_NAME:str                 = "Test"
COLLECTION_NAME:str         = "Collection"


DOC_MANY                    = [ {'Int':50,"ts":"link"} , {"oid":50} ]
QUERY:dict                  = { 'Int' : { '$lt':100 }  }
QUERY_MUL:dict              = { "$or": [ {'Int' : { '$lt':100 } } , {'oid' : { '$lt':100 } } ]  }
PROJECTION:dict             = {"Int":1 , "oid":1 }

QUERY_UPDATE:dict           = { 'Int': { '$lt':100 } }
UPDATE:dict                 = { "$set" : { 'Float':150.80, 'string':"ciao" } }


QUERY_BIN:dict              = {'_id':402}

#Load Data, LogisticRegressor, training and evaluation
X, Y                        = load_iris(return_X_y=True)
clf:LogisticRegression      = LogisticRegression(random_state=0, max_iter=500)

BIN_DOCS:dict               = [ {'_id':402 , 'obj':clf} ]
TO_BIN:list                 = [ ["obj"]  ]



@pytest.mark.asyncio
async def test_mongo():

    #Connessione a MongoDB
    engine:MongoEngine                                          = MongoEngine(HOST_NAME, PORT, USERNAME , PASSWORD, DB_NAME , COLLECTION_NAME)
    res:Union[ None, Exception ]                                = engine.start()
    assert issubclass (type(res) , Exception) == False


    #A scopo di Test cancello tutti i doc della collezione
    await engine._db[COLLECTION_NAME].delete_many({})


    #Scrittura di un Record
    insertion_ids:Union[ List[ObjectId] , Exception ]           = await engine.push(DOC_MANY)
    assert issubclass (type(insertion_ids) , Exception) == False
    print ("\n\n[!] Id Inserimenti: {}".format(insertion_ids))


    #Query FIFO
    res:Union[dict, Exception, None]                            = await engine.queryOnes(QUERY,PROJECTION)
    assert issubclass (type(res) , Exception) == False

    if (type(res) == None):
        print ("\n[!] La query non ha prodotto alcun risultato")
    else:
        print("\n[!] Query FIFO:\n\n {}\n".format(res))


    #Query
    res:Union[List[dict], Exception]                            = await engine.query(QUERY_MUL,PROJECTION)
    assert issubclass (type(res) , Exception) == False

    if (res == []):
        print ("[!] La query non ha prodotto alcun risultato")
    else:
        print("\n[!] Query Multipla:\n\n {}\n".format(res))


    #Count
    res:Union[int, Exception]                                   = await engine.count(QUERY)
    assert issubclass (type(res) , Exception) == False
    print ("\n[!] Il numero di Documenti che soddifano la query è: {}".format(res))


    #Aggiornamento
    res:Union[UpdateResult, Exception]                          = await engine.update(QUERY_UPDATE, UPDATE)
    assert issubclass (type(res) , Exception) == False
    print ("\n[!] Aggiornamento Effettuato con Successo : {}".format(res))



    #Test inserimento oggeto serializzato in binario sul DB
    clf.fit(X,Y)
    score_prec:float                                            = clf.score(X, Y)
    print ("\n<PRE> [OBJ] => {} - [SCORE] => {}".format(clf,score_prec))
    
    #Binary Insert
    insertion_ids:Union[List[ObjectId], Exception]              = await engine.pushBinary(BIN_DOCS,TO_BIN)
    assert issubclass (type(insertion_ids) , Exception) == False
    print ("\n[!] Id Inserimenti: {}".format(insertion_ids))


    #Binary Retrieve
    result:Union[dict, Exception]                               = await engine.queryOnesBinary(TO_BIN,QUERY_BIN)
    assert issubclass (type(result) , Exception) == False
    print ("\n[!] Oggetto Ripristinato: {}".format( result['obj'] ) )

    score_current:float                                         = result['obj'].score(X, Y)
    assert score_prec == score_current
    print ("\n<PRE> [OBJ] => {} - [SCORE] => {}".format(score_prec,score_current))


    #Stop Connessione
    res:Union[None , Exception]                                 = engine.stop()
    assert issubclass (type(res) , Exception) == False