"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Thu 15/07/2021

Questa classe serve per testare la classe HTTPEngine
"""

from ..lib.http_engine.HTTPEngine import HTTPEngine
import pytest
import json
import base64

TIME_OUT:int                    = 60

TEST_URL_GET:str                = "http://localhost:9200/get_param/"
Q_P:dict                        = {"param":5000}

TEST_URL_GET_NO_PARAM:str       = "http://localhost:9200/get_clean/"

TEST_URL_POST_JSON:str          = "http://localhost:9200/post"
PAYLOAD:dict                    = {"name":"ciao", "price":"820.50"}

TEST_URL_POST_BIN:str           = "http://localhost:9200/post_bin/"
BIN_DATA:bytes                  = b"test dati binari"

encoded:bytes                   = base64.b64encode(BIN_DATA)  
reencoded_data:str              = encoded.decode('ascii')

PAYLOAD_BIN:dict                = {'data':reencoded_data}


@pytest.mark.asyncio
async def test__async():

    print ("\n\n<<<<<<<<<<<<<<< TEST ASYNC >>>>>>>>>>>\n")

    #Creo oggetto HTTPEngine
    asyncEngine:HTTPEngine       = HTTPEngine(TIME_OUT)

    #SetUp componente Async
    asyncEngine.startAsync()


    #Test risposta GET con Parametri nell'URL
    res:dict    = await asyncEngine.getAsync(TEST_URL_GET,Q_P)
    print ("[!] GET con Parametri Query \n-> URL: {} \n-> Param: {}\n-> Response: {}\n".format(TEST_URL_GET, Q_P, res))


    #Test risposta GET senza Parametri nell'URL
    res:dict    = await asyncEngine.getAsync(TEST_URL_GET_NO_PARAM)
    print ("[!] GET senza Parametri nell'URL \n-> URL: {} \n-> Response: {}\n".format(TEST_URL_GET_NO_PARAM, res))


    #Test risposta POST con parametro JSON
    res:dict    = await asyncEngine.postAsync(TEST_URL_POST_JSON , PAYLOAD)
    print ("[!] POST JSON\n-> URL: {} \n-> Payload: {} \n-> Response: {}\n".format(TEST_URL_POST_JSON, PAYLOAD, res))


    #Test risposta POST con parametro BINARY
    res:dict    = await asyncEngine.postAsync(TEST_URL_POST_BIN , PAYLOAD_BIN)
    res:bytes   = base64.b64decode(res['payload']['data'])
    print ("[!] POST BINARY\n-> URL: {} \n-> Payload: {} \n-> Response: {}\n".format(TEST_URL_POST_BIN, PAYLOAD_BIN, res))


    #Chiusura Session
    await asyncEngine.closeAsync()    

def test_sync():

    print ("\n\n<<<<<<<<<<<<<<< TEST SYNC >>>>>>>>>>>\n")

    #Creo oggetto HTTPEngine
    engine:HTTPEngine       = HTTPEngine(TIME_OUT)


    #Test risposta GET con Parametri nell'URL
    res:dict    = engine.get(TEST_URL_GET, Q_P)
    print ("[!] GET con Parametri Query \n-> URL: {} \n-> Param: {}\n-> Response: {}\n".format(TEST_URL_GET, Q_P, res))


    #Test risposta GET senza Parametri nell'URL
    res:dict    = engine.get(TEST_URL_GET_NO_PARAM)
    print ("[!] GET senza Parametri nell'URL \n-> URL: {} \n-> Response: {}\n".format(TEST_URL_GET_NO_PARAM, res))


    #Test risposta POST con parametro JSON
    res:dict    = engine.post(TEST_URL_POST_JSON , PAYLOAD)
    print ("[!] POST JSON\n-> URL: {} \n-> Payload: {} \n-> Response: {}\n".format(TEST_URL_POST_JSON, PAYLOAD, res))


    #Test risposta POST con parametro BINARY
    res:dict    = engine.post(TEST_URL_POST_BIN , PAYLOAD_BIN)
    res:bytes   = base64.b64decode(res['payload']['data'])
    print ("[!] POST BINARY\n-> URL: {} \n-> Payload: {} \n-> Response: {}\n".format(TEST_URL_POST_BIN, PAYLOAD_BIN, res))