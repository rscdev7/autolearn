"""
@author           	:  rscalia
@build-date         :  Thu 15/07/2021
@last_update        :  Fri 23/07/2021

Questo componente permette di testare il componente NetworkSerializer
"""

from ..lib.network_serializer.NetworkSerializer import NetworkSerializer
from typing                                     import Union

KEY_PATH:str        = "../data/"
READ_FROM_DISK:bool = True
DATA_TO_CYPHER:str  = "Test di cifratura Sim"
DATA:dict           = {"ciao":450 , "test":"test", "jhg":[4,5,8,7]}


def test_nt_ser():
    ns:NetworkSerializer = NetworkSerializer(KEY_PATH)

    #Prelievo chiave crittografica
    if (READ_FROM_DISK == False):
        res:Union[None, Exception] = ns.buildNewKey()
        assert issubclass (type(res) , Exception ) == False
    else:
        res:Union[None, Exception] = ns.readKeyFromFile()
        assert issubclass (type(res) , Exception ) == False


    res:Union[str, Exception]     = ns.encryptField(DATA_TO_CYPHER)
    assert issubclass (type(res) , Exception ) == False

    res:Union[str, Exception]     = ns.decryptField(res)
    assert issubclass (type(res) , Exception ) == False

    assert DATA_TO_CYPHER == res
    print ("\n[!] Dati decifrati: {}".format(res))


def test_json_encoding ():
    ns:NetworkSerializer = NetworkSerializer()

    encoded_data:bytes  = ns.encodeJson(DATA)
    decoded_data:dict   = ns.decodeJson(encoded_data)

    assert decoded_data == DATA
    print ("\n[!] Dati Decodificati: {}".format(decoded_data))

    